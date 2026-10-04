from pathlib import Path
from PIL import Image,ImageDraw
import tempfile,copy
from 验证排版 import alternation_rules
with tempfile.TemporaryDirectory() as td:
 root=Path(td);pages=[];reports=[]
 for n in range(1,10):
  im=Image.new('RGB',(360,480),'black');dd=ImageDraw.Draw(im);dd.rectangle((20,20,46,67),fill='#23FE02');dd.rectangle((20,380,46,427),fill='#23FE02');im.save(root/f'p{n:02}.png')
  es=[{'kind':'text','text':'上方重音','font':'headline','fill':'#23FE02','size':100,'callout':True,'box':[.1,.05,.8,.1]},{'kind':'text','text':'下方白句','font':'serif-bold','fill':'#FFFFFF','size':100,'callout':True,'box':[.1,.65,.8,.1]},{'kind':'text','text':'[[名字]]','font':'body','fill':'#FFFFFF','accent':'#23FE02','size':58,'box':[.1,.85,.8,.1]}]
  pages.append({'layout':'story','elements':es});trs=[]
  for i,e in enumerate(es):trs.append({'text':e['text'],'box':e['box'],'glyphs':[{'char':'字','fill':'#23FE02' if i!=1 else '#FFFFFF','ink_bounds':[144,e['box'][1]*1920,240,e['box'][1]*1920+100]}]})
  reports.append({'page':n,'output_file':str(root/f'p{n:02}.png'),'text':trs})
 data={'config':{'accent':'#23FE02','secondary_accent':'#FF4D4D'},'pages':pages}
 assert alternation_rules(data,reports,root/'script.json',root)['passed']
 def check(d,rs,word):
  result=alternation_rules(d,rs,root/'script.json',root);assert any(word in e for e in result['errors']),result
 d=copy.deepcopy(data);d['pages'][0]['elements'][1]['fill']='#23FE02';check(d,reports,'相邻大字同类颜色')
 d=copy.deepcopy(data);rs=copy.deepcopy(reports);rs[0]['text'][0]['glyphs'][0]['fill']='#FFFFFF';check(d,rs,'上1/3缺少')
 d=copy.deepcopy(data);d['pages'][0]['elements'][2]['text']='没有着色';rs=copy.deepcopy(reports);rs[0]['text'][2]['glyphs'][0]['fill']='#FFFFFF';check(d,rs,'下1/3缺少')
 d=copy.deepcopy(data);d['pages'][0]['elements'][2]['text']='[[一个]][[两个]]';check(d,reports,'关键词2>1')
 d=copy.deepcopy(data);d['pages'][0]['elements'][2]['box']=[.1,.16,.8,.1];check(d,reports,'关键词紧挨绿色大字')
 d=copy.deepcopy(data);d['pages'][0]['elements'][1]['font']='headline';check(d,reports,'白色大字未用宋体700')
 d=copy.deepcopy(data);d['pages'][0]['elements'][0]['font']='serif-bold';check(d,reports,'强调色大字未用标题字体')
 print('PASS: color/white alternation, real glyph upper/lower zones, single keyword and adjacent color block rejection')
