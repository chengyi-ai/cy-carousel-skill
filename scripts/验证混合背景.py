from pathlib import Path
import tempfile,json
from PIL import Image
from 图像等比 import ratio_audit,cover_cell,fit_geometry
from 保脸裁切 import local_faces,safe_focus
from render import dark_backdrop,processed_image,render,watermark_layer
from 验证背景 import backdrop_rules,background_rules,geometry_rules

try:ratio_audit((200,300),(300,300),'bad-stretch')
except ValueError:pass
else:raise AssertionError('拉伸未拒绝')
for size in [(300,500),(900,1600),(1440,1920)]:
 a=[];pic=cover_cell(Image.new('RGB',size,'#F0A020'),(360,480),a,face_boxes=[])
 assert pic.size==(360,480) and a[0]['aspect_error_ratio']<.01 and not a[0]['black_padding'] and pic.getpixel((0,0))==(240,160,32)
print('PASS: 拒绝>1%拉伸；3:5/9:16/3:4格子cover等比无黑边')
faces=[{'id':0,'box':[10,400,100,490]}];focus,r=safe_focus((300,500),(360,480),faces,(.5,.35));assert r['retained_face_ids']==[0] and not r['partial_face_ids']
try:local_faces({'face_boxes':[[.1,.3,.4,.4]],'crop':[0,.4,1,1]},(100,100),(100,60))
except ValueError:pass
else:raise AssertionError('crop截脸未拒绝')
print('PASS: Vision框驱动focus；显式crop截断人脸拒绝')
with tempfile.TemporaryDirectory() as td:
 root=Path(td);Image.new('RGB',(600,500),'#AC9270').save(root/'photo.jpg');e={'kind':'dark_backdrop','path':'photo.jpg','source_id':'test','box':[0,.2,1,.4],'fit':'cover','darken':.6,'fade_fraction':.25}
 im,r=dark_backdrop(e,root,1440,1920,{'accent':'#FD3AAC'});assert im.getchannel('A').getpixel((720,0))==0 and im.getchannel('A').getpixel((720,767))==0 and r['fade_pixels_each']==192
 for bad in [{**e,'box':[.1,.2,.8,.4]},{**e,'fade_fraction':.2}]:
  try:dark_backdrop(bad,root,1440,1920,{})
  except ValueError:pass
  else:raise AssertionError('错误暗条未拒绝')
 try:processed_image({'path':'photo.jpg','fit':'contain','cover_only':True},root,(200,300),{})
 except ValueError:pass
 else:raise AssertionError('照片contain未拒绝')
 p={'layout':'story','elements':[{'kind':'text','text':'测试','box':[.1,.25,.5,.1],'size':60,'bg':'#666666'}, {**e,'kind':'image','box':[.1,.2,.7,.4],'role':'background'}]};result=backdrop_rules({'pages':[p]},[],root/'s.json',root);assert not result['passed'] and len(result['errors'])>=2
 p['elements'][0].pop('bg');p['elements'][1]=e;assert backdrop_rules({'pages':[p]},[],root/'s.json',root)['passed']
 p['elements'][1]={**e,'box':[0,0,1,1],'fade_fraction':0};assert backdrop_rules({'pages':[p]},[],root/'s.json',root)['passed']
 # 整版亮图的小黑贴条是最新规则明确许可的例外。
 p['elements'][1]={'kind':'image','path':'photo.jpg','source_id':'test','box':[0,0,1,1],'fit':'cover','role':'background'};p['elements'][0]['bg']='#080808';assert backdrop_rules({'pages':[p]},[],root/'s.json',root)['passed']
 # 数量只作建议；单页整版亮图/全黑均可成立，类型标签仍不能伪造。
 p['watermark']=False;script=root/'s.json';script.write_text(json.dumps({'pages':[p]}));reports=render(script,root/'pages');r=background_rules({'pages':[p]},reports,script,root/'pages');assert r['pages'][0]['background_type']=='full-bright' and r['passed']
 p['elements']=[{'kind':'text','text':'测试','box':[.1,.2,.8,.1],'size':60}];p['background_type']='paper';script.write_text(json.dumps({'pages':[p]}));reports=render(script,root/'pages');r=background_rules({'pages':[p]},reports,script,root/'pages');assert r['pages'][0]['background_type']=='black'
 reports[0]['image_transforms']=[{'source_region_size':[100,200],'resized_size':[200,200],'method':'malformed'}];r=geometry_rules({'pages':[p]},reports,script,root/'pages');assert not r['passed']
 layer,w=watermark_layer({'accent':'#FD3AAC','watermark_style':'neutral'},1440,1920);assert w['text']=='账号名' and w['color']=='#8A8A8A' and w['size']==22
print('PASS: full-bleed渐变实像素；拒绝灰卡片/硬边/照片留边；亮图黑贴条许可；数量仅建议、假标签无效；成图变换与尺寸检查；灰色水印')
