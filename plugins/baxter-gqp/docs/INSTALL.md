# Baxter GQP Knowledge — setup and use

Use this to search Baxter GQP and GQT procedures from Cursor and get answers with document citations. You do not install a program, sign in to Azure, or create a config file. The plugin already contains the service address and access token.

You need Cursor on the corporate network (or otherwise able to reach the GQP service over HTTPS), and the **Baxter GQP Knowledge** plugin, version **0.5.0 or later**, from the team marketplace.

## 1. Install the plugin

1. Open **Cursor Settings → Plugins**.
2. Find the marketplace **`frontlinecare-baxter-plugins`**. 
3. Install **Baxter GQP Knowledge** (`baxter-gqp`). If it is not listed, your account is not in the group that receives this plugin. Ask a Cursor org admin to assign it.
4. Confirm the version is **0.5.0 or later**.
5. Reload Cursor (Command Palette → **Developer: Reload Window**).

If you previously installed an older GQP plugin, uninstall that copy first. You can delete these leftover files if they exist. They are not used anymore:

- Linux / macOS: `~/.config/gqp-mcp.env` and `~/.config/gqp-mcp.secrets.json`
- Windows: `%USERPROFILE%\.config\gqp-mcp.env` and `%USERPROFILE%\.config\gqp-mcp.secrets.json`

## 2. Turn on the MCP server

1. Open **Cursor Settings → MCP**.
2. Enable **gqp-knowledge**.
3. Confirm it lists these tools:

- `search_gqp_documents`
- `find_testing_requirements`
- `find_risk_mitigations`
- `find_security_tasks`
- `find_required_deliverables`
- `assess_change_impact`
- `build_project_plan`

No other setup is required. Do not copy the token out of the plugin settings into chat, tickets, scripts, or another tool.

## 3. Ask a question

In Cursor chat, ask in plain language. Name a procedure number when you have one.

- "What deliverables are required if we change the sterilization method?"
- "What V&V does GQP require for software changes?"
- "What risk tasks apply to GQP-09-06?"
- "Verify the GQP citations in this design plan."

For a check before a gate review, invoke the **gqp-compliance-reviewer** agent and give it the plan or section to check.

Answers cite a document ID, revision, and section when the source provides them. They describe the corporate quality system. Product requirements stay in Polarion, and sprint work stays in Azure DevOps.

## If something fails

| What you see | What to do |
|---|---|
| Plugin is missing from the marketplace | Confirm you are under **`frontlinecare-baxter-plugins`**, then ask an admin to assign **Baxter GQP Knowledge** to your group. |
| `401 Unauthorized`, or the MCP server shows an auth error | Update **Baxter GQP Knowledge** to the latest version and reload Cursor. The access token was rotated. |
| Connection timeout | Check that this machine can reach the GQP service over HTTPS, including any proxy. |
| Tools return a generic error | Note the time and send it to the GQP maintainers. The failure is on the service. |
| No documents found | Rephrase the question, or drop a procedure number / family filter and search again. |
| Two copies of the plugin | Uninstall the one under **`briggst5-baxterplugin`**. Keep the **`frontlinecare-baxter-plugins`** copy. |

If you believe the access token was copied outside the plugin, tell the GQP maintainers so they can revoke it. Do not paste the token into the report.
