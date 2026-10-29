"""Static setup validation; intentionally does not certify research results."""
from pathlib import Path
import ast
import hashlib
import json
import tomllib
import yaml
from sync_skills import synchronize

ROOT=Path(__file__).resolve().parent.parent

def main():
    required=['AGENTS.md','CLAUDE.md','README.md','uv.lock','docs/STATE.md','docs/IDEA.md',
      'docs/AUTHORIZATION.md','docs/experiment-plan.md','docs/related-work.md','docs/BRAINSTORM.md',
      'docs/context/conference/POLICIES.md','docs/context/conference/DATES.md','docs/CLAIM_EVIDENCE.md']
    for name in required:
        if not (ROOT/name).is_file(): raise ValueError('Missing: '+name)
    for pattern in ['.codex/**/*.toml','tools/**/*.toml','pyproject.toml']:
        for p in ROOT.glob(pattern): tomllib.loads(p.read_text(encoding='utf-8'))
    for name in ['.mcp.json','.agents/mcp_config.json','.claude/settings.json']:
        json.loads((ROOT/name).read_text(encoding='utf-8'))
    for folder in ['tools','src','tests']:
        for p in (ROOT/folder).rglob('*.py'): ast.parse(p.read_text(encoding='utf-8'))
    with (ROOT/'tools/mcp/lab_config.toml').open('rb') as f: cfg=tomllib.load(f)
    assert cfg['project']['idea']=='CRIC-ED'
    assert cfg['compute']['paid_compute_authorized'] is False
    for p in (ROOT/'.codex/agents').glob('*.toml'):
        d=tomllib.loads(p.read_text(encoding='utf-8'))
        assert all(d.get(k) for k in ['name','description','developer_instructions']),p
    local_skills=[]
    for p in (ROOT/'.agents/skills').glob('*/SKILL.md'):
        body=p.read_text(encoding='utf-8'); header=body.split('---',2)[1]
        d=yaml.safe_load(header)
        assert d['name']==p.parent.name and d['description'],p
        local_skills.append(d['name'])
    for p in (ROOT/'.agents/rules').glob('*.md'):
        d=yaml.safe_load(p.read_text(encoding='utf-8').split('---',2)[1])
        assert d['trigger'] in ['always_on','glob','manual','model_decision'],p
    agents=list((ROOT/'.agents/agents').glob('*.md'))
    assert len(agents)==7, f'Expected 7 Antigravity role agents, found {len(agents)}'
    for p in agents:
        d=yaml.safe_load(p.read_text(encoding='utf-8').split('---',2)[1])
        assert d.get('name')==p.stem and d.get('description'),p
        assert d.get('mainAgent') is True and d.get('subagent') is False,p
        for skill in d.get('skills',[]):
            assert skill.startswith('skills/') and (ROOT/'.agents/skills'/skill[len('skills/'):]/'SKILL.md').is_file(),(p,skill)
    assert synchronize(check=True),'Skill mirror differs'
    sources=json.loads((ROOT/'docs/context/SOURCE_MANIFEST.json').read_text(encoding='utf-8'))
    for item in sources['files']:
        assert hashlib.sha256((ROOT/item['destination']).read_bytes()).hexdigest()==item['sha256'],item
    locked=json.loads((ROOT/'docs/SKILLS_LOCK.json').read_text(encoding='utf-8'))
    for name,h in locked['files_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    print(json.dumps({'static_setup':'PASS','skills':sorted(local_skills),'source_snapshots':len(sources['files']),
        'research_results':'NOT_RUN','paid_compute':'NOT_AUTHORIZED'},ensure_ascii=False))

if __name__=='__main__': main()
