from __future__ import print_function
from uncertainties import ufloat, ufloat_fromstr

from fhgeneral.fhstats import ufmeanstd,bin_values,dataframe2fhtab,fhtab2dataframe
from fhgeneral.fhutils import Table

def testrun():
    
    tab=Table()
    tab.data= [('info1',1,2,'op1'),('info2',2,3,3),('info3',3,4,3),('info4',4,5,3),('info5',5,6,3),('info6',6,7,3),(9,7,8,3)]
    tab.columnames=['a','b','c','d']
    print(tab)
    dfrm = fhtab2dataframe(tab)
    print(dfrm)
    ntab = dataframe2fhtab(dfrm)

    
    print ('test 1')  
    
    testufmean=[ufloat_fromstr('2.0+/-1.0'), 4.0]
    print(ufmeanstd(testufmean,True))    
    print ('test 2')  
    testufmean=[ufloat_fromstr('2.0+/-1.0'), ufloat_fromstr('4.0+/-0.0')]
    print(ufmeanstd(testufmean,True))    
    
    print ('test 3')  
    
    testufmean=[ufloat_fromstr('2.0+/-0.0'), ufloat_fromstr('4.0+/-0.0')]
    print(ufmeanstd(testufmean,True))    
    
    print ('test 4')  
    
    testufmean=[2.0, 4.0]
    print(ufmeanstd(testufmean,True))    
    
    print('test 1')
    binlis=[1,1,2,2]
    bins=[1,2,3]
    bl=bin_values(binlis,bins)
    print('binlis:',binlis,'\n','bins:',bins,'\n','binned:',bl)

    print('test 2')
    binlis=[0,0,1,1,2,2]
    bins=[1, 2, 3]
    bl=bin_values(binlis,bins)
    print(binlis,'\n',bins,'\n',bl)

    print('test 3')
    binlis=[1,1,2,2,3,3]
    bins=[1, 2, 3]
    bl=bin_values(binlis,bins)
    print(binlis,'\n',bins,'\n',bl)

    print('test 4')
    binlis=[1,1,2,2,3,3,4,4]
    bins=[1, 2, 3]
    bl=bin_values(binlis,bins)
    print(binlis,'\n',bins,'\n',bl)


    # import numpy as np
    # 
    # x = np.array(binlis)
    # bins = np.array([0,25,50,75,101])
    # inds = np.digitize(x, bins)
    # for n in range(x.size):
    #     print bins[inds[n]-1], "<=", x[n], "<", bins[inds[n]]

if __name__ == '__main__':
    testrun()