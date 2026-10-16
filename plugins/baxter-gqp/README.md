# Baxter GQP Knowledge Plugin

Standalone plugin for **GQP Knowledge MCP** — hybrid RAG search over Baxter GQP/GQT documents, plus skills and rules for **compliance Q&A with verified citations**.

| | |
|--|--|
| **Audience** | Quality, regulatory, engineering leads, compliance reviewers |
| **Install guide** | [docs/INSTALL.md](docs/INSTALL.md) (Linux, macOS, Windows) |
| **Not related to** | Polarion MCP — connects to the hosted `gqp-knowledge` service |

## Quick start

1. Install **baxter-gqp** from the private marketplace.
2. Enable **gqp-knowledge** in Cursor → Settings → MCP.
3. Try: *"What deliverables are required if we change the sterilization method?"*

No binary, Node.js, Azure CLI, Key Vault access, or sign-in is required on your machine.

Pair with **baxter-product-owner** when answers must also trace to Polarion requirements or ADO delivery items.

## What's included

### Skills

| Skill | Purpose |
|-------|---------|
| `gqp-compliance-advisor` | Route compliance questions to MCP tools; format cited answers |

### Agents

| Agent | Purpose |
|-------|---------|
| `gqp-compliance-reviewer` | Audit plans and documents for citation accuracy before gate reviews |

### Rules (Cursor only)

| Rule | Purpose |
|------|---------|
| `gqp-compliance-citations` | Require GQP/GQT doc_id, revision, section citations; flag unsupported claims |

### MCP tools

| Tool | Purpose |
|------|---------|
| `search_gqp_documents` | General GQP/GQT search |
| `find_testing_requirements` | V&V requirements |
| `find_risk_mitigations` | Risk-related tasks |
| `find_security_tasks` | Security activities |
| `find_required_deliverables` | Deliverable lists |
| `assess_change_impact` | Change impact on quality system |
| `build_project_plan` | Project planning support |

## How it connects

`gqp-knowledge` is a remote MCP server (Streamable HTTP) hosted in Azure. Search and model credentials stay in the service, which reaches Azure AI Search and Azure OpenAI with its own managed identity.

Requests carry a **shared access token** that the release pipeline writes into this plugin's packaged `.mcp.json`. The source repository only contains `__GQP_MCP_URL__` / `__GQP_MCP_TOKEN__` placeholders.

### Shared-token limitations (interim, until SSO)

- The token identifies "a holder of this plugin", not an individual user. There is no per-user attribution or revocation.
- Anyone who has the installed plugin can read the token. Do not copy it into other tools, scripts, tickets, or chats.
- The endpoint is internet-reachable; requests without a valid token are rejected with `401`.
- The token is rotated periodically and immediately on suspected exposure. After a rotation, update the plugin; the old token stops working at the end of the overlap window.

**Suspected exposure:** report it to the GQP maintainers right away. They revoke the token (see the GQP repo `docs/cloud-mcp.md`) and publish a new plugin version.

## Example prompts

- "What V&V does GQP-1234 require for software?"
- "Verify the GQP citations in this design plan"
- "What deliverables are required if we change the sterilization method?"

## Maintainers

This plugin ships configuration, rules, skills, and agents only — no binaries. The service source, infrastructure, and release scripts live in the private GQP repo.

Never commit a real token into this repository. Publish with `scripts/package-plugin.sh` from the GQP repo, which injects the token from Key Vault into a staged copy, verifies the source tree is token-free, and writes the artifact to the restricted distribution repo.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).
