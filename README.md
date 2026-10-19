# BYO Releases

Public download home for the **BYO installer**: the native Rust `byo` launcher,
compiled firmware MCP sidecar, and workflow pack for Codex and Claude.

The current public build is the unsigned [v0.1.9 preview](https://github.com/buh07/BYO-Releases/releases/tag/v0.1.9).
It supports macOS 12+ on Apple silicon and Intel, Windows 10 22H2/11 x86-64,
and Linux x86-64 with glibc 2.28+.

## One-line install

Copy the command for your computer. It downloads the installer and verifies the
native archive against its exact SHA-256. Python, Rust, `uv`, a source checkout,
and administrator access are not required. Keep `--allow-unsigned` /
`-AllowUnsigned` for this unsigned preview.

### macOS - Apple silicon

```sh
(set -e; installer=$(curl -fsSL https://github.com/buh07/BYO-Releases/releases/download/v0.1.9/install.sh); printf '%s\n' "$installer" | sh -s -- --version 0.1.9 --base-url https://github.com/buh07/BYO-Releases/releases/download/v0.1.9 --sha256 d3218a331e957e8a88b18b7844ab9c123985029c2fc27bb6035f448d25361afd --allow-unsigned)
```

### macOS - Intel

```sh
(set -e; installer=$(curl -fsSL https://github.com/buh07/BYO-Releases/releases/download/v0.1.9/install.sh); printf '%s\n' "$installer" | sh -s -- --version 0.1.9 --base-url https://github.com/buh07/BYO-Releases/releases/download/v0.1.9 --sha256 4157cfd19958fe92097ec26ddcbf90225ffeca026250964a6f5d3b8c42cd9ef4 --allow-unsigned)
```

### Windows - x86-64 (PowerShell)

```powershell
& ([scriptblock]::Create((New-Object System.Net.WebClient).DownloadString('https://github.com/buh07/BYO-Releases/releases/download/v0.1.9/install.ps1'))) -Version 0.1.9 -BaseUrl 'https://github.com/buh07/BYO-Releases/releases/download/v0.1.9' -Sha256 f5a0862748b1c6985e08bc6c2855ef94c998bb73ceb8c1d1390ded3581f1af18 -AllowUnsigned
```

### Linux - x86-64, glibc 2.28+

```sh
(set -e; installer=$(curl -fsSL https://github.com/buh07/BYO-Releases/releases/download/v0.1.9/install.sh); printf '%s\n' "$installer" | sh -s -- --version 0.1.9 --base-url https://github.com/buh07/BYO-Releases/releases/download/v0.1.9 --sha256 5c0a80ecc78dd412871b057782cd80dce502cc15a354b175fc443df69df23103 --allow-unsigned)
```

Installation adds BYO to `PATH`. On macOS/Linux, open a new terminal afterward.
The inline Windows command makes `byo` available in the current PowerShell
session; restart other terminal apps that were already open.

These bundles are unsigned and not notarized. Signed automatic updates are not
available. The [release assets](https://github.com/buh07/BYO-Releases/releases/tag/v0.1.9)
also include native archives, separate `.sha256` receipts and installer scripts
for manual/offline installation. Use `sh ./install.sh --bundle ./ARCHIVE` on
macOS/Linux or `powershell -NoProfile -ExecutionPolicy Bypass -File ./install.ps1 -Bundle ./ARCHIVE.zip`
on Windows after checking the archive's SHA-256.

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
project, and runs its health check. It also creates thin native skill loaders
for Codex in `.agents/skills` and Claude in `.claude/skills`; each loader retrieves
its verified private workflow body when selected. Restart an already-open Codex
or Claude session after initialization.

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
