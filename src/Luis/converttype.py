#!/usr/bin/env python
#_*_ coding: utf-8_*_
'''
Created on 2015-8-31

@author: luis
'''

class converttype(object):

    name = '';
    age = 0;
    
    def __init__(self, name,age):
        self.name = name
        self.age = age
        
def convert_to_dict(obj):
    '''把Object对象转换成Dict对象'''
    dict = {}
    dict.update(obj.__dict__)
    return dict
   
     
def convert_to_dicts(objs):
    '''把对象列表转换为字典列表'''
    obj_arr = []
     
    for o in objs:
        #把Object对象转换成Dict对象
        dict = {}
        dict.update(o.__dict__)
        obj_arr.append(dict)
     
    return obj_arr
           
 
def class_to_dict(obj):
    '''把对象(支持单个对象、list、set)转换成字典'''
    is_list = obj.__class__ == [].__class__
    is_set = obj.__class__ == set().__class__
     
    if is_list or is_set:
        obj_arr = []
        for o in obj:
            #把Object对象转换成Dict对象
            dict = {}
            dict.update(o.__dict__)
            obj_arr.append(dict)
        return obj_arr
    else:
        dict = {}
        dict.update(obj.__dict__)
        return dict
    
if __name__ == '__main__':
    stu = converttype('zhangsan', 20)
     
    print '-----------'
    print convert_to_dict(stu)
      
    print '-----------'
    print convert_to_dicts([stu, stu])
     
    print '-----------'
    print class_to_dict(stu)
     
    print '-----------'
    print class_to_dict([stu, stu])
     
    stua = converttype('zhangsan', 20)
    stub = converttype('lisi', 10)
     
    stu_set = set()
    stu_set.add(stua)
    stu_set.add(stub)
    print class_to_dict(stu_set)