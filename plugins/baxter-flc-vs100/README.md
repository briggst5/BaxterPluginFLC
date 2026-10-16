# Baxter FLC VS100

VS100 knowledge retrieval for Baxter engineers through an Azure AI Search-backed MCP server in Cursor and VS Code.

## Included capabilities

| Capability | Description |
|---|---|
| `vs100-knowledge` skill | Routes grounded product and implementation questions to the VS100 knowledge MCP. |
| `vs100-knowledge` MCP | Searches the curated `vs100-kb-chunks-v2` index and returns source citations. |

## Installation

See [docs/INSTALL.md](docs/INSTALL.md) for prerequisites, Entra authentication, optional non-secret configuration, verification, and troubleshooting.

**VS Code users:** set `VS100_PLUGIN_DIR` to the installed plugin directory in `~/.config/vs100-knowledge-mcp.env`. VS Code does not expand `${PLUGIN_ROOT}` for plugin MCP servers, so the launcher reads this value to locate itself. See [VS Code: set the plugin directory](docs/INSTALL.md#vs-code-set-the-plugin-directory). Cursor does not need this.

## Authentication

The self-contained MCP binary authenticates with the local developer's Entra identity (Azure CLI, VS Code, Windows SSO, or managed identity). Users need Azure AI Search data-plane read access. The launcher creates `~/.config/vs100-knowledge-mcp.env` on first use with placeholder-only settings.

Maintainers publish binaries for `linux-x64`, `osx-arm64`, `osx-x64`, and `win-x64` under `bin/<rid>/`. Do not store Search keys, access tokens, connection strings, or corpus content in plugin configuration or logs.
