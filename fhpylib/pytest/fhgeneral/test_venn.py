import logging

from fhgeneral import venndiagram

logger=logging.getLogger('fhstandard')

def testrun():
    
    dataset=[('a',(1,2,3,4,5,6,7,8,90)),('b',(1,2,3,4,5,6,7,80,9)),
    ('c',(1,2,3,4,5,6,70,8,9)),('d',(1,2,3,4,5,60,7,8,9))]
    venndiagram.venn_runner(dataset,vennengine='rvenn',outputdir='testfiles')
    venndiagram.venn_runner(dataset,vennengine='venneuler',outputdir='testfiles')
    
    # NOT WORKING venndiagram.venn_runner(dataset,vennengine='rvennerable',outputdir='testfiles')
    # NOT WORKING venndiagram.venn_runner(dataset,vennengine='evenn',outputdir = 'testfiles')

    print 'ALL TESTS RUN'

if __name__ == '__main__':
    testrun()
