# Switch to the Front Line Care marketplace

The Baxter plugins now ship from the official team marketplace. If you still see the older personal marketplace, remove it and install from the new source.

| | Old (remove) | New (use this) |
|--|--------------|----------------|
| **Marketplace label** | `briggst5-baxterplugin` | `frontlinecare-baxter-plugins` |
| **Typical button** | **Get** | **Try** / **Install** |
| **Context tag** | Baxter - Front Line Care | Baxter - Front Line Care |

Both can list the same plugin names (Baxter Core, Polarion, Security, and so on). Always check the **marketplace header** above the list, not only the plugin title.

## 1. Uninstall plugins from the old marketplace

1. Open **Cursor Settings** → **Plugins** (or **Customize** in the sidebar).
2. Find the section headed **`briggst5-baxterplugin`**.
3. For each Baxter plugin installed from that section, choose **Uninstall** (or disable / turn off if Uninstall is unavailable).
4. Repeat until nothing under `briggst5-baxterplugin` is installed.

You do **not** need to delete MCP credential files under `~/.config/` (or `%USERPROFILE%\.config\` on Windows). Those stay valid after you reinstall from the new marketplace.

## 2. Remove the old marketplace source

If `briggst5-baxterplugin` still appears as a marketplace you added yourself:

1. Stay in **Settings** → **Plugins**.
2. Open marketplace / source management for that entry (gear, overflow menu, or remove control next to the marketplace name).
3. **Remove** / disconnect **`briggst5-baxterplugin`**.

If the old marketplace was pushed by org policy and you cannot remove it, stop installing from that section and use only **`frontlinecare-baxter-plugins`**. Ask a Cursor org admin to retire the old marketplace for the team.

## 3. Install from the new marketplace

1. In **Settings** → **Plugins**, find **`frontlinecare-baxter-plugins`**.
2. Install what you need (start with **Baxter Core**):

   | Plugin | Who needs it |
   |--------|----------------|
   | Baxter Core | Everyone |
   | Baxter Product Owner | PO / RTE / agile teams |
   | Baxter Polarion | Polarion / ALM workflows |
   | Baxter FLC Platform Software | Platform / embedded SW |
   | Baxter Security | Security / CVE triage |
   | Baxter GQP Knowledge | Quality / compliance |

3. Reload Cursor if prompted (Command Palette → **Developer: Reload Window**).
4. Open **Settings** → **MCP** and enable servers for the plugins you use (for example `polarion-mcp`, `azure-devops`, `gqp-knowledge`).

## 4. Verify

- In Plugins, installed Baxter plugins appear under **`frontlinecare-baxter-plugins`**, not under `briggst5-baxterplugin`.
- In chat, try: *"Review this diff using baxter standards"* (needs Baxter Core).
- MCP servers you previously configured still start with the same env files.

## Troubleshooting

| Symptom | What to do |
|---------|------------|
| Same plugin listed twice | Uninstall the copy under `briggst5-baxterplugin`; keep only the new marketplace install |
| Skills or agents missing | Confirm install under `frontlinecare-baxter-plugins`, then reload the window |
| MCP still red | Re-enable the server in Settings → MCP; check env files per [getting-started](getting-started.md) |
| Cannot remove old marketplace | Use only the new section for installs; ask an org admin to delete the old Team Marketplace |

## Related

- [Getting started](getting-started.md) — install order and role-based plugins
- Per-plugin [INSTALL](../plugins/baxter-core/docs/INSTALL.md) guides under each `plugins/*/docs/` folder
