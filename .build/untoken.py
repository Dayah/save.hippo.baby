# Turn the built page back into editable source: numbered superscripts become ⟦doi:…⟧ tokens,
# and the generated reference list and popovers are removed. Run build.py to regenerate them.
import re
p='index.html'; s=open(p).read()
key={}
for n,href in re.findall(r'<li id="r(\d+)">.*?<a href="([^"]+)">[^<]*</a></li>',s):
    key[n]='pmid:'+href.rstrip('/').split('/')[-1] if 'pubmed' in href else 'doi:'+href.split('doi.org/')[1]
s=re.sub(r'&#8288;<sup><a class="ref" href="#r(\d+)"[^>]*>\[\d+\]</a></sup>',lambda m:'⟦'+key[m.group(1)]+'⟧',s)
a=s.index('<h2>References</h2>'); b=s.index('<footer>'); s=s[:a]+s[b:]
s=re.sub(r'<div class="tip" popover="hint" id="t\d+">.*?</div>\n','',s)
open(p,'w').write(s); print(len(key),'refs untokenised')
