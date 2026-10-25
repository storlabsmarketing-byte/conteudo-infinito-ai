"""No-AI integration check. Validates a synthetic, unpublished bundle through OIDC."""
import base64, datetime as dt, io, json, pathlib, urllib.request
from PIL import Image
from delivery import SITE,AUDIENCE,json_request,oidc,state
def main():
    status=state()
    if not status.get("enabled"):raise ValueError("Site import is disabled")
    post={"slug":"verificacao-editorial-nao-publicar","title":"Verificação técnica da integração",
      "excerpt":"Pacote sintético de validação. Não publicar.","seoTitle":"Verificação da integração editorial",
      "metaDescription":"Verificação técnica da conexão entre GitHub e blog, com imagens e metadados para validar o fluxo de importação sem publicar um artigo no site do Espúrio.",
      "author":"O Espúrio","category":"Teste","status":"published","publishedAt":dt.datetime.now(dt.timezone.utc).isoformat(),
      "body":[{"type":"paragraph","text":"Investidor Legionário, pacote técnico sem publicação."},
              {"type":"link","text":"Espelho Financeiro","href":SITE+"/gestao-financeira"},
              {"type":"link","text":"Fonte de teste","href":"https://www.bcb.gov.br"},
              {"type":"link","text":"Fonte de teste","href":"https://www.ibge.gov.br"}]}
    # Existing public editorial images are reused only in this non-publishing check.
    files=[("capa","/blog/credito-facil-pode-comprometer-investimentos/capa.jpg"),
           ("imagem-1","/blog/superavit-2027-governo-novos-gastos-conta-fecha/orcamento.jpg"),
           ("imagem-2","/blog/superavit-2027-governo-novos-gastos-conta-fecha/investimentos.jpg")]
    assets=[]
    for name,source in files:
        with urllib.request.urlopen(SITE+source,timeout=30) as response:raw=response.read(1500000)
        with Image.open(io.BytesIO(raw)) as im:
            im=im.convert("RGB");im.thumbnail((1600,1600));buf=io.BytesIO();im.save(buf,format="JPEG",quality=78,optimize=True);width,height=im.size
        path="/blog/"+post["slug"]+"/"+name+".jpg"
        assets.append({"path":path,"data":base64.b64encode(buf.getvalue()).decode(),"mime":"image/jpeg"})
        block={"src":path,"width":width,"height":height,"alt":"Ilustração gerada por IA para validação técnica"}
        if name=="capa":post["cover"]=block
        else:post["body"].append({"type":"image",**block,"caption":"Ilustração gerada por IA. Pacote de validação sem publicação."})
    result=json_request(AUDIENCE+"/validate",{"post":post,"assets":assets},
       {"Authorization":"Bearer "+oidc(),"Content-Type":"application/json"})
    if result.get("status")!="validated":raise ValueError("Integration did not validate")
    print("GitHub OIDC identity, public Site reads, image loading and authenticated validation succeeded. No content published.")
if __name__=="__main__":main()
