# Moving SSH Keys into 1Password

Move the SSH key off the laptop's disk and into 1Password's SSH agent, keeping GitHub access and signed commits working throughout. Do it in two stages: prove the plumbing with the existing key, then rotate to a fresh 1Password-generated key once the first stage is verified.

## Why this is worth doing

`~/.ssh/id_ed25519` currently has **no passphrase**. Anything that can read that file — a malicious npm postinstall, a compromised CLI, a backup that syncs the wrong directory, anyone with the unlocked laptop — gets a key that pushes to every repo and signs commits as you. A passphrase would help, but 1Password's agent is better: the private key never exists as a file, and every use needs Touch ID.

The current state, verified 2026-08-22:

| Thing | Value |
|---|---|
| Key | `~/.ssh/id_ed25519`, ED25519, `SHA256:c3qHF1vrDo7+1b7jwojonH6J/Ydnui6KofSvMCsKWLw`, no passphrase |
| `~/.ssh/config` | one entry: `Host github.com`, `AddKeysToAgent yes`, `IdentityFile ~/.ssh/id_ed25519` |
| Signing | `gpg.format = ssh`, `user.signingkey = ~/.ssh/id_ed25519.pub`, `commit.gpgsign = true`, `tag.gpgsign = true` |
| Allowed signers | `~/.ssh/allowed_signers`, one line, same key |
| 1Password | app installed, CLI 2.34.1, `op-ssh-sign` present at the standard path |
| Agent | not enabled — no `agent.sock`, no `IdentityAgent` in ssh config |

## The one thing that will bite you

Git commit signing does **not** go through the SSH agent. `gpg.format = ssh` makes git shell out to `ssh-keygen -Y sign`, which reads the private key from disk. Move the key into 1Password without also setting `gpg.ssh.program`, and signing breaks — and because `commit.gpgsign` and `tag.gpgsign` are both `true`, **every commit fails**, not just pushes.

So the signing switch and the key move have to land together, and the key file stays on disk until both are verified.

## Stage 1 — Same key, new home

Nothing is deleted in this stage. The key file stays exactly where it is, so rollback is "undo the config change".

### 1. Enable the agent

In 1Password: **Settings → Developer → Set Up SSH Agent**. Verify:

```bash
ls -l ~/Library/Group\ Containers/2BUA8C4S2C.com.1password/t/agent.sock
```

### 2. Import the existing key

In 1Password, create an SSH Key item and import `~/.ssh/id_ed25519`. Confirm 1Password reports the same fingerprint (`SHA256:c3qHF1...`) — if it differs, stop, because GitHub and `allowed_signers` both trust that exact key.

```bash
SSH_AUTH_SOCK=~/Library/Group\ Containers/2BUA8C4S2C.com.1password/t/agent.sock ssh-add -l
```

The fingerprint must appear in that list.

### 3. Point ssh at the agent

Edit `~/.ssh/config`. Note this file is **not** currently tracked in dotfiles — decide separately whether it should be (see Open questions).

```
Host *
  IdentityAgent "~/Library/Group Containers/2BUA8C4S2C.com.1password/t/agent.sock"

Host github.com
  IdentityFile ~/.ssh/id_ed25519.pub
```

Two deliberate changes: `IdentityFile` now points at the **public** key, which is how you tell ssh which agent identity to offer, and `AddKeysToAgent yes` goes, since it only applies to on-disk keys.

Verify without touching a repo:

```bash
ssh -T git@github.com
```

Expect the GitHub greeting and a 1Password approval prompt.

### 4. Switch signing to 1Password

In `symlinked/gitconfig.sh`, under the existing `[gpg "ssh"]` block:

```
[gpg "ssh"]
    program = /Applications/1Password.app/Contents/MacOS/op-ssh-sign
    allowedSignersFile = /Users/michaelswanson/.ssh/allowed_signers
```

`user.signingkey` and `allowed_signers` stay as they are: same key, same public half.

Verify on a throwaway commit, not real work:

```bash
cd $(mktemp -d) && git init -q . && echo x > a && git add a
git commit -qm "signing test"
git log --show-signature -1
```

Expect `Good "git" signature` and a 1Password prompt. If it fails, revert the `program` line and signing works again immediately.

### 5. Live for a few days

Push, pull, and commit normally. What to watch for: anything that runs without you present — a cron job, a git hook, a CI runner on this machine, `bmad-loop` sessions that commit unattended. Those cannot answer a Touch ID prompt.

## Stage 2 — Remove the key from disk

Only after Stage 1 has been quiet for several days.

1. Back up the key into 1Password as a secure note first, then `trash ~/.ssh/id_ed25519` — keep the `.pub`, since ssh config and `user.signingkey` reference it.
2. Re-run the Stage 1 verifications, all of them.
3. Confirm no leftover copies: `ls ~/.ssh/`, and check `~/.ssh/agent/`, which exists and should be inspected before assuming it is empty.

## Stage 3 — Rotate (optional, recommended later)

The imported key spent its life unprotected on disk. Once the plumbing is proven, generate a **new** key inside 1Password (it never touches the filesystem), add it to GitHub, and add its public half to `allowed_signers` as a second line.

Keep the old line in `allowed_signers`. Removing it makes every commit you have already signed fail verification. Two lines cost nothing and preserve history.

## Rollback

Each stage reverses independently:

| Stage | Undo |
|---|---|
| 3 | Point `user.signingkey` back at the old key |
| 2 | Restore the private key from the 1Password backup to `~/.ssh/`, `chmod 600` |
| 1 | Remove `IdentityAgent` from ssh config; remove `gpg.ssh.program` from gitconfig |

Stage 1 rollback is the important one, and it is two config lines. Nothing is destroyed until Stage 2, which is why Stage 2 is gated on days of real use rather than a single successful test.

## Trade-offs, stated plainly

**What you gain.** No private key on disk. Per-use biometric approval. Keys sync across your machines through 1Password rather than being copied by hand. A stolen laptop yields no usable key.

**What you give up.** 1Password must be running and unlocked before the first git operation of the day. Headless and unattended work breaks — that is the real constraint here, given how much of your workflow runs agents that commit on their own. Any tool that reads `~/.ssh/id_ed25519` directly stops working; most use the agent, but not all. And you take a dependency on 1Password being healthy for your ability to push code.

**The honest middle option**, if the unattended-work constraint turns out to bite: put a passphrase on the on-disk key and add it to the macOS keychain. Weaker than the agent, much stronger than today, and nothing about your workflow changes.

## Open questions

- **Track `~/.ssh/config` in dotfiles?** It is currently untracked, so this change would not reproduce on a new machine. The config itself holds no secrets. The counter-argument is that `.ssh/` is a directory where an accidental `git add` is expensive — the old `install.conf.yaml` even carries a commented-out TODO about symlinking into `.ssh`, suggesting this was considered before and dropped.
- **Do the unattended agent sessions commit?** If `bmad-loop` runs sign commits while you are away, Stage 1 will block them. Worth checking before starting, not after.
- **Any non-GitHub hosts** using this key — servers, Tailscale nodes, deploy targets? The `Host *` block covers them, but each needs testing.
