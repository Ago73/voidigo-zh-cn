import json,re
d=json.load(open('extracted/zh_final_v10.json'));log=[]
ESS={'While on a run, get $20 kills$ with a \nweapon to unlock its essence.':'一局内用一把武器击杀$20次$，\n即可解锁它的精华。\n集齐精华可解开虚空之门锁链。',
'While on a run, $fully upgrade$ a \npowerup to unlock its essence.':'一局内把一个道具$升满级$，\n即可解锁它的精华。\n集齐精华可解开虚空之门锁链。',
'While on a run, $defeat a boss$ to \nunlock its essence.':'一局内$击败首领$，\n即可解锁它的精华。\n集齐精华可解开虚空之门锁链。',
"While on a run, $survive the Void$ to \nunlock your character's essence.":'一局内$在虚空中存活$，\n即可解锁角色的精华。\n集齐精华可解开虚空之门锁链。'}
for k,v in ESS.items(): log.append({'en':k,'context':'essence unlock condition; same string is shown by the camp essence pile tooltip (title + this text)','current':d[k],'final':v,'reason':'v10只显示第二行（见下条换行修复）；补全“集齐精华可解开虚空之门锁链”'}); d[k]=v
# $-tooltip renderer splits on spaces; a token containing \n keeps only text after \n. EN always writes " \n".
fixed=0
for k,v in d.items():
  if ' \n' in k and '\n' in v:
    nv=re.sub(r'(?<! )\n',' \n',v)
    if nv!=v: d[k]=nv;fixed+=1
json.dump(d,open('extracted/zh_final_v11_clean.json','w'),ensure_ascii=False,indent=0)
NB_BEFORE=set(map(chr,[0xFF0C,0x3002,0xFF01,0xFF1F,0x3001,0xFF1B,0xFF1A,0x201D,0x2019,0xFF09,0x300B,0x300D,0x300F,0x3011,0x3015,0x2026,0x2014,0xB7,0xFF05,0xFF0E,0x30FC]))|set(',.!?;:)%]}"\'')
NB_AFTER=set(map(chr,[0x201C,0x2018,0xFF08,0x300A,0x300C,0x300E,0x3010,0x3014]))|set('([{')
cjk=lambda c:'\u2e80'<=c<='\u9fff' or '\u3000'<=c<='\u303f' or '\uff00'<=c<='\uffef' or c in '“”‘’…—·'
Z='\u200b';n=0
def zw(s):
  o=[s[0]]
  for a,b in zip(s,s[1:]):
    if (cjk(a) or cjk(b)) and a not in ' \n$' and b not in ' \n$' and b not in NB_BEFORE and a not in NB_AFTER: o.append(Z)
    o.append(b)
  return ''.join(o)
for k,v in d.items():
  if len(v)>=16 and '$' not in v and ' \n' not in v: d[k]=zw(v);n+=1
json.dump(d,open('extracted/zh_final_v11.json','w'),ensure_ascii=False,indent=0)
json.dump(log,open('phase5/changes_v11.json','w'),ensure_ascii=False,indent=1)
print('space-fix',fixed,'zwsp entries',n)
