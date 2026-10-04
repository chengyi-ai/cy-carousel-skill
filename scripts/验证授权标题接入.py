"""只用内置OFL字体当技术夹具；不放商业字库、不保存图。"""
import warnings,tempfile
from pathlib import Path
from render import FONT_ROOT,resolved_font,load_font,TITLE_FONT_KEYS

def regression():
 p=FONT_ROOT/'NotoSerifSC[wght].ttf';cfg={'fonts':{'licensed_headline':{'path':str(p),'weight':600}}}
 for key in TITLE_FONT_KEYS:
  face,info=resolved_font(key,80,cfg)
  assert not info['fallback'] and info['weight']==600 and info['source']=='licensed_headline'
  assert bytes(face.getmask('字'))==bytes(load_font(str(p),80,0,600).getmask('字'))
 assert resolved_font('body',80,cfg)[1]['weight']==500
 with tempfile.TemporaryDirectory() as td:
  with warnings.catch_warnings(record=True) as warnings_seen:
   warnings.simplefilter('always')
   for key in TITLE_FONT_KEYS:
    _,info=resolved_font(key,80,{'fonts':{'licensed_headline':{'path':str(Path(td)/'missing.ttf')}}})
    assert info['fallback'] and info['weight']==700 and '不存在' in info['error']
   assert warnings_seen
 for setting in [{'path':str(p),'index':-1},{'path':str(p),'weight':1200},{'path':str(FONT_ROOT/'MaShanZheng-Regular.ttf'),'weight':700}]:
  with warnings.catch_warnings():
   warnings.simplefilter('ignore');assert resolved_font('heading',80,{'fonts':{'licensed_headline':setting}})[1]['fallback']
 print('PASS: 三标题key/正文不变/缺文件与index或weight错误明确回退；无商业字库')
if __name__=='__main__':regression()
