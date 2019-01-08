# -*- encoding: utf-8 -*-

import operator
import itertools
import sys

def unity(relis,spos,sep = ';',flat=True,fillin='NA'):
    finlis=[]
    kcount=0
    relis=sorted(relis,key=operator.itemgetter(spos))
    for _k,v in itertools.groupby(relis,operator.itemgetter(spos)):
        tmp=[]
        kcount+=1
        
        group=list(v)
        group.sort(key=operator.itemgetter(spos))
        submerge = itertools.izip_longest(*group,fillvalue=fillin)
        for ele in submerge:
            if flat:
                uniques=set(ele)
                if len(uniques)==1:
                    grpele=ele[0]
                else:
                    grpele=ele
            else:
                grpele = ele
                
            if sep=='tu':
                tmp.append(grpele)
            else:
                if isinstance(grpele,tuple):
                    tu=sep.join([str(x) for x in grpele])
                    tmp.append(tu)
                else:
                    tmp.append(grpele)
        finlis.append(tuple(tmp))
    
    if len(finlis) != kcount:
        print '############\n\nERROR IN UNITY CHECK carefully\n\n\n#######################'
        print len(finlis)
        print kcount
        sys.exit(1)

    return finlis

def regroupdata(data,keypos):
    regroup1 = unity(data,keypos,flat=False,sep='tu')
    regroup2=[]
    for data in regroup1:
        tmp = []
        for row in data:
            tmp.append(row)
        tmp=zip(*tmp)
        regroup2.append(tmp)
    return regroup2    

def singdel(agilis): #clears family which consists only of one splice variant or has only one gene
    if not agilis:
        return agilis
    else:
        loagilis = []
        loagilis = [agi.split('.')[0] for agi in agilis]
        splc = set(loagilis)
        if len(splc)<=1:
            result = []
        else:
            result = agilis
        return result

def tandemdel(agilis,tandemlis): #clears family already covered in the tandem set
    loagilis = []
    result = []
    if not agilis:
        return agilis
    else:
        loagilis = []
        for i in range(0,len(agilis)):
            loagi = agilis[i].split('.')[0]
            loagilis.append(loagi)
        splc = list(set(loagilis))
        if splc in tandemlis:
            result = []
        else:
            result = agilis
        return result

# test routine for tandemdel
# a = ['AT3G09820.1', 'AT5G03300.2']
# e = ['AT2G09820.1', 'AT3G03300.2']
# b = [['AT3G09820', 'AT5G03300'],['AT4G16860', 'AT4G16890'], ['AT1G28350', 'AT2G33840']]
# d = [['AT3G09820', 'AT4G16860'],['AT5G03300', 'AT4G16890'], ['AT1G28350', 'AT2G33840']]
# c = tandemdel(e,d)
# 
# print c

