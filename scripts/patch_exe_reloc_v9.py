#!/usr/bin/env python3
"""Relocating patcher: zh strings go into new section .zhstr; abs32 (HIGHLOW-reloc'd) and rip refs rewritten."""
import pefile,pickle,struct,json,sys,hashlib
sys.path.insert(0,'scripts')
from patch_exe_fast import index_strings
SRC='extracted/voidigo.exe.vanilla';DST=sys.argv[2] if len(sys.argv)>2 else 'extracted/voidigo.exe.zh'
MAP=sys.argv[1] if len(sys.argv)>1 else 'extracted/zh_final.json'
raw=open(SRC,'rb').read()
pe=pefile.PE(SRC,fast_load=True);pe.parse_data_directories(directories=[5]);IB=pe.OPTIONAL_HEADER.ImageBase
def o2r(o):
  for s in pe.sections:
    if s.PointerToRawData<=o<s.PointerToRawData+s.SizeOfRawData: return o-s.PointerToRawData+s.VirtualAddress
zh=json.load(open(MAP))
idx=index_strings(raw,0,len(raw))
want={}  # rva -> (en,zh,off,blen)
NEW=set(json.load(open('phase3/v9_new_keys.json')))
for en,z in zh.items():
  hs=idx.get(en,[]);lo_=61200000 if en in NEW else 62500000
  cat=[h for h in hs if lo_<=h[0]<=62899000]
  for off,bl in (cat or hs): want[o2r(off)]=(en,z,off,bl)
refs={}
for b in pe.DIRECTORY_ENTRY_BASERELOC:
  for e in b.entries:
    if e.type==3:
      o=pe.get_offset_from_rva(e.rva);v=struct.unpack_from('<I',raw,o)[0]-IB
      if v in want: refs.setdefault(v,[]).append(('abs32',o))
for v,l in pickle.load(open('/tmp/refs2.pkl','rb')).items():
  for r in l:
    pass  # x86 (32-bit) binary: no RIP-relative refs
# new section
last=pe.sections[-1];FA=pe.OPTIONAL_HEADER.FileAlignment;SA=pe.OPTIONAL_HEADER.SectionAlignment
al=lambda x,a:(x+a-1)//a*a
new_rva=al(last.VirtualAddress+last.Misc_VirtualSize,SA);new_off=al(last.PointerToRawData+last.SizeOfRawData,FA)
assert new_off==len(raw)
blob=bytearray();pos={}
for v,(en,z,off,bl) in want.items():
  if v in refs and z not in pos:
    pos[z]=len(blob);blob+=z.encode()+b'\0'
data=bytearray(raw)
rel=inpl=trunc=0;flags=[];rep=[]
for v,(en,z,off,bl) in want.items():
  if v in refs:
    nv=IB+new_rva+pos[z]
    for r in refs[v]:
      if r[0]=='abs32': struct.pack_into('<I',data,r[1],nv)
      else:
        o=r[1];prva=o2r(o);d=(new_rva+pos[z])-(prva+4+r[2]);struct.pack_into('<i',data,o,d)
    rel+=1;rep.append((en,z,'reloc',len(refs[v])))
  else:
    b=z.encode()
    if len(b)<=bl:
      data[off:off+bl]=b+b' '*(bl-len(b));inpl+=1;rep.append((en,z,'inplace',0))
    else:
      trunc+=1;flags.append((en,z,bl))  # left English, no truncation
# section header
hdr_off=pe.sections[-1].get_file_offset()+40
assert hdr_off+40<=pe.OPTIONAL_HEADER.SizeOfHeaders and not any(raw[hdr_off:hdr_off+40])
vs=len(blob);rs=al(vs,FA)
sh=struct.pack('<8sIIIIIIHHI',b'.zhstr\0\0',vs,new_rva,rs,new_off,0,0,0,0,0x40000040)
data[hdr_off:hdr_off+40]=sh
nso=pe.DOS_HEADER.e_lfanew+6
struct.pack_into('<H',data,nso,pe.FILE_HEADER.NumberOfSections+1)
soi=pe.OPTIONAL_HEADER.get_file_offset()+56
struct.pack_into('<I',data,soi,al(new_rva+vs,SA))
data+=blob+b'\0'*(rs-vs)
p2=pefile.PE(data=bytes(data),fast_load=True)
ck=p2.generate_checksum();struct.pack_into('<I',data,pe.OPTIONAL_HEADER.get_file_offset()+64,ck)
open(DST,'wb').write(data)
s={'relocated':rel,'inplace':inpl,'left_english_too_long':trunc,'truncated':0,'section_bytes':vs,'sha256':hashlib.sha256(data).hexdigest(),'size':len(data)}
print(json.dumps(s));json.dump({'summary':s,'flags':flags,'entries':rep},open('extracted/reloc_report.json','w'),ensure_ascii=False,indent=1)
