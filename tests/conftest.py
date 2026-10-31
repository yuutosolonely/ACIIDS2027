"""Keep temporary test artifacts inside this project, avoiding shared OS temp state."""
from pathlib import Path
from uuid import uuid4

def pytest_configure(config):
    if config.option.basetemp is None:
        root=Path(__file__).resolve().parents[1]
        target=(root/'.cache/pytest'/uuid4().hex).resolve()
        if not target.is_relative_to(root):
            raise ValueError('Test temporary directory must stay within project')
        target.parent.mkdir(parents=True,exist_ok=True)
        config.option.basetemp=str(target)
