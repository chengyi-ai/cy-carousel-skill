"""色调规则正反例：全黑合法，亮照片不等于浅色平涂，纸张不能插进暗篇。"""
from pathlib import Path
import tempfile,json,copy
from PIL import Image
from render import render
from 验证背景 import background_rules,tone_rules

with tempfile.TemporaryDirectory() as td:
 root=Path(td);Image.new('RGB',(300,400),'#AF8B71').save(root/'photo.jpg')
 def check(pages,tone='暗',config=None):
  data={'tone':tone,'config':config or {},'pages':copy.deepcopy(pages)}
  path=root/'s.json';path.write_text(json.dumps(data));rs=render(path,root/'pages')
  return tone_rules(data,rs,path,root/'pages'),background_rules(data,rs,path,root/'pages')
 black={'layout':'story','watermark':False,'elements':[]}
 paper={**black,'background':'#F1EADD','elements':[{'kind':'text','text':'黑字正文','box':[.1,.1,.8,.15],'font':'body','fill':'#151515','size':50}]}
 assert not check([black,paper])[0]['passed']
 assert not check([paper,black],'浅')[0]['passed']
 assert check([paper,paper],'浅')[0]['passed']
 assert not check([black],'混搭')[0]['passed']
 tone,bg=check([black]*9,config={'has_archive_content':True})
 assert tone['passed'] and bg['passed'] and bg['counts']['black']==9 and bg['longest_black_run']==9
 full={**black,'elements':[{'kind':'image','path':'photo.jpg','source_id':'photo','box':[0,0,1,1],'fit':'cover','role':'background'}]}
 assert check([full],'暗')[0]['passed'] and check([full],'浅')[0]['passed']
 assert check([{**full,'background':'#F1EADD'}],'暗')[0]['passed'] # 完全被照片遮住的底色不是浅色页。
 dark=copy.deepcopy(full);dark['elements'][0]['darken']=.56
 assert check([dark],'暗')[0]['passed'] and not check([dark],'浅')[0]['passed']
 fake=copy.deepcopy(full);fake['elements'].append({'kind':'rect','box':[0,0,1,1],'fill':'#F1EADD'})
 assert not check([fake],'暗')[0]['passed'] # 黑底声明或照片标签不能隐藏实际平涂。
 override=copy.deepcopy(black);override['tone']='浅';assert not check([override],'暗')[0]['passed']
 print('PASS：暗篇拒绝纸张/浅色平涂；浅篇拒绝黑/暗图；整版亮照片允许；整篇全黑与档案无需纸张；真实可见平涂/页面tone覆盖拒绝。')
