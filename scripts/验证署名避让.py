from 验证排版 import watermark_rules
cfg={'accent':'#FD3AAC','account_name':'{账号名}'}
def check(box):return watermark_rules({'config':cfg,'pages':[{'layout':'story','elements':[{'kind':'text','text':'覆盖文字','box':box,'font':'body','size':60,'lineheight':78}]}]})
assert check([.05,.05,.5,.1])['passed']
bad=check([.765,.935,.23,.06]);assert not bad['passed'] and bad['collisions'][0]['actual_ink_overlap_pixels']>0
print('PASS：署名真实alpha与文字墨迹相交拒绝；顶部文字通过。')
