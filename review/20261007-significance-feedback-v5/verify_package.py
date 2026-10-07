from pathlib import Path
import hashlib, json, zipfile
root = Path(__file__).resolve().parent
manifest = json.loads((root / 'MANIFEST.json').read_text())
for row in manifest['files']:
    p = root / row['path']
    data = p.read_bytes()
    assert len(data) == row['bytes'], row['path']
    assert hashlib.sha256(data).hexdigest() == row['sha256'], row['path']
    if p.suffix == '.docx':
        with zipfile.ZipFile(p) as z:
            assert z.testzip() is None, row['path']
print(json.dumps({'status': 'PASS', 'verified_files': len(manifest['files']), 'scope': 'Integrity and DOCX CRC only; no statistical execution'}))
