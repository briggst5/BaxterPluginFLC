# VS100 Knowledge MCP

Standalone MCP server for citation-ready retrieval from the curated VS100 Azure AI Search index.

## Status

- Runtime: .NET 8 self-contained binary
- Transport: MCP stdio
- Clients: Cursor and VS Code GitHub Copilot
- Authentication: ambient Baxter Entra identity through `DefaultAzureCredential`

## Tool

- `search_vs100_knowledge`: searches `vs100-kb-chunks-v2` and returns bounded snippets with file, Blob URL, and chunk citations.

## Run

Enable `vs100-knowledge` in the Cursor or VS Code MCP settings. On first use, the launcher creates `~/.config/vs100-knowledge-mcp.env` from `vs100-knowledge-mcp.env.example`.

Manual setup:

```bash
node scripts/setup-vs100-knowledge-env.mjs
bin/linux-x64/vs100-knowledge-mcp
```

## Configuration

The user-level configuration contains only tenant, Search endpoint, and index settings. The server uses the ambient Entra identity and Azure AI Search data-plane RBAC; it does not require user-managed Search keys.

## Troubleshooting

- Run `az login` when Entra authentication is unavailable.
- Set `REQUESTS_CA_BUNDLE` in the user config only when a corporate proxy requires a CA bundle.