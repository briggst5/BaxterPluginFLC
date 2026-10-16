---
name: flc-tools-knowledge
description: Search the approved FLC Tools SAP document knowledge base in Azure AI Search and return grounded answers with source citations. Use for FLC Tools product-document, procedure, and indexed-document questions.
---

# FLC Tools Knowledge

## Prerequisites

- The `flc-tools-knowledge` MCP server must be enabled and available.
- The user must be authenticated with a Baxter Entra identity that has Azure AI Search data-plane read access.
- Treat an MCP authentication, authorization, or availability failure as unavailable knowledge-base evidence. State the failure plainly; do not answer FLC Tools factual claims from memory as a fallback.

## MCP Tools

| Question type | Tool | Use when |
|---|---|---|
| General FLC Tools document question | `search_flc_tools_knowledge` | The topic is unclear or spans multiple documents. |
| Known document, SAP DIR, or type | `find_flc_tools_document` | The user references a specific SAP DIR or a document type. Narrow with `sapDir` or `documentType` when supplied. |
| Returned excerpt follow-up | `get_flc_tools_document` | A previous result's `chunk_id` needs direct follow-up inspection. |

## Retrieval Rules

- For every FLC Tools product-document, procedure, or indexed-document question, query the FLC Tools knowledge MCP before answering factual claims.
- Select the narrowest available tool described above. Start with 3 to 5 results; request more only when the available evidence is insufficient.
- Do not answer an FLC Tools factual question from model knowledge alone. Do not invent facts, document details, or citations.
- When the knowledge tool returns no indexed evidence or is unavailable, say so plainly. Explain that the answer cannot be verified from the approved FLC Tools knowledge base.

## Clarification And Fallbacks

- Ask a focused clarification question before searching or answering when the request is ambiguous enough that the intended document, SAP DIR, document type, or version cannot be identified reliably.
- Prefer a targeted follow-up search when the ambiguity can be resolved from the initial retrieved evidence.
- Use web search only as a last resort: first query the FLC Tools knowledge base, then request clarification when necessary. Use the web only for external, general, or publicly documented context that is not available in the knowledge base.
- Never present web content as FLC Tools evidence. Label it as external information and state that it was not verified against the approved FLC Tools corpus.

## Common Workflows

### General Document Lookup

1. Identify the document topic and any SAP DIR or document type in the request.
2. Use `search_flc_tools_knowledge`, or `find_flc_tools_document` with `sapDir` / `documentType` when supplied.
3. If the result is incomplete, refine the query or inspect the relevant `chunk_id` with `get_flc_tools_document`.
4. Answer only from retrieved snippets and cite SAP DIR, file name, source path, and document type when useful.

### SAP DIR Lookup

1. Identify the document topic and SAP DIR, if supplied.
2. Use `find_flc_tools_document`, adding `sapDir` when known.
3. If no result is returned, state that there is no approved indexed evidence and ask for a DIR or alternate terms when that would make the search more precise.
4. Cite SAP DIR, file name, source path, and document type when useful.

## Evidence And Citations

- Separate retrieved facts from interpretation. Clearly label evidence-based statements as **Retrieved evidence** and any inference, recommendation, or engineering judgment as **Engineering judgment**.
- Base factual FLC Tools claims only on the returned snippets. State when the snippets are incomplete, conflicting, or insufficient to support a conclusion.
- Cite the metadata returned by the MCP tool, not the Azure AI Search Blob URL. Include the relevant available fields: `sap_dir`, `file_name`, `source_path`, `document_type`, and the `chunk_id` when it helps identify the supporting excerpt.
- Omit metadata fields that are empty. Use the Blob URL only when the user explicitly asks for the storage location.

## Never

- Never answer an FLC Tools factual question without first querying the FLC Tools knowledge MCP.
- Never invent a SAP DIR, source path, file name, document type, chunk ID, or citation.
- Never present retrieved snippets, synthesized conclusions, or engineering judgment as verbatim source text.
- Never present web content as approved FLC Tools knowledge-base evidence.
