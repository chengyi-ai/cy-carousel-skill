#!/usr/bin/env python3
"""建立独立选题工作目录；占位素材/事实必须补齐，脚本不会编造历史内容。"""
from pathlib import Path
import argparse,json,copy
ROOT=Path(__file__).resolve().parents[1]

def create(out,topic,tone='dark',pages=10,accent=None,mode='production'):
 out=Path(out);tone={'dark':'暗','light':'浅','暗':'暗','浅':'浅'}[tone]
 if out.exists() and any(out.iterdir()):raise ValueError('输出目录非空，拒绝覆盖既有工作')
 if mode=='production' and not 9<=pages<=13:raise ValueError('正式稿需D封面＋8–12内页；三页流程小样请显式--mode sample')
 if mode=='sample' and pages!=3:raise ValueError('流程小样固定3页（D＋2内页），不宣称完整成品')
 out.mkdir(parents=True,exist_ok=True);(out/'assets').mkdir();(out/'research').mkdir()
 template=json.loads((ROOT/'assets/templates'/('暗色页面脚本.json' if tone=='暗' else '浅色页面脚本.json')).read_text())
 template.update(topic=topic,tone=tone,mode=mode)
 if accent:template['config']['accent']=accent
 base=template['pages'];result=[copy.deepcopy(base[0])]
 for i in range(pages-1):
  p=copy.deepcopy(base[1+i%(len(base)-1)]);p['skeleton']=p['skeleton']+f'-{i+1}'
  p['visual_focus']=f'第{i+1}页经核实的视觉焦点'
  for e in p['elements']:
   if e.get('path'):e['path']=f'assets/图源-{i+1}.jpg';e['source_id']=f'source-{i+1}'
  result.append(p)
 template['pages']=result;(out/'页面脚本.json').write_text(json.dumps(template,ensure_ascii=False,indent=2))
 for f in ['标题.txt','正文.txt','置顶评论.txt','来源.md']:
  shutil_text=(ROOT/'assets/templates'/f).read_text();(out/f).write_text(shutil_text)
 (out/'research/事实表.md').write_text('# 事实表\n\n|陈述|原文与页码|出处URL|已证实/传说/存疑|用页|\n|---|---|---|---|---|\n')
 (out/'research/图源许可.csv').write_text('source_id,file,creator,date,source_url,license_url,license,sha256,face_method,processing\n')
 (out/'待确认.md').write_text('# 待确认\n\n- 真实账号主体与署名。\n- 占位事实与图片尚未补齐，不可发布。\n- 许可、原尺寸目检和人工盲测需要逐项记录。\n')
 (out/'README.md').write_text('# '+topic+'\n\n补齐research和assets；保持页面脚本相对路径；保存人工或Vision人脸框与真实mask。随后按Skill运行render、check_all、blind_test、package。首次渲染遇缺图应报错，不会自动生成替代历史照片。\n')
 return out

if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--topic',required=True);ap.add_argument('--tone',choices=['dark','light','暗','浅'],default='dark');ap.add_argument('--pages',type=int,default=10);ap.add_argument('--mode',choices=['production','sample'],default='production');ap.add_argument('--accent');ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 print(create(a.out,a.topic,a.tone,a.pages,a.accent,a.mode))
