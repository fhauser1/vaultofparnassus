from builtins import range
import sys
import os

import matplotlib
# matplotlib.use('qt4agg')
import matplotlib.pyplot

# matplotlib.pyplot.switch_backend("TkAgg")
# matplotlib.rcParams['backend.qt4']='PySide'
#
from fhgeneral.plot_rengine import ggscatterplot,rpygraphinit,ggboxplot,ggbarplot
from fhgeneral.fhutils import Table
from fhgeneral.fhstats import statoverview,rpystatinit

def testrun():
    rp=6
    lp=9
    
    data=[list(range(0+i,3+i)) for i in range(1,25)]
    data=[tuple(ele[0:2]+[rp,2,'k']) if ele[2]<10 else tuple(ele[0:2]+[lp,6,'o']) for ele in data]
    tab =Table('testdata')
    tab.data=data
    tab.columnames=('A','B','C','D','E')
    tab.write('testplotdata.txt')

    statoverview(tab)
#    figure=matplotlib.pyplot.figure('ooop')
#    matplotlib.pyplot.show()
#    matplotlib.pyplot.close('all')
#    matplotlib.pyplot.close(figure)
    
    
    ggscatterplot(tabdata=tab,xvar='A',yvar='B',group='',error='',figname='a.pdf',main='a',
    colormode='hue',graphncol=0,width=7,height=7,gformat='pdf',doscale=False,dolabelflip=False,reducepnt=False,dofit=False)
    
    ggscatterplot(tabdata=tab,xvar='A',yvar='B',group='C',error='',figname='b.pdf',main='b',
    colormode='hue',graphncol=0,width=7,height=7,gformat='pdf',doscale=False,dolabelflip=False,reducepnt=False,dofit=False)
    
    ggscatterplot(tabdata=tab,xvar='A',yvar='B',group='C',error='D',figname='c.pdf',main='c',
    colormode='hue',graphncol=0,width=7,height=7,gformat='pdf',doscale=False,dolabelflip=False,reducepnt=False,dofit=False)
    
    ggscatterplot(tabdata=tab,xvar='A',yvar='B',group='C',error='',figname='d.pdf',main='d',
    colormode='hue',graphncol=0,width=7,height=7,gformat='pdf',doscale=False,dolabelflip=False,reducepnt=False,dofit=False)
    
    ggboxplot(tabdata=tab,xvar='E',yvar='B',group='C',error='',figname='e.pdf',main='e',
    colormode='hue',graphncol=0,width=7,height=7,gformat='pdf',doscale=False,dolabelflip=False)
    
    ggbarplot(tabdata=tab,xvar='A',yvar='B',group='A',error='',figname='f.pdf',main='ABA',
    colormode='hue',graphncol=0,width=7,height=7,gformat='pdf',doscale=False,dolabelflip=False)

    ggbarplot(tabdata=tab,xvar='A',yvar='B',group='E',error='',figname='g.pdf',main='ABE',
    colormode='hue',graphncol=0,width=7,height=7,gformat='pdf',doscale=False,dolabelflip=False)
    
    ggbarplot(tabdata=tab,xvar='A',yvar='B',group='',error='',figname='h.pdf',main='AB',
    colormode='hue',graphncol=0,width=7,height=7,gformat='pdf',doscale=False,dolabelflip=False)
    


if __name__ == '__main__':
    testrun()