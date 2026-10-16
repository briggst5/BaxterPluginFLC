# BaxterPlugin

Enterprise team marketplace for Baxter engineering: shared MCP servers, skills, rules, and agents for **Cursor** and **VS Code GitHub Copilot**.

**New users:** start with [docs/getting-started.md](docs/getting-started.md) — install order, per-OS setup, and example prompts.

**Already on the old `briggst5-baxterplugin` marketplace?** Switch to **`frontlinecare-baxter-plugins`** using [docs/migrate-marketplace.md](docs/migrate-marketplace.md).

## Plugins

| Plugin | Cursor mode | Audience | Documentation |
|--------|-------------|----------|-----------------|
| [baxter-core](plugins/baxter-core/) | **Required** | All engineers | [README](plugins/baxter-core/README.md) · [INSTALL](plugins/baxter-core/docs/INSTALL.md) |
| [baxter-product-owner](plugins/baxter-product-owner/) | SCIM group | PO, RTE, agile teams | [README](plugins/baxter-product-owner/README.md) · [INSTALL](plugins/baxter-product-owner/docs/INSTALL.md) |
| [baxter-polarion](plugins/baxter-polarion/) | SCIM group | Teams using Polarion | [README](plugins/baxter-polarion/README.md) · [INSTALL](plugins/baxter-polarion/docs/INSTALL.md) |
| [baxter-flc-platform-sw](plugins/baxter-flc-platform-sw/) | SCIM group | Platform / embedded SW | [README](plugins/baxter-flc-platform-sw/README.md) · [INSTALL](plugins/baxter-flc-platform-sw/docs/INSTALL.md) |
| [baxter-security](plugins/baxter-security/) | SCIM group | Security, release gates | [README](plugins/baxter-security/README.md) · [INSTALL](plugins/baxter-security/docs/INSTALL.md) |
| [baxter-gqp](plugins/baxter-gqp/) | SCIM group | Quality / compliance | [README](plugins/baxter-gqp/README.md) · [INSTALL](plugins/baxter-gqp/docs/INSTALL.md) |
| [baxter-flc-tools](plugins/baxter-flc-tools/) | SCIM group | FLC engineers using SAP docs | [README](plugins/baxter-flc-tools/README.md) · [INSTALL](plugins/baxter-flc-tools/docs/INSTALL.md) |


## Quick start

```bash
# Validate marketplace structure
./scripts/validate-plugin.sh
```

Then configure MCP per plugin INSTALL guide, reload Cursor, enable MCP servers in Settings.

## Cursor Team Marketplace rollout

1. Push this repo to your org GitHub (e.g. `your-org/BaxterPlugin`).
2. Cursor Dashboard → Settings → Plugins → Team Marketplaces → **Import from Repo**.
3. Set `baxter-core` to **Required**; map optional plugins to SCIM groups.
4. Enable **Auto Refresh**.
5. Run `./scripts/validate-plugin.sh` in CI on every PR.

## VS Code Copilot rollout

VS Code discovers this repo as an agent plugin marketplace via
[.github/plugin/marketplace.json](.github/plugin/marketplace.json). Each plugin
exposes a VS Code manifest at `<plugin>/.plugin/plugin.json`.

1. Ensure `chat.plugins.enabled` is `true` (managed at the org level; contact your admin if it is disabled).
2. Add the marketplace in user or workspace `settings.json`:

```json
"chat.plugins.marketplaces": [
  "your-org/BaxterPlugin"
]
```

3. Open the Extensions view, search `@agentPlugins`, and install the Baxter plugins. The first install from a new marketplace shows a trust prompt.
4. For team defaults, copy [templates/copilot-settings.json](templates/copilot-settings.json) into `.github/copilot/settings.json` (or `.claude/settings.json`) of consuming projects to recommend the marketplace and enable `baxter-core` by default.

**Note:** Cursor `.mdc` rules are not available in Copilot. Use the `baxter-standards` skill for equivalent guidance.

## Contributing

Skills, MCP, rules, and agents are **vendored into this repo** and committed. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Repository layout

```
.cursor-plugin/marketplace.json   # Cursor marketplace index
.github/plugin/marketplace.json   # VS Code Copilot marketplace index
plugins/baxter-core/              # required core plugin
plugins/baxter-security/          # optional domain plugin
.cursor-plugin/marketplace.json   # marketplace index
docs/getting-started.md           # user onboarding hub
plugins/                          # one directory per plugin
scripts/                          # bootstrap, validate, add-mcp-entry
templates/                        # Copilot workspace settings
```

## License

MIT — see [LICENSE](LICENSE).
