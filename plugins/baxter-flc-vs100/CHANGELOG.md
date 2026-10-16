# Changelog

## 0.2.2 - 2026-09-09

- Use the Agent Plugins 1.0 root manifest and `mcp.json` for VS Code MCP discovery so `${PLUGIN_ROOT}` resolves to the installed plugin directory.

## 0.2.1 - 2026-09-09

- Fixed VS100 knowledge retrieval requests that selected the removed `product` index field and failed with Azure AI Search HTTP 400.
- Use any-term matching for multi-term knowledge queries.
- Rebuilt bundled `linux-x64`, `osx-arm64`, `osx-x64`, and `win-x64` MCP binaries.

## 0.2.0 - 2026-09-01

- Added the `vs100-knowledge` Azure AI Search MCP server for Cursor and VS Code.
- Added Entra-authenticated, citation-ready Search retrieval from the VS100 knowledge index.
- Added cross-platform launchers, installation guidance, configuration example, and retrieval skill.
- Removed the obsolete static VS100 reference skill bundle in favor of the curated knowledge base.
- Converted plugin delivery to self-contained platform binaries; source now builds separately in `vs100-knowledge-mcp`.
