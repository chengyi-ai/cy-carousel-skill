"""浅篇路径正反例：不是靠换tone标签或有档案便放宽其他硬规则。"""
from pathlib import Path
import tempfile,json,copy
from PIL import Image,ImageDraw
from render import render,draw_text,processed_image,normalize_tone
from 验证背景 import background_rules,tone_rules
assert normalize_tone('light')=='浅' and normalize_tone('dark')=='暗'
with tempfile.TemporaryDirectory() as td:
 root=Path(td);Image.new('RGB',(300,400),'#C9BAA5').save(root/'photo.jpg')
 config={'background':'#F3EDE2','tone':'light','accent':'#9E2632'}
 t={'kind':'text','text':'浅底正文','box':[.05,.1,.8,.09],'size':50,'lineheight':70,'font':'body','fill':'#161616','bg':'#FAF6EE'}
 page={'layout':'story','watermark':False,'elements':[{'kind':'image','path':'photo.jpg','source_id':'one','box':[0,0,1,1],'fit':'cover','role':'background'},t]}
 def check(p):
  data={'tone':'light','config':config,'pages':[p]};s=root/'s.json';s.write_text(json.dumps(data));rs=render(s,root/'out');bg=background_rules(data,rs,s,root/'out');tone=tone_rules(data,rs,s,root/'out',bg);return bg,tone
 assert all(v['passed'] for v in check(page))
 for color in ['#FFF3A3','#80F0F5','#FFFFFF']:
  p=copy.deepcopy(page);p['elements'][1]['bg']=color;assert check(p)[0]['passed']
 p=copy.deepcopy(page);p['elements'][1]['bg']='#999999';assert not check(p)[0]['passed']
 p=copy.deepcopy(page);p['elements'][1]['fill']='#FFFFFF';assert not check(p)[1]['passed']
 p=copy.deepcopy(page);p['elements'][0]['darken']=.6;assert not check(p)[1]['passed']
 ink=Image.new('RGBA',(1440,1920));audit=[];draw_text(ink,{'text':'清晰标题','box':[.1,.1,.8,.12],'font':'headline','fill':'#9E2632','size':100,'effect':'3d'},config,1440,1920,audit)
 a=audit[0];assert a['depth']==1 and a['shadow_color']=='#D4CDBF' and a['soft_shadow']['blur']==2 and a['soft_shadow']['opacity']==.12
 # 同步裁切mask：左半透明、右半人物。若把完整mask缩放到右半裁片，左边会错误变透明。
 Image.new('RGB',(200,200),'#FFFFFF').save(root/'source.png');mask=Image.new('L',(200,200));ImageDraw.Draw(mask).rectangle((100,0,199,199),fill=255);mask.save(root/'mask.png')
 result=processed_image({'path':'source.png','mask':'mask.png','crop':[.5,0,1,1],'fit':'cover'},root,(100,200),config)
 assert result.getchannel('A').getextrema()==(255,255)
print('PASS：light/dark别名，浅色白/黄/青黑字贴条，灰卡/白正文/暗图负例，浅灰轻影默认，源图与人物mask同步裁切。')

# 完整浅篇检查及反例由调用者提供的独立样稿驱动，避免静默跳过不存在的项目文件。
from 浅色排版 import blank_paper,light_editorial_rules
assert blank_paper(Image.new('RGB',(1440,1920),'#F3EDE2'))==1
