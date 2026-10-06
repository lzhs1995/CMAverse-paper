#!/usr/bin/env python3
"""用 Python 标准库核验本增量包；不执行模型或解压覆盖文件。"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import zipfile


def verify(path):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        assert len(names) == len(set(names)), 'duplicate ZIP member'
        assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names), 'unsafe member'
        assert z.testzip() is None, 'ZIP CRC failure'
        manifest = json.loads(z.read('MANIFEST.json'))
        entries = manifest['files']
        assert set(names) == {e['path'] for e in entries} | {'MANIFEST.json'}, 'manifest coverage mismatch'
        parsed = {'json': 0, 'csv': 0, 'docx': 0}
        for e in entries:
            data = z.read(e['path'])
            assert len(data) == e['bytes'], e['path'] + ': size'
            assert hashlib.sha256(data).hexdigest() == e['sha256'], e['path'] + ': SHA256'
            if e['path'].endswith('.json'):
                json.loads(data); parsed['json'] += 1
            elif e['path'].endswith('.csv'):
                list(csv.reader(io.StringIO(data.decode('utf-8-sig')))); parsed['csv'] += 1
            elif e['path'].endswith('.docx'):
                from xml.etree import ElementTree
                with zipfile.ZipFile(io.BytesIO(data)) as doc:
                    assert doc.testzip() is None
                    for name in doc.namelist():
                        if name.endswith(('.xml', '.rels')):
                            ElementTree.fromstring(doc.read(name))
                parsed['docx'] += 1
        acceptance = json.loads(z.read('ACCEPTANCE.json'))
        candidate = next(n for n in names if n.startswith('manuscript/') and n.endswith('.docx') and '/sources/' not in n)
        assert hashlib.sha256(z.read(candidate)).hexdigest() == acceptance['candidate_sha256']
        predecessors = [n for n in names if n.startswith('manuscript/sources/') and n.endswith('.docx')]
        numeric = next(n for n in predecessors if '数值收尾合入' in n)
        with zipfile.ZipFile(io.BytesIO(z.read(candidate))) as current, zipfile.ZipFile(io.BytesIO(z.read(numeric))) as old:
            assert set(current.namelist()) == set(old.namelist())
            changed = sorted(n for n in current.namelist() if current.read(n) != old.read(n))
            assert changed == ['word/document.xml'], changed
        return {'status': 'PASS', 'zip': str(path.resolve()), 'bytes': path.stat().st_size,
                'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'members': len(names), 'payload_hashes_verified': len(entries),
                'crc': 'PASS', 'manifest_self_excluded': True, 'parsed': parsed,
                'candidate_sha256': acceptance['candidate_sha256'],
                'docx_parts_changed': changed,
                'scope': 'File integrity, parsing, and offline DOCX part comparison; not model execution or native Word/PDF QA.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('zip', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = verify(args.zip)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.write_text(rendered, encoding='utf-8')
    print(rendered, end='')
