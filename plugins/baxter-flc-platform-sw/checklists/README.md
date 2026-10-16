# Checklists Directory

Reusable code review evaluation frameworks in Markdown. All checklists are tool-agnostic and apply equally to AI-generated and hand-written code.

**Plugin users:** skills and rules reference `checklists/` in this plugin — no per-project copy required when **baxter-flc-platform-sw** is installed.

## Available checklists

| File | Use with skill |
|------|----------------|
| [code-review-checklist.md](code-review-checklist.md) | `code-review` |
| [pr-review-checklist.md](pr-review-checklist.md) | `pr-review` |
| [class-c-code-checklist.md](class-c-code-checklist.md) | Class C / safety-critical review |
| [kotlin-checklist.md](kotlin-checklist.md) | Kotlin sources (`kotlin-review` rule) |
| Plus API, concurrency, error-handling, security, etc. | Scoped reviews in skill workflows |

### IEC 62304 / Class C

Use `class-c-code-checklist.md` and the `iec62304-requirements` rule with **baxter-polarion** for Polarion-backed requirements workflows.

## Checklist immutability

These checklists are **shared read-only assets** in the plugin distribution. Projects should not fork modified checklist copies into app repos.

## Integration

| Tool | How checklists are used |
|------|-------------------------|
| **Cursor + plugin** | `code-review` / `pr-review` skills + `foundation-standards` rule |
| Copilot | [copilot-setup.md](../docs/copilot-setup.md) |

Install: [INSTALL.md](../docs/INSTALL.md)
