"""验证清晰版B与v7.1实际墨迹排距；保留历史压距参数的兼容测试。"""
from pathlib import Path
from PIL import Image,ImageChops,ImageFont
from render import draw_text,font,FONT_ROOT,FONTS

cfg={'accent':'#23FE02'}
base={'text':'立体','box':[.1,.1,.6,.2],'font':'headline','size':120,'spacing':0,'fill':'#23FE02'}
def paint(extra):
 im=Image.new('RGBA',(1440,1920));audit=[];draw_text(im,{**base,**extra},cfg,1440,1920,audit);return im,audit[0]
expected=ImageFont.truetype(str(FONT_ROOT/'MaShanZheng-Regular.ttf'),120)
for name in ['headline','cover-title','heading']:
 assert FONTS[name][2] is None and bytes(font(name,120,{}).getmask('做'))==bytes(expected.getmask('做'))
face,_=paint({'stroke':1})
zero,_=paint({'effect':'3d','depth':0,'soft_shadow':{'opacity':0}})
assert ImageChops.difference(face,zero).getbbox() is None,'字面不是同色1px加粗'
solid,a=paint({'effect':'3d','soft_shadow':{'opacity':0}})
x0,y0,x1,y1=face.getbbox();sx0,sy0,sx1,sy1=solid.getbbox()
assert (sx0,sy0)==(x0,y0) and (sx1,sy1)==(x1+7,y1+7),'默认挤出方向/厚度不对'
assert sum(px==(12,12,12,255) for px in solid.get_flattened_data())>100
assert a['bold']==1 and a['external_outline'] is False
soft,b=paint({'effect':'3d'})
assert b['soft_shadow']=={'color':'#000000','offset':[6,7],'blur':5,'opacity':110/255}
assert sum(0<px[3]<120 for px in soft.get_flattened_data())>sum(0<px[3]<120 for px in solid.get_flattened_data())+500
base['text']='前：后'
normal,n=paint({'effect':'3d','depth':0,'tight_punctuation':False,'punctuation_shift':0,'soft_shadow':{'opacity':0}})
compact,c=paint({'effect':'3d','depth':0,'tight_punctuation':False,'soft_shadow':{'opacity':0}})
assert abs(c['compact_punctuation_advances']['：']-120*.65)<.01
assert abs(normal.getbbox()[2]-compact.getbbox()[2]-42)<=1,'冒号后整行未收回0.35em'
assert normal.getbbox()[1:4:2]==compact.getbbox()[1:4:2],'压距改变了垂直基线'
base['font']='serif-bold'
normal,n=paint({'effect':'3d','depth':0,'soft_shadow':{'opacity':0}})
assert not n['compact_punctuation_advances'] and n['font_file']['weight']==700
base['font']='brush'
wide,_=paint({'effect':'3d','tight_punctuation':False,'soft_shadow':{'opacity':0}})
tight,t=paint({'effect':'3d','tight_punctuation':True,'soft_shadow':{'opacity':0}})
assert tight.getbbox()[2]<wide.getbbox()[2]-60 and t['compact_punctuation_advances']['：']<40
base['text']='甲·乙';_,r=paint({'effect':'3d'})
assert r['fallback_characters']==['·']
base.update(font='headline',size=100,box=[.05,.05,.9,.75])
base['text']='“甲”‘乙’丙。丁，戊、己？庚！辛…壬：癸\n“清晰可见。”\n“新的\n死亡之舞。”'
_,optical=paint({'effect':'3d'})
assert optical['tight_punctuation']=='all' and optical['punctuation_shift']==0
assert len(optical['punctuation_gaps'])>=25
assert all(0<=v['gap_em']<=.2 for v in optical['punctuation_gaps']),'标点与相邻墨迹空白超过0.2em'
assert all(abs(v['gap_em']-.1)<.001 for v in optical['punctuation_gaps']),'未按实际墨迹保持0.1em'
_,legacy=paint({'effect':'3d','tight_punctuation':False})
assert any(v['adjacent_han'] and v['gap_em']>.2 for v in legacy['punctuation_gaps']),'检查没有发现旧版标点空隙'
assert optical['fallback_characters']==[]
print('PASS：清晰B字库/1px/7层/柔影；旧0.35em及colon兼容；新标点按实际墨迹0.1em；旧版大空隙负例被发现；缺字补字可核。')
