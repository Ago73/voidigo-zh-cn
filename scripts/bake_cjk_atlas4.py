# bake_cjk_atlas4.py KIND PATH SIZE OUTDIR [PAD]  KIND=tt|pcf ; 1-bit, exact cells, PAD gutter
import sys,os,numpy as np;sys.path.insert(0,os.path.dirname(__file__));from fontsrc import *
from PIL import Image
K,P,S,OUT=sys.argv[1:5];PAD=int(sys.argv[5]) if len(sys.argv)>5 else 2;os.makedirs(OUT,exist_ok=True)
f=PCF(P) if K=='pcf' else TT(P,int(S))
chars=sorted({c for c in open('extracted/cjk_charset.txt',encoding='utf-8').read() if ord(c)>0x7e and not c.isspace()})
miss=[c for c in chars if not f.has(c)];chars=[c for c in chars if f.has(c)]
G={c:f.get(c) for c in chars}
rows=np.zeros(f.H,bool)
for a,_ in G.values(): rows|=a.any(1)
r=np.where(rows)[0];T,B=r.min(),r.max()+1;H=B-T
W=1024;x=y=PAD;pl=[]
for c in chars:
  a,adv=G[c];c_=np.where(a.any(0))[0];w=max(adv,(c_.max()+1) if len(c_) else 1)
  if x+w+PAD>W: x=PAD;y+=H+2*PAD
  pl.append((c,x,y,w,adv));x+=w+2*PAD
m=np.zeros((y+H+PAD,W),np.uint8)
for c,gx,gy,w,adv in pl: m[gy:gy+H,gx:gx+w]=G[c][0][T:B,:w]*255
with open(OUT+'/cjk_glyphs.tsv','w') as o:
  for c,gx,gy,w,adv in pl: o.write(f"{ord(c)}\t{gx}\t{gy}\t{w}\t{H}\t{adv}\t0\n")
img=Image.new('RGBA',(W,m.shape[0]),(255,255,255,0));img.putalpha(Image.fromarray(m));img.save(OUT+'/cjk_atlas.png')
print(OUT,len(pl),img.size,'H',H,'missing',''.join(miss))
