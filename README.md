# Research Assistant MCP Server

An MCP (Model Context Protocol) server for the **Academic Research** domain,
built with the [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk).

## What it exposes

| Type     | Name                  | Description                                                        |
|----------|------------------------|---------------------------------------------------------------------|
| Tool     | `search_papers`        | Search a small demo set of papers by keyword.                       |
| Tool     | `add_citation`         | Save a paper (title, author, year) to a persistent bibliography.    |
| Resource | `bibliography://all`   | Read-only view of every saved citation.                             |
| Prompt   | `research_helper`      | Template guiding the model to search for papers and save good ones. |

## Security best practices

1. **Input Sanitization** — every SQL query uses parameterized `?` placeholders
   (see `database.py`), and citation fields are validated (length limits, type
   checks) before ever reaching the database. See `tests/test_security.py`
   for a proof-of-concept SQL injection attempt that is safely neutralized.
2. **Error Disclosure control** — unexpected errors (e.g. a locked database
   file) are caught and logged in full detail to a local `server_errors.log`
   file, while the user only ever sees a generic, safe error message. See
   `tests/test_security.py` for a proof-of-concept forced failure.

## Setup

```bash
uv sync
```

## Run the tests (proves both security protections work)

```bash
uv run python tests\test_security.py
```

You should see two lines starting with `PASSED:`.

## Run the server standalone (for development)

```bash
uv run mcp dev src\assignment_4_python\server.py
```

This opens the MCP Inspector, a browser-based tool for manually testing tools,
resources, and prompts without needing Claude Desktop.

## Connect to Claude Desktop

1. Copy the contents of `claude_desktop_config.json` (in this repo) into your
   Claude Desktop config file, adjusting the paths to match where you've
   placed this project on your own machine.
2. Fully quit and reopen Claude Desktop.
3. Check **Settings → Developer** — `research-assistant` should show "Running".

## Project layout

```
assignment 4 python/
├── src/assignment_4_python/
│   ├── server.py       # MCP wiring: tools, resource, prompt
│   └── database.py     # SQLite access, validation, safe error handling
├── tests/
│   └── test_security.py  # Exploit attempts + proof they're blocked
├── requirements.txt
├── claude_desktop_config.json
└── README.md
```
## Claude Sonnet was used for this coding assignment.
