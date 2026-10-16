"""Run the unchanged official ADB verifier in a separate pinned Docker image."""
import argparse,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def commands(candidate,output):
 task=ROOT/'examples/adb/sky130-ota-5t-gain40-pm60-noise50uv-pvt'
 image='virtuoso-spectre-adb-example-verifier:972f7cd'
 return [['docker','build','-t',image,str(task/'tests')],['docker','run','--rm','--network','none','--cpus','4','--memory','4g','--mount','type=bind,src='+str(candidate)+',dst=/app/circuit.spi,readonly','--mount','type=bind,src='+str(output)+',dst=/logs/verifier',image,'sh','/tests/test.sh']]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,default=ROOT/'output/adb');p.add_argument('--dry-run',action='store_true');a=p.parse_args();c=a.candidate.resolve();out=a.output.resolve();assert c.is_file(),'Candidate must exist'
 cmds=commands(c,out)
 if a.dry_run:print(json.dumps({'commands':cmds,'simulation_started':False},indent=2));return
 out.mkdir(parents=True,exist_ok=True)
 if any(out.iterdir()):raise SystemExit('Use a new empty output directory; stale reward files are rejected')
 for cmd in cmds:subprocess.run(cmd,check=True)
 reward=out/'reward.json'
 if not reward.is_file():raise SystemExit('Verifier did not produce reward.json')
 print(reward.read_text())
if __name__=='__main__':main()
