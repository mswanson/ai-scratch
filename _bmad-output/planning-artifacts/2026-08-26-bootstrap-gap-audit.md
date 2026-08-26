# Bootstrap Gap Audit

**The bar:** install Xcode CLI tools, clone dotfiles, run `make bootstrap`, log
into accounts, start working. Audited 2026-08-26 against what is actually
configured on this machine.

Six gaps. One of them explains the iTerm theme file you half-remembered, and it
turns out to be a pattern rather than a one-off.

---

## 1. Three apps keep their settings outside the repo

`~/Documents/App Settings/` holds the real configuration for three apps, none of
it tracked:

| App | What is there | How the app finds it |
|---|---|---|
| **iTerm2** | `com.googlecode.iterm2.plist`, 17.6 KB, 89 keys | `PrefsCustomFolder` = that path, `LoadPrefsFromCustomFolder` = 1 |
| **Alfred** | `Alfred.alfredpreferences`, 1.9 MB | Alfred's sync folder setting |
| **Rectangle Pro** | `RectangleProConfig.json`, 10 KB | its own config directory |

**This is the file you were thinking of.** iTerm is not reading its settings
from `~/Library/Preferences` at all; it is loading them from Documents. That is
also why `setup-iterm.sh` only sets a font and scrollback and then tells you to
pick the colour preset by hand: the script is poking at a plist the app has
already been told to ignore.

On a fresh machine all three apps come up with defaults, and nothing in the
bootstrap says otherwise.

**Fix:** move the folder into the repo (`config/app-settings/`), dotbot-link it
back to where each app expects it, and set the three "load from here" keys
during bootstrap. iTerm then arrives with the theme, font, keybindings and
profile already applied, and the manual preset selection goes away entirely.

**Note before moving:** Rectangle Pro also has `iCloudSync = 1`, with a last
sync in 2023. Worth deciding which source wins before pointing it somewhere new.

---

## 2. Two scripts exist but bootstrap never calls them

| Script | Make target | Consequence of skipping it |
|---|---|---|
| `setup-iterm.sh` | `make iterm` | iTerm keeps stock font and colours |
| `set-default-shell.sh` | `make shell` | **login shell stays `/bin/zsh`**, not the Homebrew zsh the config targets |

The second matters more than it looks. `symlinked/zshenv.sh` hardens `fpath`
against Homebrew's versioned zsh paths, and `Brewfile.cli` declares `zsh`
precisely so the login shell is the modern one. Bootstrap installs it and never
switches to it.

`set-default-shell.sh` needs `sudo` and runs `chsh`, which is why it was left
out. That is a reason to run it last with a clear prompt, not a reason to omit
it from a workflow whose whole point is one command.

---

## 3. Chrome apps are all manual

Six on this machine, each a separate Chrome profile install:

`Gmail | Personal`, `Calendar | Personal`, `Coda | Personal`, `Miro | Forge512`,
`YNAB`, `Hotutils`

`Brewfile.apps` lists them in a comment and says "set up by hand today". These
are the "calendar/gmail apps" from your bar, and they are exactly what is not
covered.

**The honest constraint:** Chrome apps are per-profile and profiles are created
by signing in, so this cannot be fully automated ahead of the account logins.
What *can* be scripted is creating them once the profiles exist, since a Chrome
app is a shortcut with a known URL and profile directory. That is the
`setup-chrome-profiles.sh` note already sitting in the plan's parking lot.

---

## 4. VS Code config is untracked

`settings.json` is 6 KB and **53 extensions** are installed. Neither is in the
repo, and `code --install-extension` from a tracked list is a solved problem
(the README's old TODO list had this item before it was removed).

VS Code has built-in Settings Sync, which is the other answer. Either is fine;
neither is happening now.

---

## 5. Nothing installs the Claude Code CLI

`claude` lives at `~/.local/share/claude/versions/2.1.246`, symlinked into
`~/.local/bin`. It is not a brew formula, not an npm global, and not in any list
here. `cask "claude"` in `Brewfile.apps` is the **desktop app**, which is a
different thing.

This is load-bearing: `setup-mcp-servers.sh` gates on `claude` being on PATH, so
on a fresh machine step 12 skips and no MCP server gets registered. That is not
theoretical — it is what the test account did.

---

## 6. Dock layout, and the settings that need export rather than write

Already recorded in `setup-macos-defaults.sh` as export-only, and unchanged:
`com.apple.dock persistent-apps` is an array of binary bookmarks. Keyboard
shortcuts are handled (`config/macos/symbolichotkeys.plist`); the Dock is not.

Low value compared to the five above. Rebuilding a Dock takes two minutes.

---

## What bootstrap already covers, so it is not re-litigated

Xcode CLI tools, Homebrew, all 53 formulae and 37 casks, symlinks, **SSH key and
commit signing** (added 2026-08-26), asdf plus both runtimes, npm/python/uv
globals, agent skills, MCP registration, the LiteLLM scaffold and the qmd index.
macOS defaults and keyboard shortcuts run as an optional prompted step.

---

## Suggested order

1. **App settings into the repo** — biggest gap, and it removes a manual step
   from every fresh machine. Also the one you noticed.
2. **`set-default-shell.sh` and `setup-iterm.sh` into bootstrap** — small, and
   they close the "one workflow" promise.
3. **Claude Code CLI** — small, and it unblocks the MCP step.
4. **VS Code settings and extensions** — medium.
5. **Chrome apps** — needs the account-login step to happen first by nature.
6. **Dock** — optional.

Items 1-3 are an hour and get you most of the way to the stated bar.
