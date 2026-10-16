"""Verify upstream task bytes and reject secret/vendor payloads before publishing."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def verify():
 p=json.loads((ROOT/'examples/adb/provenance.json').read_text());task=ROOT/'examples/adb'/p['task_id'];actual={str(x.relative_to(task)) for x in task.rglob('*') if x.is_file()}
 assert actual==set(p['files']),'Official task inventory changed'
 for n,h in p['files'].items():assert hashlib.sha256((task/n).read_bytes()).hexdigest()==h,n
 assert not (task/'solution').exists() and not (task/'results').exists()
 files=[]
 for f in ROOT.rglob('*'):
  rel=f.relative_to(ROOT)
  if not f.is_file() or any(x in {'.git','.venv','output','__pycache__'} for x in rel.parts):continue
  assert not f.is_symlink();assert f.suffix not in {'.lic','.key','.pem','.sqfs','.qcow2','.vhdx','.iso','.zip'},str(rel)
  assert not f.name.startswith('.env') or f.name=='.env.example',str(rel)
  b=f.read_bytes();assert not re.search(rb'(sk-[A-Za-z0-9]{20,}|e2b_[a-f0-9]{24,}|gh[pousr]_[A-Za-z0-9]{20,}|BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY)',b),str(rel)
  files.append(str(rel))
 return {'status':'PASS','upstream_task':p['task_id'],'upstream_commit':p['commit'],'upstream_files_verified':len(actual),'files_checked':len(files),'vendor_binaries_included':False,'credentials_included':False}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
