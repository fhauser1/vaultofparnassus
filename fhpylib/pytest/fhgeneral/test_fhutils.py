from __future__ import print_function
import sys
import os
import unittest

from fhgeneral.fhutils import dictinvert
from fhgeneral.fhutils import keylis2dic
from fhgeneral.fhutils import filterconsecutive
from fhgeneral.fhutils import natsorted
from fhgeneral.fhutils import renamefilename
from fhgeneral.fhutils import setup_logging
from fhgeneral.fhutils import execwrapper
from fhgeneral.fhutils import Table
from fhgeneral.fhutils import read_panda


class TestUtils(unittest.TestCase):
    """docstring for TestUtils"""
    def setUp(self):
            self.seq = range(10)
        
    def testtable(self):
        tab1=Table()
        tab2=Table()
        tab1.read('testfiles/tab1.txt',columnames=True)
        tab2.read('testfiles/tab1.txt',columnames=False)
        print ('read test')
        print (tab1)
        print (tab2)
        tab1.read('testfiles/tab1.txt',columnames=True)
        tab2.read('testfiles/tab2.txt',columnames=True)
        print ('merge test')
        print (tab1)
        print (tab2)
        tab1.merge(tab2,by_x='r',by_y='w')
        print (tab1)
        tab2.read('testfiles/tab2.txt',columnames=True)
        tab2.write_html('testfiles/tab2.html')
        tab2.write('testfiles/tab2-repo.txt')
        sub1 = tab1.getcolumn(('r','t')).tolist()
        self.assertEqual(sub1,[['3', '3'],['3', '333']])
        sub2 = tab1.getcolumn(0).tolist()
        self.assertEqual(sub2,[['1'],['2']])


    def testpanda(self):
        tabp = read_panda('testfiles/tab1.txt',columnames=True)
        print (tabp  )  
        tabp = read_panda('testfiles/tab1.txt',columnames = True,rownames=True)
        # print tabp
        # print tabp[['e','t']]
        for row in tabp.iterrows():
            print(row[0])

    def testrun(self):

        # self.testtable()
    
    
        print ('test 1')
    
        d = {'a': 1, 'b': 1, 'c':1, 'd':7}
        ind = dictinvert(d)
        ind2 = dictinvert(ind)
        print (d)
        print (ind)
        print (ind2)
    
        d = {1: ['a', 'b', 'b'], 7: ['d']}
        ind = dictinvert(d)
        ind2 = dictinvert(ind)
        print (d)
        print (ind)
        print (ind2)
    
        d = {1: ['ahh', 'bjjj', 'bjjj'], 7: ['oood']}
    
        ind = dictinvert(d)
        ind2 = dictinvert(ind)
    
        print (d)
        print (ind)
        print (ind2)

    
        a = ['ver-1.3.12', 'ver-1.3.3', 'ver-1.2.5', 'ver-1.2.15', 'ver-1.2.3', 'ver-1.2.1']
        b = natsorted(a)
        print (a,'\n',b)
        tulis=[('yellow', 1), ('blue', 2), ('yellow', 3), ('blue', 4), ('red', 1)]
        d=keylis2dic(tulis)
        print (d['blue'])
        self.assertEqual (list(d.items()),[('blue', [2, 4]), ('red', [1]), ('yellow', [1, 3])])
    
        confirmed = filterconsecutive(mtchlis = [0,1,2,5,6,7,10,12,13])
        self.assertEqual(confirmed,[(0,2),(5,7),(10,10),(12,13)])
    
    
        print (renamefilename(os.path.join('','oop.GRF.fastaR'),'hih','iii'))
        print(renamefilename('/llll/kllklkkl/annotationfilename.txt', prefix='txt'))
    
        import logging
        setup_logging()
        logger = logging.getLogger('fhstandard')
        logger.info('info message')
        logger.error('error message')

    
        execwrapper('ls -alt')
        # 
        execwrapper('ls --alt')
    
    
        print ('ALL TESTS RUN')

if __name__ == '__main__':
    unittest.main()