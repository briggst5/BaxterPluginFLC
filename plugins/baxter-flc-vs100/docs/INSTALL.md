# Baxter FLC VS100 Installation

## Prerequisites

- Baxter FLC VS100 plugin installed from the marketplace.
- Node.js 20+ for the cross-platform launcher.
- A Baxter Entra identity with Azure AI Search data-plane read access to `ais-flc-product-agents`.

The MCP server uses Entra authentication through the local developer identity. It never uses Azure AI Search admin keys.

## Enable the VS100 knowledge MCP

1. Install or update the `baxter-flc-vs100` plugin.
2. Sign in with Azure CLI if you do not already have an Entra developer identity available:

   ```bash
   az login
   ```

3. Enable `vs100-knowledge` in the Cursor or VS Code MCP settings.
4. Reload the MCP server. The launcher selects the self-contained binary for the current platform.

## VS Code: set the plugin directory

VS Code does not expand the `${PLUGIN_ROOT}` placeholder for plugin MCP servers, so the `vs100-knowledge` server reads the plugin directory from `VS100_PLUGIN_DIR` in the config file. Set it once per machine. (Cursor supplies its own plugin root and does not need this.)

1. Find the installed plugin directory — the `baxter-flc-vs100` folder under the VS Code agent-plugins location:

   | OS | Base location |
   |---|---|
   | Windows | `%USERPROFILE%\.vscode\agent-plugins\` |
   | macOS / Linux | `~/.vscode/agent-plugins/` |

   The full path includes marketplace and repository segments, for example:
   `...\.vscode\agent-plugins\dev.azure.com\<org>\<project>\_git\<repo>\plugins\baxter-flc-vs100`

2. Add a `VS100_PLUGIN_DIR` line with that path to the config file:

   | OS | Config path |
   |---|---|
   | Linux / macOS | `~/.config/vs100-knowledge-mcp.env` |
   | Windows | `%USERPROFILE%\.config\vs100-knowledge-mcp.env` |

   Example line (Windows):

   ```ini
   VS100_PLUGIN_DIR=%USERPROFILE%\.vscode\agent-plugins\<marketplace>\plugins\baxter-flc-vs100
   ```

   `%USERPROFILE%`, `${HOME}`, and a leading `~` are expanded; a home-relative path is resolved against your home directory.

3. Reload the `vs100-knowledge` MCP server (or reload the VS Code window).

## Optional configuration

Configure the approved Search service and index using non-secret values.

| OS | Config path |
|---|---|
| Linux / macOS | `~/.config/vs100-knowledge-mcp.env` |
| Windows | `%USERPROFILE%\.config\vs100-knowledge-mcp.env` |

The launcher creates this file automatically from `mcp-servers/vs100-knowledge-mcp.env.example` on first use. Do not put keys, tokens, connection strings, or other secrets in this file.

## Verify

In Cursor or VS Code chat, ask a VS100 factual question such as:

> Search the VS100 knowledge base for the configuration-store module and cite the source.

A successful response contains snippets and source citations. No results means the query has no indexed evidence; it is not a prompt to invent an answer.

## Troubleshooting

| Symptom | Resolution |
|---|---|
| Authentication or authorization failure | Run `az login` with the Baxter tenant and request the required Azure AI Search data-plane role. |
| No search results | Verify the configured endpoint/index and confirm the corpus has been indexed. |
| `VS100 Search is unavailable (400)` | Update to plugin version 0.2.1 or later, then reload the MCP server. |
| `Cannot find module 'c:\\scripts\\launch-vs100-knowledge-mcp.mjs'` | Update to plugin version 0.2.2 or later, then reinstall or update the plugin and reload VS Code. |
| `Cannot find module '...${PLUGIN_ROOT}...launch-vs100-knowledge-mcp.mjs'` (VS Code) | Add `VS100_PLUGIN_DIR=<plugin directory>` to `~/.config/vs100-knowledge-mcp.env`, then reload the MCP server. |
| MCP does not start | Check the MCP output logs for the Node launcher and Python dependency error. |
