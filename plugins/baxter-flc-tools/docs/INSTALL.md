# Baxter FLC Tools Installation

## Prerequisites

- Baxter FLC Tools plugin installed from the marketplace.
- Node.js 20+ for the cross-platform launcher.
- A Baxter Entra identity with Azure AI Search data-plane read access to `ais-flc-product-agents`.

The MCP server uses Entra authentication through the local developer identity. It never uses Azure AI Search admin keys.

## Enable the FLC Tools knowledge MCP

1. Install or update the `baxter-flc-tools` plugin.
2. Sign in with Azure CLI if you do not already have an Entra developer identity available:

   ```bash
   az login
   ```

3. Enable `flc-tools-knowledge` in the Cursor or VS Code MCP settings.
4. Reload the MCP server. The launcher selects the self-contained binary for the current platform.

## VS Code: set the plugin directory

VS Code does not expand the `${PLUGIN_ROOT}` placeholder for plugin MCP servers, so the `flc-tools-knowledge` server reads the plugin directory from `FLC_TOOLS_PLUGIN_DIR` in the config file. Set it once per machine. (Cursor supplies its own plugin root and does not need this.)

1. Find the installed plugin directory — the `baxter-flc-tools` folder under the VS Code agent-plugins location:

   | OS | Base location |
   |---|---|
   | Windows | `%USERPROFILE%\.vscode\agent-plugins\` |
   | macOS / Linux | `~/.vscode/agent-plugins/` |

   The full path includes marketplace and repository segments, for example:
   `...\.vscode\agent-plugins\dev.azure.com\<org>\<project>\_git\<repo>\plugins\baxter-flc-tools`

2. Add a `FLC_TOOLS_PLUGIN_DIR` line with that path to the config file:

   | OS | Config path |
   |---|---|
   | Linux / macOS | `~/.config/flc-tools-knowledge-mcp.env` |
   | Windows | `%USERPROFILE%\.config\flc-tools-knowledge-mcp.env` |

   Example line (Windows):

   ```ini
   FLC_TOOLS_PLUGIN_DIR=%USERPROFILE%\.vscode\agent-plugins\<marketplace>\plugins\baxter-flc-tools
   ```

   `%USERPROFILE%`, `${HOME}`, and a leading `~` are expanded; a home-relative path is resolved against your home directory.

3. Reload the `flc-tools-knowledge` MCP server (or reload the VS Code window).

## Optional configuration

Configure the approved Search service and index using non-secret values.

| OS | Config path |
|---|---|
| Linux / macOS | `~/.config/flc-tools-knowledge-mcp.env` |
| Windows | `%USERPROFILE%\.config\flc-tools-knowledge-mcp.env` |

The launcher creates this file automatically from `mcp-servers/flc-tools-knowledge-mcp.env.example` on first use. Do not put keys, tokens, connection strings, or other secrets in this file.

## Verify

In Cursor or VS Code chat, ask an FLC Tools factual question such as:

> Search the FLC Tools knowledge base for a known SAP document and cite the source.

A successful response contains snippets and source citations. No results means the query has no indexed evidence; it is not a prompt to invent an answer.

## Troubleshooting

| Symptom | Resolution |
|---|---|
| Authentication or authorization failure | Run `az login` with the Baxter tenant and request the required Azure AI Search data-plane role. |
| No search results | Verify the configured endpoint/index and confirm the corpus has been indexed. |
| `FLC Tools Search is unavailable (400)` | Verify `FLC_TOOLS_SEARCH_INDEX` matches an existing index, then reload the MCP server. |
| MCP does not start (VS Code) | Add `FLC_TOOLS_PLUGIN_DIR=<plugin directory>` to `~/.config/flc-tools-knowledge-mcp.env`, then reload the MCP server. |
| MCP does not start | Check the MCP output logs for the Node launcher error and confirm Node.js 20+ is available. |
