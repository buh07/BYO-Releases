# BYO Releases

Public download home for the **BYO installer**: the native Rust `byo` launcher,
compiled firmware MCP sidecar, and workflow pack for Codex and Claude.

The current public build is the unsigned
[`v0.1.3-preview`](https://github.com/buh07/BYO-Releases/releases/tag/v0.1.3-preview).
Preview bundles use the offline `--bundle` / `-Bundle` installation path; signed
network installation and automatic updates are not available yet.

## Install from GitHub Releases

Choose the commands for your computer. Each block downloads the native archive,
its `.sha256` receipt, and the separate installer, then verifies the archive
before installation. Python, Rust, `uv`, a source checkout, and administrator
access are not required.

### macOS — Apple silicon

```sh
curl -fLO https://github.com/buh07/BYO-Releases/releases/download/v0.1.3-preview/byo-0.1.3-macos-aarch64.zip
curl -fLO https://github.com/buh07/BYO-Releases/releases/download/v0.1.3-preview/byo-0.1.3-macos-aarch64.sha256
curl -fLO https://github.com/buh07/BYO-Releases/releases/download/v0.1.3-preview/install.sh
shasum -a 256 -c byo-0.1.3-macos-aarch64.sha256
xattr -d com.apple.quarantine ./byo-0.1.3-macos-aarch64.zip 2>/dev/null || true
sh ./install.sh --bundle ./byo-0.1.3-macos-aarch64.zip
```

### macOS — Intel

```sh
curl -fLO https://github.com/buh07/BYO-Releases/releases/download/v0.1.3-preview/byo-0.1.3-macos-x86_64.zip
curl -fLO https://github.com/buh07/BYO-Releases/releases/download/v0.1.3-preview/byo-0.1.3-macos-x86_64.sha256
curl -fLO https://github.com/buh07/BYO-Releases/releases/download/v0.1.3-preview/install.sh
shasum -a 256 -c byo-0.1.3-macos-x86_64.sha256
xattr -d com.apple.quarantine ./byo-0.1.3-macos-x86_64.zip 2>/dev/null || true
sh ./install.sh --bundle ./byo-0.1.3-macos-x86_64.zip
```

### Windows — x86-64

Run in PowerShell:

```powershell
Invoke-WebRequest https://github.com/buh07/BYO-Releases/releases/download/v0.1.3-preview/byo-0.1.3-windows-x86_64.zip -OutFile .\byo-0.1.3-windows-x86_64.zip
Invoke-WebRequest https://github.com/buh07/BYO-Releases/releases/download/v0.1.3-preview/byo-0.1.3-windows-x86_64.sha256 -OutFile .\byo-0.1.3-windows-x86_64.sha256
Invoke-WebRequest https://github.com/buh07/BYO-Releases/releases/download/v0.1.3-preview/install.ps1 -OutFile .\install.ps1
$expected = ((Get-Content .\byo-0.1.3-windows-x86_64.sha256 -Raw).Trim() -split '\s+')[0]
$actual = (Get-FileHash .\byo-0.1.3-windows-x86_64.zip -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected.ToLowerInvariant()) { throw "BYO archive SHA-256 mismatch" }
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Bundle .\byo-0.1.3-windows-x86_64.zip
```

### Linux — x86-64, glibc 2.28+

```sh
curl -fLO https://github.com/buh07/BYO-Releases/releases/download/v0.1.3-preview/byo-0.1.3-linux-x86_64.tar.gz
curl -fLO https://github.com/buh07/BYO-Releases/releases/download/v0.1.3-preview/byo-0.1.3-linux-x86_64.sha256
curl -fLO https://github.com/buh07/BYO-Releases/releases/download/v0.1.3-preview/install.sh
sha256sum -c byo-0.1.3-linux-x86_64.sha256
sh ./install.sh --bundle ./byo-0.1.3-linux-x86_64.tar.gz
```

The checksum command must report `OK` before installation. Installation does
not edit `PATH` by default. Add `--modify-path` to the final macOS/Linux command
or `-ModifyPath` to the Windows command to opt in, then open a new terminal.

## Initialize BYO in a project

The runtime is installed once per computer. Initialize every firmware project
that should use its MCP server:

```sh
cd /path/to/your/firmware-project
byo init --dry-run
byo init
byo codex firmware
# Or launch Claude:
byo claude firmware
```

The dry run is optional. `byo init` creates the project capsule, configures both
clients to start the compiled MCP server through `byo mcp serve`, registers the
project, and runs its health check. It also creates thin native Claude skill
loaders in `.claude/skills`; each loader retrieves its verified private workflow
body only when Claude selects it. Restart an already-open Codex or Claude
session after initialization.

Initialize a project from another directory with:

```sh
byo init --project /path/to/your/firmware-project
```

## Uninstall from one project

Close sessions using the project, then run from its root:

```sh
byo uninstall
```

Or identify the project explicitly:

```sh
byo uninstall --project /path/to/your/firmware-project
```

This removes BYO-managed client integrations and unregisters the project while
preserving the shared runtime, `.firm`, plans, handoffs, specifications,
backups, and unrelated client configuration. It also removes BYO from Claude's
local MCP approval lists and deletes empty configuration shells left by BYO.

### Purge one project

Run from the project root:

```sh
byo uninstall --purge
```

Or use `byo uninstall --purge --project /path/to/your/firmware-project` from
anywhere. This performs the normal project uninstall and also deletes the
dedicated BYO roots created for that project, including `.agent-workspace`,
`.agent-backups`, `.firm`, `.generated/byo`, and BYO-owned skill directories.
Project source and unrelated Codex or Claude files and settings are preserved.

## Uninstall from the computer

Close active Codex and Claude sessions, then run:

```sh
byo uninstall --global
```

This is the explicit computer-wide purge. It preflights every unique registered
project, applies project purge to each one, and then removes the launcher,
installed runtimes, global data/state/config/cache roots, and recorded PATH
edits. A live project lease or unsafe registered path stops the operation before
project or PATH mutation and reports every registered project path. Duplicate
registry entries for the same canonical project are handled once.

On Windows, the BYO application-data root is removed before the command
returns. Windows Defender or another scanner can briefly keep the renamed,
just-exited launcher open; BYO retries that final file deletion in the
background for up to about two minutes.

| Operation | Removes | Preserves |
|---|---|---|
| `byo uninstall` | Current project's BYO integration | Shared runtime and retained project working data |
| `byo uninstall --purge` | Current project's integration and dedicated BYO data | Project source and unrelated agent configuration |
| `byo uninstall --global` | Every registered project's BYO data plus all global BYO content | Unrelated project source and configuration only |

Every uninstall prints a receipt. Add `--receipt <path>` to write it as JSON.
Downloaded release archives, receipts, and installer scripts are ordinary files
outside the BYO installation and are not deleted automatically.
