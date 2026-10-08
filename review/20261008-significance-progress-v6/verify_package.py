#!/usr/bin/env python3
# 完整性校验；不执行统计、DOCX宏或包内其他代码。
from pathlib import Path, PurePosixPath
import hashlib, io, json, sys, zipfile
zpath=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name("significance_progress_part01.zip")
with zipfile.ZipFile(zpath) as z:
    names=z.namelist()
    assert len(names)==len(set(names)), "duplicate ZIP entries"
    assert all(not PurePosixPath(n).is_absolute() and ".." not in PurePosixPath(n).parts for n in names), "unsafe path"
    assert z.testzip() is None, "CRC mismatch"
    m=json.loads(z.read("MANIFEST.json"))
    assert set(names)==set(x["path"] for x in m["files"])|{"MANIFEST.json"}, "member set mismatch"
    for f in m["files"]:
        b=z.read(f["path"])
        assert len(b)==f["bytes"] and hashlib.sha256(b).hexdigest()==f["sha256"], f["path"]
        if f["path"].endswith(".docx"):
            with zipfile.ZipFile(io.BytesIO(b)) as doc: assert doc.testzip() is None, f["path"]
print(json.dumps({"status":"PASS","members":len(names),"files_checked":len(m["files"]),"bytes":zpath.stat().st_size,"sha256":hashlib.sha256(zpath.read_bytes()).hexdigest(),"statistics_executed":False},ensure_ascii=False))
