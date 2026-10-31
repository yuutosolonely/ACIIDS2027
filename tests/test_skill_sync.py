from pathlib import Path
import pytest
from sync_skills import synchronize

def test_sync_preserves_unmanaged_files_and_blocks_local_edits(tmp_path):
    source=tmp_path/'.agents/skills/example/SKILL.md'
    source.parent.mkdir(parents=True); source.write_text('canonical',encoding='utf-8')
    assert synchronize(tmp_path)
    mirror=tmp_path/'.claude/skills/example/SKILL.md'
    extra=mirror.parent/'personal.txt'; extra.write_text('keep',encoding='utf-8')
    source.write_text('next',encoding='utf-8'); assert synchronize(tmp_path)
    assert mirror.read_text(encoding='utf-8')=='next' and extra.read_text()=='keep'
    mirror.write_text('local edit',encoding='utf-8')
    source.write_text('changed again',encoding='utf-8')
    with pytest.raises(ValueError): synchronize(tmp_path)
    assert mirror.read_text(encoding='utf-8')=='local edit'
    assert not synchronize(tmp_path,check=True)
