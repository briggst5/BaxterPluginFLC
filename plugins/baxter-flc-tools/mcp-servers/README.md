# FLC Tools Knowledge MCP

Standalone MCP server for citation-ready retrieval from the curated FLC Tools Azure AI Search index.

## Status

- Runtime: .NET 8 self-contained binary
- Transport: MCP stdio
- Clients: Cursor and VS Code GitHub Copilot
- Authentication: ambient Baxter Entra identity through `DefaultAzureCredential`

## Tools

- `search_flc_tools_knowledge`: general search over `flc-tools-index-v2` with bounded, cited snippets.
- `find_flc_tools_document`: filtered search with optional `sapDir` and `documentType`.
- `get_flc_tools_document`: retrieve a chunk by its citation chunk ID.

## Run

Enable `flc-tools-knowledge` in the Cursor or VS Code MCP settings. On first use, the launcher creates `~/.config/flc-tools-knowledge-mcp.env` from `flc-tools-knowledge-mcp.env.example`.

Manual setup:

```bash
node scripts/setup-flc-tools-knowledge-env.mjs
bin/linux-x64/flc-tools-knowledge-mcp
```

## Configuration

The user-level configuration contains only tenant, Search endpoint, and index settings. The server uses the ambient Entra identity and Azure AI Search data-plane RBAC; it does not require user-managed Search keys.

## Troubleshooting

- Run `az login` when Entra authentication is unavailable.
- Set `REQUESTS_CA_BUNDLE` in the user config only when a corporate proxy requires a CA bundle.
