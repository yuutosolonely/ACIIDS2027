"""Mirror canonical project skills without overwriting local edits or deleting extras."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parent.parent

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def synchronize(root=ROOT, check=False):
    root = Path(root).resolve()
    src, dst = root/'.agents/skills', root/'.claude/skills'
    manifest = root/'docs/SKILL_MIRROR_MANIFEST.json'
    old = json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else {}
    files = {p.relative_to(src).as_posix():p for p in src.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    changes = []
    for name,p in files.items():
        q = dst/name
        if q.exists() and digest(q) != digest(p):
            if not check and old.get(name) != digest(q):
                raise ValueError(f'Mirror has unowned/local changes: {name}; reconcile manually.')
            changes.append(name)
        elif not q.exists():
            changes.append(name)
    if check:
        return not changes
    # Preflight all conflicts before any writes. Unmanaged extra files are preserved.
    for name in changes:
        q = dst/name
        q.parent.mkdir(parents=True, exist_ok=True)
        q.write_bytes(files[name].read_bytes())
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps({name:digest(p) for name,p in files.items()}, indent=2)+'\n',encoding='utf-8')
    return True

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    a=parser.parse_args()
    ok=synchronize(check=a.check)
    print('Skill mirror: MATCH' if ok else 'Skill mirror: DIFFERENT')
    raise SystemExit(0 if ok else 1)
