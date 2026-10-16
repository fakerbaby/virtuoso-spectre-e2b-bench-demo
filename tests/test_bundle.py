import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from verify_bundle import verify
from run_adb import commands
class BundleTests(unittest.TestCase):
 def test_upstream_bytes_and_publish_payload(self):self.assertEqual(verify()['status'],'PASS')
 def test_verifier_does_not_mount_reference_or_credentials(self):
  c=commands(Path('/tmp/candidate.spi'),Path('/tmp/results'));flat=' '.join(c[1]);self.assertIn('--network none',flat);self.assertIn('dst=/app/circuit.spi,readonly',flat);self.assertNotIn('/solution',flat);self.assertNotIn('E2B_API_KEY',flat)
 def test_starter_is_not_misrepresented_as_reference_solution(self):
  p=json.loads((ROOT/'examples/adb/provenance.json').read_text());self.assertFalse(p['reference_solution_included']);self.assertFalse(p['reference_results_included'])
 def test_pinned_simulator_image_matches_in_both_containers(self):
  p=ROOT/'examples/adb/sky130-ota-5t-gain40-pm60-noise50uv-pvt';a=(p/'environment/Dockerfile').read_text().splitlines()[0];b=next(x for x in (p/'tests/Dockerfile').read_text().splitlines() if x.startswith('FROM '));self.assertEqual(a,b);self.assertIn('@sha256:',a)
if __name__=='__main__':unittest.main()
