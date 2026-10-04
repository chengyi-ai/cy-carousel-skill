#!/usr/bin/env python3
"""用户合法提供字库后接入；正文保持。技术验证不代替授权，缺文件直接停止。"""
from pathlib import Path
import argparse,json,copy
from render import TITLE_FONT_KEYS,load_font,missing_glyph,render

def prepare(script,font,assets_root=None,index=0,weight=None,pages=None):
 script=Path(script).resolve();root=Path(assets_root or script.parent).resolve();font=Path(font).expanduser().resolve()
 if not font.is_file():raise ValueError('字体文件不存在：请等待用户提供正式授权文件')
 try:relative=str(font.relative_to(root))
 except ValueError:raise ValueError('字库请放在所选素材根目录的私有fonts/licensed内；不复制进可分发Skill')
 face=load_font(str(font),100,index,weight);data=json.loads(script.read_text());data=copy.deepcopy(data)
 setting={'path':relative,'index':index,'weight':weight}
 changed=[]
 for number,page in enumerate(data['pages'],1):
  if pages and number not in pages:continue
  titles=[e for e in page.get('elements',[]) if e.get('font') in TITLE_FONT_KEYS]
  if not titles:continue
  text=''.join(e['text'].replace('[[','').replace(']]','') for e in titles)
  missing=sorted({ch for ch in text if not ch.isspace() and missing_glyph(face,ch)})
  if missing:raise ValueError(f'P{number:02}授权字库缺字：'+''.join(missing)+'；请合法补字或改写后再接入')
  page.setdefault('config',{}).setdefault('fonts',{})['licensed_headline']=setting
  for e in titles:
   for key in ('stroke','stroke_fill','shadow','glow'):e.pop(key,None)
   # Retain current clear-B/light-route effects; real authorized face needs human visual tuning.
   e.setdefault('effect','3d')
  changed.append(number)
 return data,changed

if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--script',type=Path,required=True);ap.add_argument('--font',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--assets-root',type=Path);ap.add_argument('--index',type=int,default=0);ap.add_argument('--weight',type=float);ap.add_argument('--pages');ap.add_argument('--check-only',action='store_true');a=ap.parse_args()
 try:
  data,changed=prepare(a.script,a.font,a.assets_root,a.index,a.weight,[int(v) for v in a.pages.split(',')] if a.pages else None)
  if a.check_only:print(json.dumps({'font_loaded':True,'changed_pages':changed,'authorization':'必须人工核对'},ensure_ascii=False));raise SystemExit(0)
  if a.out.exists() and any(a.out.iterdir()):raise ValueError('输出目录非空，拒绝覆盖')
  a.out.mkdir(parents=True,exist_ok=True);spec=a.out/'页面脚本.json';spec.write_text(json.dumps(data,ensure_ascii=False,indent=2))
  render(spec,a.out/'pages',assets_root=a.assets_root or a.script.parent)
  print(json.dumps({'changed_title_pages':changed,'human_review':'授权范围与实际视觉需核对；技术成功不等于授权'},ensure_ascii=False))
 except (OSError,ValueError,TypeError) as exc:ap.exit(2,str(exc)+'\n')
