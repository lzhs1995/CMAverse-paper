"""Verify package members; optionally run 41 offline recovery tests."""
from pathlib import Path
import hashlib,json,subprocess,sys
root=Path(__file__).resolve().parent
manifest=json.loads((root/'MANIFEST.json').read_text())
actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
expected={r['path'] for r in manifest['files']}|{'MANIFEST.json'}
assert actual==expected,('FILE_SET_MISMATCH',actual^expected)
for r in manifest['files']:
 p=root/r['path'];b=p.read_bytes()
 assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'],r['path']
print('PASS: '+str(len(manifest['files']))+' manifest entries')
if '--tests' in sys.argv:
 subprocess.run([sys.executable,'-B',str(root/'code/run_tests.py')],check=True)

