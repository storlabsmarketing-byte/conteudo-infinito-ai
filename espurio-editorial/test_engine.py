import importlib.util, pathlib, unittest, copy
spec=importlib.util.spec_from_file_location("engine",pathlib.Path(__file__).with_name("engine.py"))
engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
class Validation(unittest.TestCase):
 def sample(self):
  return {"post":{"slug":"tema-original","title":"Tema original","excerpt":"Resumo",
   "seoTitle":"Tema original","metaDescription":"a"*150,
   "body":[{"type":"paragraph","text":"Investidor Legionário, exemplo educativo."},
           {"type":"link","text":"Conheça","href":engine.CTA}]},
   "sources":[{"url":"https://www.bcb.gov.br","facts":["Fato A"]},
              {"url":"https://www.ibge.gov.br","facts":["Fato B"]}],
   "visuals":[{"role":"cover"},{"role":"inline"},{"role":"inline"}]}
 def test_preserves_draft_and_brand(self):
  p=engine.validate(self.sample(),[])
  self.assertEqual(p["post"]["status"],"draft")
  self.assertEqual(p["post"]["author"],"O Espúrio")
 def test_rejects_duplicate_slug(self):
  with self.assertRaises(ValueError):
   engine.validate(self.sample(),[{"title":"Outro","url":"https://oespurio.com.br/blog/tema-original"}])
 def test_rejects_missing_cta(self):
  p=self.sample();p["post"]["body"].pop()
  with self.assertRaises(ValueError):engine.validate(p,[])
 def test_rejects_missing_evidence(self):
  p=self.sample();p["sources"]=[]
  with self.assertRaises(ValueError):engine.validate(p,[])
if __name__=="__main__":unittest.main()
