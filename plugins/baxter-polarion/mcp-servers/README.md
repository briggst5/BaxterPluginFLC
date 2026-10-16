# PolarionMCP (.NET)

MCP server for Polarion ALM using SOAP/WSDL services.

## Status

- **Binary-only** delivery in this plugin (no `dotnet/` sources in-repo)
- Runtime: `.NET 8` (self-contained under `bin/<rid>/`)
- Transport: MCP stdio
- Platforms: `win-x64`, `linux-x64`, `osx-x64`, `osx-arm64`
- API surface: Polarion SOAP only (no REST)

## Layout

```text
../bin/<rid>/polarion-mcp[.exe]   Prebuilt MCP server
../scripts/launch-polarion-mcp.mjs  Cross-platform launcher
polarion-mcp.env.example            Config template
docs/OPERATIONS.md                  Install / config / troubleshooting
```

## Tools

- `get_work_item`
- `set_work_item_status`
- `list_work_item_workflow_actions`
- `get_work_item_links`
- `add_work_item_link`
- `remove_work_item_link`
- `get_work_item_raw_fields`
- `query_work_items`
- `list_documents`
- `list_document_work_items`
- `list_configuration_srs_inventory`
- `get_document_text`

## Run

```bash
node scripts/setup-polarion-env.mjs   # from plugin root
# edit ~/.config/polarion-mcp.env
```

Enable **polarion-mcp** in Cursor → Settings → MCP. The launcher requires a vendored binary; it does not build from source.

## Configuration

See `polarion-mcp.env.example` and [docs/OPERATIONS.md](docs/OPERATIONS.md).
