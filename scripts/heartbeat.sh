#!/usr/bin/env bash
# bmad-loop heartbeat — token-free run monitor.
#
# Watches the active bmad-loop run and alerts (desktop notification + terminal
# bell + audible chime on macOS) on the three things worth interrupting for:
#   1. Dialog stall   — a spawned session waiting on a prompt it can't answer.
#   2. Engine death   — the engine process gone / crashed / stopped.
#   3. Phase change   — dev -> review -> done, and finished / paused.
#
# Costs nothing to run. Leave it in a spare tmux pane, or tail the log:
#   tail -f "$(dirname "$0")/heartbeat.log"
#
# Usage:  bash scripts/heartbeat.sh [interval_seconds] [run_id]   (interval default 30)
#   run_id is optional — pin a specific run so an auto-clean-on-finish race
#   (bmad-loop deletes the run dir the instant it finishes) is read as a clean
#   finish, not "no run found". Without it, the newest run dir is used.
#
# PROJECT is auto-detected as the parent of this script's directory (so this
# script is expected to live at <project>/scripts/heartbeat.sh). Override with
# the BMAD_LOOP_PROJECT env var if you keep it elsewhere.

set -uo pipefail

PROJECT="${BMAD_LOOP_PROJECT:-$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)}"
INTERVAL="${1:-30}"
PIN_RUN="${2:-}"
LOG="$(dirname "${BASH_SOURCE[0]:-$0}")/heartbeat.log"   # gitignore this (scripts/*.log)

STALL_TICKS=5   # identical-pane ticks before we call it a possible hang.

log()  { printf '%s  %s\n' "$(date '+%H:%M:%S')" "$*" | tee -a "$LOG"; }
alert() {
  # $1 = short title, $2 = body. Loud: bell + chime + macOS banner (best-effort).
  printf '\a' >&2
  osascript -e "display notification \"$2\" with title \"bmad heartbeat: $1\" sound name \"Glass\"" >/dev/null 2>&1
  afplay /System/Library/Sounds/Glass.aiff >/dev/null 2>&1 &
  log "🔔 ALERT [$1] $2"
}

if [ -n "$PIN_RUN" ]; then
  RUN_DIR="$PROJECT/.bmad-loop/runs/$PIN_RUN"
else
  RUN_DIR="$(ls -1dt "$PROJECT"/.bmad-loop/runs/*/ 2>/dev/null | head -1)"
fi
if [ -z "$RUN_DIR" ] || [ ! -d "$RUN_DIR" ]; then
  echo "No run under $PROJECT/.bmad-loop/runs/. Nothing to watch." >&2
  exit 1
fi
RUN_DIR="${RUN_DIR%/}"
STATE="$RUN_DIR/state.json"
PIDFILE="$RUN_DIR/engine.pid"
RUN_ID="$(basename "$RUN_DIR")"

START_HEAD="$(git -C "$PROJECT" rev-parse HEAD 2>/dev/null || echo unknown)"
START_BRANCH="$(git -C "$PROJECT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
SESS="$(tmux ls -F '#{session_name}' 2>/dev/null | grep -E '^bmad-loop-[0-9]' | head -1)"

read_json() { # $1 = key: finished|stopped|crashed|paused_reason|phase|tokens
  python3 - "$STATE" "$1" <<'PY' 2>/dev/null
import json,sys
try: d=json.load(open(sys.argv[1]))
except Exception: print(""); sys.exit()
key=sys.argv[2]
if key=="phase":
    t=d.get("tasks") or {}; v=next(iter(t.values()),{}).get("phase","") if t else ""
elif key=="tokens":
    t=d.get("tasks") or {}; tk=next(iter(t.values()),{}).get("tokens",{}) if t else {}
    v=f"in {tk.get('input_tokens',0)} out {tk.get('output_tokens',0)} cache {tk.get('cache_read_tokens',0)}"
else: v=d.get(key,"")
print("" if v is None else v)
PY
}

engine_alive() { local pid; pid="$(cat "$PIDFILE" 2>/dev/null)"; [ -n "$pid" ] && ps -p "$pid" >/dev/null 2>&1; }
pane_tail() { [ -n "$SESS" ] || return 0; tmux capture-pane -t "$SESS" -p 2>/dev/null | tail -30; }
looks_like_prompt() { grep -qE '(Do you want to (proceed|trust)|❯ +1\.|1\. +Yes.*|Press Enter to|Yes, I accept|awaiting your (input|response))' <<<"$1"; }

log "▶ watching run $RUN_ID  (interval ${INTERVAL}s, session ${SESS:-none})"
prev_phase=""; prev_hash=""; same_count=0

while true; do
  if [ ! -d "$RUN_DIR" ]; then
    now_head="$(git -C "$PROJECT" rev-parse HEAD 2>/dev/null || echo unknown)"
    if [ "$now_head" != "$START_HEAD" ]; then
      alert "FINISHED (auto-cleaned)" "run $RUN_ID dir gone; $START_BRANCH advanced $START_HEAD→$now_head — verify merge-back"
    else
      alert "RUN DIR GONE" "run $RUN_ID dir removed but $START_BRANCH HEAD unchanged — check for a paused/failed finish before trusting"
    fi
    exit 0
  fi

  finished="$(read_json finished)"; stopped="$(read_json stopped)"; crashed="$(read_json crashed)"
  paused="$(read_json paused_reason)"; phase="$(read_json phase)"; toks="$(read_json tokens)"

  if [ -n "$phase" ] && [ "$phase" != "$prev_phase" ]; then
    [ -n "$prev_phase" ] && alert "phase" "$prev_phase → $phase  ($toks)"
    log "phase=$phase  $toks"; prev_phase="$phase"
  fi

  if [ "$crashed" = "True" ]; then alert "CRASHED" "engine reported crash — see $RUN_DIR"; exit 2; fi
  if [ "$finished" = "True" ]; then alert "FINISHED" "run $RUN_ID finished — verify merge-back"; exit 0; fi
  if [ "$stopped" = "True" ]; then alert "STOPPED" "run $RUN_ID stopped"; exit 0; fi
  if [ -n "$paused" ] && [ "$paused" != "None" ]; then alert "PAUSED" "reason: $paused — check pane before acting (do NOT git reset)"; fi

  if ! engine_alive; then alert "ENGINE GONE" "engine.pid not running and state not terminal — likely died"; exit 3; fi

  pane="$(pane_tail)"
  if [ -n "$pane" ]; then
    h="$(printf '%s' "$pane" | cksum | awk '{print $1}')"
    if [ "$h" = "$prev_hash" ]; then same_count=$((same_count+1)); else same_count=0; prev_hash="$h"; fi
    if [ "$same_count" -ge "$STALL_TICKS" ]; then
      if looks_like_prompt "$pane"; then
        alert "DIALOG STALL" "pane shows a prompt & unchanged ${same_count} ticks — session waiting for input"
      else
        alert "POSSIBLE HANG" "pane unchanged ${same_count} ticks (~$((same_count*INTERVAL/60))m) — check it"
      fi
      same_count=0
    fi
  fi

  sleep "$INTERVAL"
done
