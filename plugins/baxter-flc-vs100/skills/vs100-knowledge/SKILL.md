---
name: vs100-knowledge
description: Search the approved VS100 Azure AI Search knowledge base and return grounded answers with source citations. Use for VS100 product, architecture, implementation, and indexed-document questions.
---

# VS100 Knowledge

## Prerequisites

- The `vs100-knowledge` MCP server must be enabled and available.
- The user must be authenticated with a Baxter Entra identity that has Azure AI Search data-plane read access.
- Treat an MCP authentication, authorization, or availability failure as unavailable knowledge-base evidence. State the failure plainly; do not answer VS100 factual claims from memory as a fallback.

## MCP Tools

| Question type | Tool | Use when |
|---|---|---|
| General or mixed VS100 question | `search_vs100_knowledge` | The source type is unclear or the question spans multiple domains. |
| Implementation or build question | `find_vs100_source_code` | The user asks about code, configuration, Yocto/BitBake, a repository, or a source path. Narrow with `repository` or `path` when supplied. |
| SAP product-document question | `find_vs100_product_documents` | The user asks about product documents, requirements, procedures, or a known SAP DIR. Narrow with `sapDir` when supplied. |
| Architecture or design question | `find_vs100_architecture` | The user asks about architecture, component design, or system behavior. |
| Returned excerpt follow-up | `get_vs100_source_document` | A previous result's `chunk_id` needs direct follow-up inspection. |

## Retrieval Rules

- For every VS100 product, architecture, implementation, source-code, build, or indexed-document question, query the VS100 knowledge MCP before answering factual claims.
- Select the narrowest available tool described above. Start with 3 to 5 results; request more only when the available evidence is insufficient.
- Do not answer a VS100 factual question from model knowledge alone. Do not invent VS100 facts, source details, or citations.
- When the knowledge tool returns no indexed evidence or is unavailable, say so plainly. Explain that the answer cannot be verified from the approved VS100 knowledge base.

## Clarification And Fallbacks

- Ask a focused clarification question before searching or answering when the request is ambiguous enough that the intended VS100 component, repository, SAP DIR, version, branch, or time frame cannot be identified reliably.
- Prefer a targeted follow-up search when the ambiguity can be resolved from the initial retrieved evidence.
- Use web search only as a last resort: first query the VS100 knowledge base, then request clarification when necessary. Use the web only for external, general, or publicly documented context that is not available in the knowledge base.
- Never present web content as VS100 evidence. Label it as external information and state that it was not verified against the approved VS100 corpus.

## Common Workflows

### Source Code Or Build Lookup

1. Identify any repository, branch, source path, module, build target, or BitBake term in the request.
2. Use `find_vs100_source_code`, adding the available `repository` or `path` filter.
3. If the result is incomplete, refine the query or inspect the relevant `chunk_id` with `get_vs100_source_document`.
4. Answer only from retrieved snippets and cite repository, branch, source path, file name, document type, and chunk ID when useful.

### SAP Product-Document Lookup

1. Identify the document topic and SAP DIR, if supplied.
2. Use `find_vs100_product_documents`, adding `sapDir` when known.
3. If no result is returned, state that there is no approved indexed evidence and ask for a DIR or alternate terms when that would make the search more precise.
4. Cite SAP DIR, file name, source path, document type, and chunk ID when useful.

### Architecture Or Cross-Corpus Question

1. Use `find_vs100_architecture` for an architecture-specific question; otherwise use `search_vs100_knowledge`.
2. If retrieved sources are incomplete or disagree, state the limitation, identify the evidence that differs, and avoid a definitive factual conclusion.
3. Ask a focused clarification question or perform a targeted follow-up search before using external sources.

## Evidence And Citations

- Separate retrieved facts from interpretation. Clearly label evidence-based statements as **Retrieved evidence** and any inference, recommendation, comparison, or engineering judgment as **Engineering judgment**.
- Base factual VS100 claims only on the returned snippets. State when the snippets are incomplete, conflicting, or insufficient to support a conclusion.
- Cite the metadata returned by the MCP tool, not the Azure AI Search Blob URL. Include the relevant available fields:
	- SAP documents: `sap_dir`, `file_name`, `source_path`, and `document_type`.
	- Source code: `repository`, `branch`, `source_path`, `file_name`, and `document_type`.
	- Any result: include the `chunk_id` when it helps identify the supporting excerpt.
- Omit metadata fields that are empty or have the value `not_applicable`. In particular, do not require or infer `sap_dir` for source-code results or cite a branch for non-code results.
- Use the Blob URL only when the user explicitly asks for the storage location.

## Never

- Never answer a VS100 factual question without first querying the VS100 knowledge MCP.
- Never invent a repository, branch, SAP DIR, source path, file name, document type, chunk ID, or citation.
- Never present retrieved snippets, synthesized conclusions, or engineering judgment as verbatim source text.
- Never present web content as approved VS100 knowledge-base evidence.
