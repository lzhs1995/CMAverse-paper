"""Run unchanged recovery tests with the pinned read-only broker fixture."""
from pathlib import Path
import hashlib, importlib.util, runpy, sys
ROOT = Path(__file__).resolve().parent
broker = ROOT / 'reference_broker.py'
assert hashlib.sha256(broker.read_bytes()).hexdigest() == '27039b5941598825c928a2a4647cabb87d890f96ef2704461df5725e35762974'
spec = importlib.util.spec_from_file_location('resource_broker', broker)
module = importlib.util.module_from_spec(spec)
sys.modules['resource_broker'] = module
spec.loader.exec_module(module)
sys.path.insert(0, str(ROOT))
runpy.run_path(str(ROOT / 'test_recovery.py'), run_name='__main__')

