#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""固定提交远端逐字节核验；不运行任何模型或原生应用。"""
import concurrent.futures, datetime, hashlib, io, json, pathlib, subprocess, time, urllib.parse, urllib.request, zipfile
ROOT=pathlib.Path("/tmp/cma-web-delivery-20261006")
OUT=pathlib.Path(__file__).resolve().parent
COMMIT="c0f6fac62dd20fa5d14c94b57d53344628290b39"
PREFIX="review/20261007-cumulative-manuscript-v1"
files=subprocess.check_output(["git","-C",str(ROOT),"ls-tree","-r","--name-only",COMMIT,"--",PREFIX,"README.md"],text=True).splitlines()
DEST=OUT/"remote_download_c0f6fac"
DEST.mkdir(exist_ok=True)
def sha(b):return hashlib.sha256(b).hexdigest()
def fetch(name):
    expected=subprocess.check_output(["git","-C",str(ROOT),"show",COMMIT+":"+name])
    url="https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/"+COMMIT+"/"+urllib.parse.quote(name,safe="/")
    last=None
    for attempt in range(1,4):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"CMAverse-source-verification"})
            with urllib.request.urlopen(req,timeout=45) as r:
                status=r.status; data=r.read()
            assert status==200 and data==expected, name
            target=DEST/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
            return {"path":name,"url":url,"http_status":status,"bytes":len(data),"sha256":sha(data),"matches_commit_blob":True,"attempts":attempt}
        except Exception as e:
            last=e
            if attempt<3:time.sleep(1)
    raise RuntimeError(name+": "+repr(last))
rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    for future in concurrent.futures.as_completed([pool.submit(fetch,n) for n in files]):
        rows.append(future.result())
        if len(rows)%15==0:print("verified "+str(len(rows))+"/"+str(len(files)),flush=True)
payload=DEST/PREFIX
archive=(payload/"cumulative_review_part01.zip").read_bytes()
assert len(archive)==6037715 and sha(archive)=="a727e520e695f0a8b2044e3bc86ee87e6080508e9f9911c2c52da9af8e0dd035"
with zipfile.ZipFile(io.BytesIO(archive)) as z:
    assert len(z.namelist())==87 and z.testzip() is None
    manifest=json.loads(z.read("MANIFEST.json"));assert manifest["count"]==86
    assert set(z.namelist())=={x["path"] for x in manifest["files"]}|{"MANIFEST.json"}
    for row in manifest["files"]:
        data=z.read(row["path"])
        assert len(data)==row["bytes"] and sha(data)==row["sha256"]
        assert data==(payload/row["path"]).read_bytes()
verification=subprocess.run(["/opt/homebrew/opt/python@3.14/bin/python3.14","-B",str(payload/"verify_package.py")],text=True,capture_output=True)
assert verification.returncode==0, verification.stderr
portable=json.loads(verification.stdout)
receipt={"status":"REMOTE_VERIFIED","verified_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"repository":"https://github.com/lzhs1995/CMAverse-paper","artifact_commit":COMMIT,"published_files_verified":len(rows),"directory_files_verified":len(rows)-1,"root_readme_verified":True,"archive":{"bytes":len(archive),"sha256":sha(archive),"members":87,"manifest_covered":86,"crc":"PASS"},"remote_portable_verification":portable,"review_mode":"solo_self_review","native_status":"PENDING","models_executed":0,"files":sorted(rows,key=lambda x:x["path"])}
(OUT/"REMOTE_VERIFY_RECEIPT.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({k:v for k,v in receipt.items() if k!="files"},ensure_ascii=False),flush=True)

