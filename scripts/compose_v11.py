import struct,pefile,hashlib,sys
IB=0x400000;R=0x4197000;S=0x3f2a800
P=[(392,7),(840,10),(868,4),(56549952,5),(56602438,1),(56603644,6),(56604280,6),(56709477,1),(56709979,3),(56713748,6),(56907856,5),(56918805,18),(58382192,126)]
NEW=sys.argv[1];OUT=sys.argv[2]
new=open(NEW,'rb').read();zh=open('extracted/voidigo.exe.zh12','rb').read();van=open('extracted/voidigo.exe.vanilla','rb').read()
z=bytearray(zh[:0x1000])+bytearray(new[0x1000:S])
for a,l in P:
  if a>=0x1000:
    assert new[a:a+l]==van[a:a+l],('new touches patch range',a); z[a:a+l]=zh[a:a+l]
pn=pefile.PE(NEW,fast_load=True);pn.parse_data_directories(directories=[5]);sn=pn.sections[-1]
assert sn.PointerToRawData==S and sn.VirtualAddress==R
blob=new[S:S+sn.Misc_VirtualSize]
pz=pefile.PE(data=zh,fast_load=True);sz=pz.sections[-1]
code=zh[sz.PointerToRawData+0x1bc00:sz.PointerToRawData+0x1be00]
L=blob.rfind(b'\0',0,0x1bc00)+1;SH=0x1be00-L
sec=bytearray(blob[:L])+bytearray(0x1bc00-L)+bytearray(code)+blob[L:]
lo,hi=IB+R,IB+R+len(blob);refs=[]
for b in pn.DIRECTORY_ENTRY_BASERELOC:
  for e in b.entries:
    if e.type==3:
      o=pn.get_offset_from_rva(e.rva)
      if o>=S: continue
      v=struct.unpack_from('<I',new,o)[0]
      if lo<=v<hi: refs.append((o,v))
for q,v in refs:
  if v-lo>=L: struct.pack_into('<I',z,q,v+SH)
# helper: break only at space or U+200B (ZWSP inserted at legal CJK break points)
h=sec.find(bytes.fromhex('83f820745e3d802e0000'));assert h==0x1bc00,hex(h)
sec[h+5:h+14]=bytes.fromhex('3d0b20000074'+'57'+'eb58')
vs=len(sec);raw=(vs+0x1ff)&~0x1ff;sec+=bytearray(raw-vs)
z=z+sec
pz=pefile.PE(data=bytes(z),fast_load=True);s=pz.sections[-1]
s.Misc_VirtualSize=vs;s.SizeOfRawData=raw;pz.OPTIONAL_HEADER.SizeOfImage=(R+vs+0xfff)&~0xfff
z=bytearray(pz.write());struct.pack_into('<I',z,pz.OPTIONAL_HEADER.get_file_offset()+64,0)
pz=pefile.PE(data=bytes(z),fast_load=True);pz.OPTIONAL_HEADER.CheckSum=pz.generate_checksum();z=pz.write()
bad=0
cs=lambda b,o:b[o:b.index(b'\0',o)]
for q,v in refs:
  t=struct.unpack_from('<I',z,q)[0]-lo
  if cs(z,S+t)!=cs(blob,v-lo): bad+=1
open(OUT,'wb').write(z)
print('refs',len(refs),'bad',bad,'L',hex(L),'vs',hex(vs),hashlib.sha256(z).hexdigest().upper(),len(z))
