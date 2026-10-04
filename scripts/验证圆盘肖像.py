"""合成alpha夹具检查四向出圆与露盘；没有项目肖像依赖。"""
import tempfile
from pathlib import Path
from PIL import Image,ImageDraw
from render import disc_portrait

def regression():
 with tempfile.TemporaryDirectory() as td:
  root=Path(td);figure=Image.new('RGBA',(100,420));d=ImageDraw.Draw(figure)
  d.ellipse((24,8,76,64),fill='red');d.polygon([(30,60),(70,60),(90,140),(72,410),(28,410),(10,140)],fill='red')
  for direction in ('top','bottom','left','right'):
   p=root/(direction+'.png');(figure.rotate(90,expand=True) if direction in ('left','right') else figure).save(p)
   e={'cutout_path':str(p),'source_id':'synthetic-alpha','center':[.5,.5],'radius':160,'breakout':30,'breakout_direction':direction}
   _,_,_,r=disc_portrait(e,root,1440,1920,{'accent':'#FD3AAC'})
   assert r['disc_visible_ratio']>=.4 and r['actual_outside_pixels']>0 and not r['outline']
  p=root/'opaque.png';Image.new('RGB',(100,420),'red').save(p)
  try:disc_portrait({**e,'cutout_path':str(p)},root,1440,1920,{'accent':'#FD3AAC'})
  except ValueError:pass
  else:raise AssertionError('不透明照片被当成抠图')
  p=root/'broad.png';broad=Image.new('RGBA',(400,450),(255,0,0,255));broad.putpixel((0,0),(0,0,0,0));broad.save(p)
  try:disc_portrait({**e,'cutout_path':str(p),'breakout_direction':'top','portrait_radius':220},root,1440,1920,{'accent':'#FD3AAC'})
  except ValueError as exc:assert '圆盘可见面积' in str(exc)
  else:raise AssertionError('遮盘超过60%未拒绝')
 print('PASS: 四向出圆、露盘≥40%、不透明图及过量遮挡拒绝')
if __name__=='__main__':regression()
