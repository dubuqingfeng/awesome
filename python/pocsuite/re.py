import re
__author__ = 'qingfeng'

content = '<thead><tr><th class="w80"></th><th class="w150"></th><th class="tl"></th><th class="w120"></th><th class="w150"></th><th class="w110"></th></tr></thead><tbody><tr class="bd-line"><td>1</td><td>~admin</td><td class="tl"><em class="delivery"></em>~96e79218965eb72c92a549dd5a330112</td><td><p><i class="icon-phone"></i>1</p><p><i class="icon-mobile-phone"></i>1</p></td>'
match_result = re.findall(r'~\w*', content, re.I | re.M)

print match_result[0][1:]
if match_result:
    print match_result[0]
    print match_result[1][1:]
