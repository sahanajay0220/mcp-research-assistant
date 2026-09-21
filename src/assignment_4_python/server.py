# The @mcp.tool(), @mcp.resource(), and @mcp.prompt() decorator pattern used
# in this file follows the one shown in the official MCP Python SDK
# documentation and examples: https://github.com/modelcontextprotocol/python-sdk

from mcp.server.mcpserver import MCPServer
from database import get_connection, validate_citation_input, InvalidInputError, logger

mcp = MCPServer("Research Assistant")

FAKE_PAPER_DATABASE = [
    {"title": "Attention Is All You Need", "author": "Vaswani et al.", "year": 2017, "topic": "transformers"},
    {"title": "Deep Residual Learning for Image Recognition", "author": "He et al.", "year": 2015, "topic": "neural networks"},
    {"title": "A Few Useful Things to Know About Machine Learning", "author": "Domingos", "year": 2012, "topic": "machine learning"},
    {"title": "Generative Adversarial Networks", "author": "Goodfellow et al.", "year": 2014, "topic": "neural networks"},
]


@mcp.tool()
def search_papers(query: str) -> list[dict]:
    """Search for academic papers matching a topic (demo data, not a live API)."""
    query_lower = query.lower()
    results = [p for p in FAKE_PAPER_DATABASE if query_lower in p["topic"].lower() or query_lower in p["title"].lower()]
    return results


@mcp.tool()
def add_citation(title: str, author: str, year: int) -> dict:
    """Save a paper to the bibliography."""
    try:
        validate_citation_input(title, author, year)
    except InvalidInputError as e:
        return {"status": "error", "message": str(e)}

    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO citations (title, author, year) VALUES (?, ?, ?)",
            (title, author, year),
        )
        conn.commit()
        conn.close()
        return {"status": "success", "citation": {"title": title, "author": author, "year": year}}
    except Exception as e:
        logger.error("add_citation failed: %s", e, exc_info=True)
        return {"status": "error", "message": "Could not save citation due to an internal error. Please try again."}

@mcp.resource("bibliography://all")
def all_citations() -> str:
    """All saved citations, one per line."""
    conn = get_connection()
    rows = conn.execute("SELECT title, author, year FROM citations").fetchall()
    conn.close()
    if not rows:
        return "No citations saved yet."
    lines = [f"{r['author']} ({r['year']}). {r['title']}." for r in rows]
    return "\n".join(lines)


@mcp.prompt()
def research_helper(topic: str) -> str:
    """Guide the model to search for papers and save good ones."""
    return (
        f"Search for academic papers about '{topic}' using search_papers. "
        "Then, for any papers that seem genuinely relevant, use add_citation "
        "to save them to the bibliography. Finally, summarize what you found."
    )

if __name__ == "__main__":
    mcp.run(transport="stdio")
