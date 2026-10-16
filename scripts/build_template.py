"""Derive a software-only private template from an existing authorized EDA base."""
import argparse,json,os,time,urllib.request
from e2b import Template

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',default='epwak9ve48ho1nu75llo');p.add_argument('--alias',required=True);p.add_argument('--dry-run',action='store_true');a=p.parse_args()
 recipe='test -x /opt/eda-bootstrap.sh && test -f /opt/cadence-full-runtime.sqfs && test ! -e /opt/rocky/run/secrets/cadence.lic'
 if a.dry_run:print(json.dumps({'base':a.base,'alias':a.alias,'cpu':4,'memory_mb':4096,'recipe':recipe,'api_called':False},indent=2));return
 key=os.environ['E2B_API_KEY'];url=os.environ.get('E2B_API_URL','http://hk-prod-e2b.xiaobei.top:3000');opts=dict(api_key=key,api_url=url,request_timeout=120)
 template=Template().from_template(a.base).run_cmd(recipe,user='root');b=Template.build_in_background(template,a.alias,cpu_count=4,memory_mb=4096,**opts)
 req=urllib.request.Request(url+'/templates/'+b.template_id,data=b'{"public":false}',headers={'X-API-Key':key,'Content-Type':'application/json'},method='PATCH')
 with urllib.request.urlopen(req,timeout=60) as r:assert r.status<300
 for _ in range(360):
  r=Template.get_build_status(b,**opts);status=r.status.value if hasattr(r.status,'value') else str(r.status)
  if status.lower()=='ready':print(json.dumps({'template_id':b.template_id,'alias':a.alias,'build_id':b.build_id,'private':True,'status':'READY'}));return
  if status.lower()=='error':raise RuntimeError('Template build failed; inspect authenticated E2B build logs')
  time.sleep(5)
 raise TimeoutError('Template build timed out')
if __name__=='__main__':main()
