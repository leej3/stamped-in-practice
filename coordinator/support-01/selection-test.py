from pathlib import Path
import types, unittest
p=Path(__file__).resolve().parent
m=types.ModuleType('support');m.__file__=str(p/'prepare.py')
exec(compile((p/'prepare.py').read_bytes(),m.__file__,'exec'),m.__dict__)
class SelectionTests(unittest.TestCase):
 def fixture(self):
  assigned=[{'run':'a','judgment':'a-j01','role':'primary'},{'run':'a','judgment':'a-j02','role':'duplicate'}]
  closures=[(Path(str(i)),{'preservation_complete':True,'judgments':[{'assignment':dict(a),'preservation_verified':True}]}) for i,a in enumerate(assigned)]
  return assigned,closures
 def test_both_slots_required(self):
  a,c=self.fixture();self.assertEqual(len(m.select_closed(a,c)),2)
  with self.assertRaises(ValueError):m.select_closed(a,c[:1])
 def test_duplicate_and_wrong_role_rejected(self):
  a,c=self.fixture()
  with self.assertRaises(ValueError):m.select_closed(a,c+c[:1])
  c[0][1]['judgments'][0]['assignment']['role']='duplicate'
  with self.assertRaises(ValueError):m.select_closed(a,c)
 def test_incomplete_and_empty_rejected(self):
  a,c=self.fixture();c[0][1]['judgments'][0]['preservation_verified']=False
  with self.assertRaises(ValueError):m.select_closed(a,c)
  with self.assertRaises(ValueError):m.select_closed([],c)
unittest.main(verbosity=2)
