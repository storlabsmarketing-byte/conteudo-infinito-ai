"""Image generation and GitHub OIDC publication. No permanent Site credential."""
import base64, io, json, os, pathlib, urllib.request
from PIL import Image, ImageOps
SITE="https://oespurio.com.br"
AUDIENCE=SITE+"/api/blog/editorial"
def json_request(url, body=None, headers=None):
    raw=None if body is None else json.dumps(body).encode()
    with urllib.request.urlopen(urllib.request.Request(url,data=raw,headers=headers or {}),timeout=180) as r:
        return json.load(r)
def state():
    return json_request(AUDIENCE+"/state")
def oidc():
    request_url=os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"]+"&audience="+urllib.parse.quote(AUDIENCE,safe="")
    return json_request(request_url,headers={"Authorization":"Bearer "+os.environ["ACTIONS_ID_TOKEN_REQUEST_TOKEN"]})["value"]
def image(prompt,reference=None):
    from engine import API,request_json
    parts=[{"text":prompt}]
    if reference:
        parts.append({"inlineData":{"mimeType":"image/jpeg","data":base64.b64encode(reference).decode()}})
    model=os.environ.get("ESPURIO_IMAGE_MODEL","gemini-2.5-flash-image")
    if not __import__("re").fullmatch("[a-zA-Z0-9._-]+",model):raise ValueError("Invalid image model")
    data=request_json(API+model+":generateContent",
        {"contents":[{"role":"user","parts":parts}],
         "generationConfig":{"responseModalities":["TEXT","IMAGE"]}},
        {"Content-Type":"application/json","x-goog-api-key":os.environ["GEMINI_API_KEY"]})
    for candidate in data.get("candidates",[]):
        for part in candidate.get("content",{}).get("parts",[]):
            asset=part.get("inlineData") or part.get("inline_data")
            if asset:
                raw=base64.b64decode(asset["data"],validate=True)
                if len(raw)>18000000:raise ValueError("Image too large")
                with Image.open(io.BytesIO(raw)) as source:
                    source=ImageOps.fit(source.convert("RGB"),(1600,900))
                    for quality in [86,80,72,64]:
                        out=io.BytesIO();source.save(out,format="JPEG",quality=quality,optimize=True)
                        if len(out.getvalue())<=350000:return out.getvalue()
                raise ValueError("Cannot optimize image")
    raise ValueError("Image provider returned no image")
def build_bundle(package,out):
    post=package["post"]
    import datetime as dt
    post["status"]="published";post["publishedAt"]=dt.datetime.now(dt.timezone.utc).isoformat()
    covers=[v for v in package["visuals"] if v.get("role")=="cover"]
    inline=[v for v in package["visuals"] if v.get("role")=="inline"]
    if len(covers)!=1 or len(inline)!=2:raise ValueError("Invalid visual roles")
    reference_url=SITE+"/blog/credito-facil-pode-comprometer-investimentos/capa.jpg"
    with urllib.request.urlopen(reference_url,timeout=30) as r:reference=r.read(1500000)
    assets=[]
    def make(v,name,reference=None):
        path="/blog/"+post["slug"]+"/"+name+".jpg"
        prompt=str(v.get("prompt",""))
        if name=="capa":
            prompt+="\nCapa 16:9 seguindo exatamente formato e moeda do modelo de referencia, serifas douradas e gradiente inferior. Substitua fotografia e todos os textos pelo tema do artigo: "+post["title"]+". Use titulo curto adequado ao tema, sem repetir credito facil nem anos. Sem marcas, sem emojis. Preserve margens e legibilidade."
        else:prompt+="\nFotografia conceitual editorial 16:9, sem textos, sem marcas, sem icones, sem simular registro de acontecimento real."
        raw=image(prompt,reference)
        (out/(name+".jpg")).write_bytes(raw)
        assets.append({"path":path,"mime":"image/jpeg","data":base64.b64encode(raw).decode()})
        return {"src":path,"width":1600,"height":900,"alt":str(v.get("alt") or "Ilustração editorial")+" Ilustração gerada por IA."}
    post["cover"]=make(covers[0],"capa",reference)
    original=post["body"];insertions={}
    for i,v in enumerate(inline,1):
        block={"type":"image",**make(v,"imagem-"+str(i)),
               "caption":str(v.get("caption") or "Planejamento financeiro.")+" Ilustração gerada por IA."}
        matches=[n for n,b in enumerate(original) if b.get("type")=="heading" and b.get("text")==v.get("afterHeading")]
        index=(matches[0]+1) if matches else max(1,len(original)*i//3)
        insertions.setdefault(index,[]).append(block)
    body=[]
    for n,b in enumerate(original):
        body.extend(insertions.get(n,[]));body.append(b)
    body.extend(insertions.get(len(original),[]));post["body"]=body
    return {"post":post,"assets":assets}
def deliver(package,out,mode):
    bundle=build_bundle(package,out)
    (out/"bundle.json").write_text(json.dumps(bundle,ensure_ascii=False),encoding="utf-8")
    # Validate first. Obtain a fresh OIDC token again before the actual write.
    headers=lambda:{"Authorization":"Bearer "+oidc(),"Content-Type":"application/json"}
    validated=json_request(AUDIENCE+"/validate",bundle,headers())
    if validated.get("status")!="validated":raise ValueError("Site rejected validation")
    if mode=="verify":
        (out/"result.json").write_text(json.dumps(validated),encoding="utf-8")
        print("External generation, images and authenticated Site validation succeeded. No article published.")
        return
    result=json_request(AUDIENCE+"/publish",bundle,headers())
    if result.get("status") not in ("published","already-published"):raise ValueError("Publication unconfirmed")
    url=result.get("url","")
    if not url.startswith(SITE+"/blog/"):raise ValueError("Invalid publication URL")
    # Read back the persisted article and all image responses before reporting success.
    with urllib.request.urlopen(url,timeout=30) as r:
        html=r.read().decode()
    if post_slug(bundle) not in html or "/gestao-financeira" not in html or "blog-article-site" not in html:
        raise ValueError("Published page verification failed")
    for asset in bundle["assets"]:
        with urllib.request.urlopen(SITE+asset["path"],timeout=30) as r:
            if r.headers.get_content_type()!="image/jpeg":raise ValueError("Image readback failed")
    for path in ["/blog/feed.xml","/sitemap.xml"]:
        with urllib.request.urlopen(SITE+path,timeout=30) as r:
            if post_slug(bundle) not in r.read().decode():raise ValueError("Discovery readback failed")
    (out/"result.json").write_text(json.dumps(result),encoding="utf-8")
    print(result["status"]+": "+url)
def post_slug(bundle):return bundle["post"]["slug"]
