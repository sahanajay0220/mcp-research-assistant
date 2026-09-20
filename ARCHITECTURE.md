# Architecture

```mermaid
flowchart TD
    A[Claude Desktop<br/>MCP client] -->|stdio / JSON-RPC| B

    subgraph B[server.py - MCP server]
        C[Tools:<br/>search_papers, add_citation]
        D[Resource:<br/>bibliography://all]
        E[Prompt:<br/>research_helper]
        C --> F[Validation +<br/>safe error handling]
        D --> F
        E --> F
    end

    F --> G[(citations.db<br/>SQLite, parameterized queries)]
    F -.->|on unexpected error| H[server_errors.log<br/>server-side only]
```

**Flow summary**

1. Claude Desktop connects to `server.py` over stdio using the MCP protocol.
2. Tool calls, resource reads, and the prompt template all pass through one shared validation and error-handling layer before touching data.
3. Validated input reaches `citations.db` through parameterized SQL queries only.
4. Any unexpected failure is logged privately to `server_errors.log` and never shown to the user in detail.