# Number the ⟦doi:…⟧ / ⟦pmid:…⟧ tokens in order of first appearance and generate the
# reference list and hover popovers. Citation metadata is cached in .build/refs.json.
import re,json,time,html,urllib.request,urllib.parse
p='index.html'; s=open(p).read(); J='.build/refs.json'; M=json.load(open(J))
def get(u):
    for i in range(5):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"refs-fetch/1.0"}),timeout=30).read().decode())
        except Exception: time.sleep(3)
def fetch(k):
    if k.startswith('doi:'):
        m=(get("https://api.crossref.org/works/"+urllib.parse.quote(k[4:],safe='/')) or {}).get("message",{})
        au=[(a.get("family","")+" "+"".join(w[0] for w in re.split(r"[\s.-]+",a.get("given","")) if w)).strip() for a in m.get("author",[]) if a.get("family")]
        return dict(authors=au,title=(m.get("title") or [""])[0],journal=(m.get("container-title") or [""])[0],year=(m.get("issued",{}).get("date-parts") or [[None]])[0][0],volume=m.get("volume"),issue=m.get("issue"),pages=m.get("page"))
    x=get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id="+k[5:])["result"][k[5:]]
    return dict(authors=[a["name"] for a in x.get("authors",[])],title=x["title"].rstrip('.'),journal=x["fulljournalname"],year=int(x["pubdate"][:4]),volume=x.get("volume"),issue=x.get("issue"),pages=x.get("pages"))
order=[]
for k in re.findall(r'⟦([^⟧]+)⟧',s):
    if k not in order: order.append(k)
for k in order:
    if k not in M: M[k]=fetch(k); print('fetched',k,'|',M[k]['title'][:70]); time.sleep(0.7)
json.dump(M,open(J,'w'),ensure_ascii=False,indent=0)
def clean(t):
    t=html.unescape(re.sub(r'\s+',' ',t)).strip().rstrip('.')
    t=re.sub(r'<(?!/?i>)[^>]+>','',t).replace('( ','(').replace(' )',')')
    return t.replace('&','&amp;')
def au(v):
    a=v['authors']; return ', '.join(a[:3])+(', et al' if len(a)>3 else '')
def cite(k):
    v=M[k]; j=clean(v['journal']).split(': The Journal')[0]; vol=''
    if v.get('volume'): vol=f";{v['volume']}"+(f"({v['issue']})" if v.get('issue') else '')+(f":{v['pages']}" if v.get('pages') else '')
    elif v.get('pages'): vol=f":{v['pages']}"
    href='https://pubmed.ncbi.nlm.nih.gov/'+k[5:]+'/' if k.startswith('pmid:') else 'https://doi.org/'+k[4:]
    lab='PMID '+k[5:] if k.startswith('pmid:') else k
    return f"{au(v)+'. ' if au(v) else ''}{clean(v['title'])}. <i>{j}</i>. {v['year']}{vol}. <a href=\"{href}\">{lab}</a>"
def plain(k):
    v=M[k]; return html.escape(re.sub(r'<[^>]+>','',f"{au(v)}. {html.unescape(clean(v['title']))}. {html.unescape(clean(v['journal']))} {v['year']}."),quote=True)
def rep(m):
    n=order.index(m.group(1))+1
    return f'&#8288;<sup><a class="ref" href="#r{n}" interestfor="t{n}" title="{plain(m.group(1))}">[{n}]</a></sup>'
s=re.sub(r'\s*⟦([^⟧]+)⟧',rep,s)
refs='<h2>References</h2>\n<ol class="refs">\n'+"".join(f'<li id="r{i+1}">{cite(k)}</li>\n' for i,k in enumerate(order))+'</ol>\n\n'
tips="".join(f'<div class="tip" popover="hint" id="t{i+1}">{cite(k)}</div>\n' for i,k in enumerate(order))
s=s.replace('<footer>',refs+'<footer>',1).replace('</main>',tips+'</main>',1)
open(p,'w').write(s); print(len(order),'references built')
