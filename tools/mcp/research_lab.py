"""Read-oriented ACIIDS literature MCP server. No paid-run tools."""
from pathlib import Path
import sys
import tomllib
from mcp.server import MCPServer

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import litlib

mcp=MCPServer('aciids-lab')

@mcp.tool()
def lit_search(query: str, limit: int = 10, year_from: int = 2023, sources: str = 's2,openalex,arxiv') -> dict:
    """Search public academic topics. Never provide private manuscript text."""
    if not 1 <= limit <= 30:
        raise ValueError('limit must be 1..30')
    requested=tuple(s.strip() for s in sources.split(','))
    if not set(requested) <= {'s2','openalex','arxiv'}:
        raise ValueError('Unknown literature source')
    return litlib.search(query,limit,year_from or None,requested)

@mcp.tool()
def paper_details(paper_id: str) -> dict:
    """Fetch public paper metadata; does not validate scientific claims."""
    return litlib.paper_details(paper_id)

@mcp.tool()
def verify_reference(doi: str = '', arxiv: str = '', title: str = '', year: int = 0) -> dict:
    """Verify identifier/title/year identity, not venue acceptance or claim support."""
    return litlib.verify(doi or None,arxiv or None,title or None,year or None)

@mcp.tool()
def research_status() -> dict:
    """Return local project scope without network, secrets, hardware probing or paid work."""
    with (ROOT/'tools/mcp/lab_config.toml').open('rb') as f:
        cfg=tomllib.load(f)
    return {'project':cfg['project'],'compute':cfg['compute'],
            'stage':'setup-and-literature; no benchmark results',
            'state_path':'docs/STATE.md','working_directory':str(ROOT)}

if __name__ == '__main__':
    mcp.run()
