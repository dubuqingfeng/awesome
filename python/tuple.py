# -*- coding: utf-8 -*
#tuple
#序列，包括列表、元组、字符串。序列特点：索引和切片
#序列操作：len(),+.*.in,max(),min(),cmp()
# D:/python/python
# Filename: using_tuple.py
zoo = ('panda', 'dog', 'cat')
zoo1 = (2,)
panda,dog,cat=zoo
print panda
print dog
print cat
print 'Number of animals in the zoo is', len(zoo)
new_zoo = ('monkey', 'dolphin', zoo)
print 'Number of animals in the new zoo is', len(new_zoo)
print 'All animals in new zoo are', new_zoo
print 'Animals brought from old zoo are', new_zoo[2]
print 'Last animal brought from old zoo is', new_zoo[2][2] 