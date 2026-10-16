"""Create an EDA sandbox, inject a runtime license, verify native OA/Spectre, clean up."""
import argparse,json,os
from pathlib import Path
from e2b import Sandbox
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--license-file',type=Path,required=True);p.add_argument('--keep',action='store_true');p.add_argument('--timeout',type=int,default=1800);p.add_argument('--report',type=Path,default=ROOT/'output/e2b-smoke.json');a=p.parse_args()
 key=os.environ.get('E2B_API_KEY');assert key,'Set E2B_API_KEY locally; never commit it'
 options=dict(api_key=key,api_url=os.environ.get('E2B_API_URL','http://hk-prod-e2b.xiaobei.top:3000'),domain=os.environ.get('E2B_DOMAIN','hk-prod-e2b.xiaobei.top:3002'),request_timeout=120)
 if os.environ.get('E2B_SANDBOX_URL'):options['sandbox_url']=os.environ['E2B_SANDBOX_URL']
 meta=json.loads((ROOT/'environment/template.json').read_text());license_data=a.license_file.read_bytes();assert license_data,'Empty license file';s=None;passed=False;r={'template_id':meta['template_id'],'scope':'Primitive analogLib OA/native-export/Spectre smoke; not an ADB score','status':'RUNNING'}
 try:
  s=Sandbox.create(meta['template_id'],timeout=a.timeout,metadata={'purpose':'public-demo-eda-smoke'},**options);r['sandbox_id']=s.sandbox_id
  options['headers']={'Host':'49983-'+s.sandbox_id+'.'+options['domain']};s=Sandbox.connect(s.sandbox_id,timeout=a.timeout,**options)
  s.commands.run('/opt/eda-bootstrap.sh',user='root',timeout=90)
  s.files.write('/opt/rocky/run/secrets/cadence.lic',license_data,user='root');del license_data
  s.commands.run('chmod 600 /opt/rocky/run/secrets/cadence.lic; mkdir -p /opt/rocky/work/public-demo',user='root',timeout=30)
  s.files.write('/opt/rocky/work/public-demo/guest_smoke.py',(ROOT/'scripts/guest_smoke.py').read_text(),user='root')
  z=s.commands.run('/opt/eda-bootstrap.sh /opt/venv/bin/python /work/public-demo/guest_smoke.py',user='root',timeout=600)
  r['stdout']=z.stdout;r['stderr']=z.stderr;r['exit_code']=z.exit_code;passed=z.exit_code==0;r['status']='PASS' if passed else 'FAIL'
 except Exception as error:
  r.update(status='ERROR',error_type=type(error).__name__,stdout=getattr(error,'stdout','').replace(key,'[REDACTED]'),stderr=getattr(error,'stderr','').replace(key,'[REDACTED]'));raise
 finally:
  if s and not (passed and a.keep):s.kill(**options);r['sandbox_destroyed']=True
  else:r['sandbox_destroyed']=False
  a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(r,indent=2)+'\n')
 if not passed:raise SystemExit(1)
 print(json.dumps({'status':r['status'],'report':str(a.report),'sandbox_id':r.get('sandbox_id'),'sandbox_destroyed':r['sandbox_destroyed']}))
if __name__=='__main__':main()
