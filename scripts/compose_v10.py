import numpy as np,struct,pefile,hashlib
IB=0x400000;R=0x4197000;S=0x3f2a800
P=[(392,7),(840,10),(868,4),(56549952,5),(56602438,1),(56603644,6),(56604280,6),(56709477,1),(56709979,3),(56713748,6),(56907856,5),(56918805,18),(58382192,126)]
old=np.fromfile('/tmp/v4/base_old.exe',np.uint8);new=np.fromfile('/tmp/v4/base_v10.exe',np.uint8)
z=bytearray(open('extracted/voidigo.exe.zh12','rb').read())
d=np.nonzero(old[:S]!=new[:S])[0];d=d[d>=0x1000]
for a,l in P: assert not ((d>=a)&(d<a+l)).any(),('overlap',a)
z[:S]=bytes(z[:S]); zz=np.frombuffer(z,np.uint8).copy(); zz[d]=new[d]; z=bytearray(zz.tobytes())
pn=pefile.PE('/tmp/v4/base_v10.exe',fast_load=True);sn=pn.sections[-1]
blob=bytes(new[sn.PointerToRawData:sn.PointerToRawData+sn.Misc_VirtualSize])
pz=pefile.PE(data=bytes(z),fast_load=True);sz=pz.sections[-1]
zsec=bytes(z[sz.PointerToRawData:sz.PointerToRawData+0x1be00])
L=blob.rfind(b'\0',0,0x1bc00)+1;SH=0x1be00-L
sec=bytearray(blob[:L])+bytearray(0x1bc00-L)+zsec[0x1bc00:0x1be00]+blob[L:]
# refs: dwords in new body pointing into blob that changed vs old
lo,hi=IB+R,IB+R+len(blob);refs=[]
cand=set()
for p in d:
  for q in range(p-3,p+1): cand.add(int(q))
for q in sorted(cand):
  v=struct.unpack_from('<I',new,q)[0]
  if lo<=v<hi and struct.unpack_from('<I',old,q)[0]!=v: refs.append((q,v))
refs=sorted(set(refs))
for q,v in refs:
  if v-lo>=L: struct.pack_into('<I',z,q,v+SH)
vs=len(sec);raw=(vs+0x1ff)&~0x1ff;sec+=bytearray(raw-vs)
z=z[:sz.PointerToRawData]+sec
pz=pefile.PE(data=bytes(z),fast_load=True);s=pz.sections[-1]
s.Misc_VirtualSize=vs;s.SizeOfRawData=raw;pz.OPTIONAL_HEADER.SizeOfImage=(R+vs+0xfff)&~0xfff
z=bytearray(pz.write());struct.pack_into('<I',z,pz.OPTIONAL_HEADER.get_file_offset()+64,0)
pz=pefile.PE(data=bytes(z),fast_load=True);pz.OPTIONAL_HEADER.CheckSum=pz.generate_checksum();z=pz.write()
for a,l in P: assert z[a:a+l]==open('extracted/voidigo.exe.zh12','rb').read()[a:a+l] or a<0x1000
bad=0
def cs(b,o): e=b.index(b'\0',o); return b[o:e]
base=S
for q,v in refs:
  t=struct.unpack_from('<I',z,q)[0]-lo
  if cs(z,base+t)!=cs(blob,v-lo): bad+=1
assert zsec[0x1bc00:0x1be00]==z[base+0x1bc00:base+0x1be00]
open('extracted/voidigo.exe.zh12v10','wb').write(z)
print('refs',len(refs),'bad',bad,'L',hex(L),'vs',hex(vs),hashlib.sha256(z).hexdigest().upper(),len(z))
