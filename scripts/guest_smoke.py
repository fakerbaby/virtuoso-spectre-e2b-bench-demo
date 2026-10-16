"""Create a fresh OA divider, export with Cadence SI, and simulate with Spectre."""
import datetime,hashlib,json,math,subprocess,re
from pathlib import Path
from virtuoso_bridge import VirtuosoClient
from virtuoso_bridge.spectre.runner import SpectreSimulator
stamp=datetime.datetime.now().strftime('%Y%m%dT%H%M%S%f');root=Path('/work/public-demo')/stamp;root.mkdir(parents=True)
report={'status':'RUNNING','scope':'Fresh analogLib divider, no PDK, no ADB grade'}
try:
 client=VirtuosoClient.local(timeout=60)
 def skill(code):
  r=client.execute_skill(code,timeout=60)
  if r.errors:raise RuntimeError(str(r.errors))
  return r.output.strip()
 assert skill('1+2')=='3';lib='demo_'+stamp
 assert skill(f'ddCreateLib("{lib}" "{root/lib}")')!='nil'
 with client.schematic.edit(lib,'divider') as sch:
  sch.add_instance('analogLib','vdc',(0,0),name='V0');sch.add_instance('analogLib','res',(3,0),name='R0');sch.add_instance('analogLib','res',(6,0),name='R1')
  for inst,plus,minus in [('V0','VDD','gnd!'),('R0','VDD','OUT'),('R1','OUT','gnd!')]:
   sch.add_net_label_to_instance_term(inst,'PLUS',plus);sch.add_net_label_to_instance_term(inst,'MINUS',minus)
 skill(f'_demoCv=dbOpenCellViewByType("{lib}" "divider" "schematic" nil "a")')
 for inst,param,value in [('V0','vdc','1'),('R0','r','1k'),('R1','r','1k')]:skill(f'cdfFindParamByName(cdfGetInstCDF(car(setof(i _demoCv~>instances i~>name=="{inst}"))) "{param}")~>value="{value}"')
 skill('schCheck(_demoCv)');skill('dbSave(_demoCv)');skill('dbClose(_demoCv)');assert (root/lib/'divider/schematic/sch.oa').is_file()
 (root/'cds.lib').write_text(f'DEFINE {lib} {root/lib}\nSOFTINCLUDE /eda/cadence/IC251/share/cdssetup/dfII/cds.lib\n')
 (root/'si.env').write_text(f'simLibName = "{lib}"\nsimCellName = "divider"\nsimViewName = "schematic"\nsimSimulator = "spectre"\nsimRunDir = "{root}"\nsimViewList = \'("spectre" "schematic")\nsimStopList = \'("spectre")\nhnlNetlistFileName = "netlist"\nsimNetlistHier = t\n')
 with (root/'export.log').open('w') as out:subprocess.run(['/eda/cadence/IC251/tools/dfII/bin/si','-batch','-command','nl',str(root)],cwd=root,stdout=out,stderr=subprocess.STDOUT,timeout=180,check=True)
 net=root/'netlist';assert net.is_file() and 'ERROR (' not in (root/'export.log').read_text()
 bench=root/'divider.scs';bench.write_text(f'simulator lang=spectre\ninclude "{net}"\ndcOp dc\nsave OUT\n')
 (root/'simulation').mkdir()
 result=SpectreSimulator.local(work_dir=root/'simulation',timeout=180,output_format='psfascii').run_simulation(bench,{})
 assert result.ok,result.errors;raw=list((root/'simulation').rglob('dcOp.dc'));assert len(raw)==1
 values=raw[0].read_text().split('\nVALUE\n',1)[1];voltage=float(re.search(r'^"OUT"\s+"[^"]*"\s+([-+0-9.eE]+)',values,re.M)[1]);assert math.isfinite(voltage) and abs(voltage-.5)<1e-5
 report.update(status='PASS',bridge=True,oa_saved=True,native_export=True,native_sha256=hashlib.sha256(net.read_bytes()).hexdigest(),spectre=True,divider_V=voltage,spectre_version=subprocess.check_output(['spectre','-W'],text=True).strip())
except Exception as e:report.update(status='FAIL',error_type=type(e).__name__,error=str(e))
(root/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));raise SystemExit(0 if report['status']=='PASS' else 1)
