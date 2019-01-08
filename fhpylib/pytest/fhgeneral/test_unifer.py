from __future__ import print_function
from fhgeneral import unifer
from fhgeneral import fhutils


# #test sequence - validate by comparison 
def test():
    
    testlist = ['0', '00', '123', '-123.', '-123e-4', '0123', '0x1a1', '-123+4.5j', '0b0101', '0.123', '-0xabc', '-0b101', '','-']
    for s in testlist:
        print ("%14s -> %-14s %s" % ('"'+s+'"', fhutils.is_numeric(s), type(fhutils.is_numeric(s))))
    
    
    trichck = [('a2', 'c', '3'),('a3', 'c', '3'),('a4', 'b', '3'),('a5', 'd', '5'),('a6', 'b', '6'),('a1', 'b', '3')]
    expect = [('a2;a3;a4;a1', 'c;c;b;b', '3'),('a5', 'd', '5'),('a6', 'b', '6')]
    uniout=unifer.unity(trichck,2,sep=';')
    print('input trichck', trichck)
    print ('expected output', expect)
    print ('out new',uniout)
    assert uniout == expect, str(expect)+str(uniout)



    diceck = [('c','AGI1'),('c','AGI2'),('d','AGI3'),('d','AGI4'),('b','AGI5'),('b','AGI6')]
    expect = [('b','AGI5;AGI6'),('c','AGI1;AGI2'),('d','AGI3;AGI4')]
    uniout= unifer.unity(diceck,0)
    print ('input diceck',diceck)
    print ('expected output', expect)
    print ('out new', uniout)
    assert uniout == expect, str(expect)+str(uniout)

    lis=[('b','c1','d4','ag'),('c','c2','d3','ac'),('c','c3','d2','af'),('b','c4','d1','ab'),('b','c5','d0','av')]
    expect=[('b',('c1','c4','c5'),('d4','d1','d0'),('ag','ab','av')),('c',('c2','c3'),('d3','d2'),('ac','af'))]
    uniout=unifer.unity(lis,0,sep = 'tu')
    print ('input lis',lis)
    print ('expected output', expect)
    print ('out new', uniout)
    assert uniout == expect, str(expect)+str(uniout)
    
    
    uniami=[(u'TAGGACTAGACATTCACCCAG', 31.5, u'AT1G15750;AT1G80490'),(u'TAGGACTAGACATTCACCCAG', 38.5, u'AT1G15750;AT1G80490'), (u'TATATACCTTTTGGCTCTCCG', 38.0, u'AT1G15750;AT1G80490'), (u'TACCTTTTGCCATTAGCCCCG', 42.5, u'AT2G21580;AT4G39200')]
    expect=[(u'TACCTTTTGCCATTAGCCCCG', 42.5, u'AT2G21580;AT4G39200'),(u'TAGGACTAGACATTCACCCAG', (31.5,38.5), u'AT1G15750;AT1G80490'),(u'TATATACCTTTTGGCTCTCCG', 38.0, u'AT1G15750;AT1G80490')]
    uniout= unifer.unity(uniami,0,sep = 'tu')
    print ('input uniami',uniami)
    print ('expected output', expect)
    print ('out new', uniout)
    assert uniout == expect, str(expect)+str(uniout)


    #
    uniami=[('AT3G10890;AT3G10900;AT3G30540;AT5G66460',4,39.25,'TGGTTCGTTCATAAGCGCCCA'),
        ('AT3G10890;AT3G10900;AT3G30540;AT5G66460',4,40.75,'TGGTTCGTTCATAAGCGCCCG'),
        ('AT3G10890;AT3G10900;AT3G30540;AT5G66460',4,46.75,'TGGTTCGTTCATAGGCGCCCA'),
        ('AT3G10890;AT3G10900;AT3G30540;AT5G66460',4,47.75,'TGGTTCGTTCATAAGCCCCCG'),
        ('AT3G10890;AT3G10900;AT3G30540;AT5G66460',4,49.25,'TGGTTCGTTCATAAGCCCCCA'),
        ('AT3G10890;AT3G10900;AT3G30540;AT5G66460',4,52.75,'TGGTTCGTTCATAAGCCCCGA'),
        ('AT3G10890;AT3G10900;AT3G30540;AT5G66460',4,52.75,'TGGTTCGTTCATATGCTCCCG'),
        ('AT3G10890;AT3G10900;AT3G30540;AT5G66460',4,54.25,'TCGTTCATAAGCTTCCGACCC'),
        ('AT3G10890;AT3G10900;AT3G30540;AT5G66460',4,61.75,'TGGTTCGTTCATATGCTCCGA'),
        ('AT3G10890;AT3G10900;AT3G30540;AT5G66460',4,63.25,'TGGTTCGTTCATAAGCTCCGA'),
        ('AT3G10890;AT3G10900;AT3G30540;AT5G66460',4,64.25,'TCGTTCATAAGCTCCCGACCA'),
        ('AT3G10890;AT3G10900;AT3G30540;AT5G66460',4,65.25,'TCGTTCATAAGCTCCCAGCCG'),
        ('AT3G10890;AT3G10900;AT3G30540;AT5G66460',4,65.75,'TCGTTCATAAGCTCCCAGCCC')]
    expect=[('AT3G10890;AT3G10900;AT3G30540;AT5G66460', 4, (39.25, 40.75, 46.75, 47.75, 49.25, 52.75, 52.75, 54.25, 61.75, 63.25, 64.25, 65.25, 65.75), ('TGGTTCGTTCATAAGCGCCCA', 'TGGTTCGTTCATAAGCGCCCG', 'TGGTTCGTTCATAGGCGCCCA', 'TGGTTCGTTCATAAGCCCCCG', 'TGGTTCGTTCATAAGCCCCCA', 'TGGTTCGTTCATAAGCCCCGA', 'TGGTTCGTTCATATGCTCCCG', 'TCGTTCATAAGCTTCCGACCC', 'TGGTTCGTTCATATGCTCCGA', 'TGGTTCGTTCATAAGCTCCGA', 'TCGTTCATAAGCTCCCGACCA', 'TCGTTCATAAGCTCCCAGCCG', 'TCGTTCATAAGCTCCCAGCCC'))]
    uniout= unifer.unity(uniami,0,sep = 'tu')
    print ('input uniami',uniami)
    print ('expected output', expect)
    print ('out new', uniout)
    assert uniout == expect, str(expect)+str(uniout)


    data=[('a',1,2),('a',2,3),('a',3,4),('a',4,5),('a',5,6),('a',7,8),('a',6,9),
        ('b',1,1),('b',2,4),('b',3,4),('b',4,5),('b',5,7),('b',6,8),('b',7,9),('b',8,7),
        ('c',1,45),('c',2,8),('c',3,7),('c',4,9),('c',5,7),('c',6,6),('c',7,1)]
    unifer.regroupdata(data,keypos=0)
if __name__ == '__main__':
    test()
