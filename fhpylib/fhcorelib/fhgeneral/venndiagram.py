import os
import fhutils
import itertools
from dbtools.SQLitebase import SQLiteTools
import rpy2.robjects as robjects

import logging
logger=logging.getLogger('fhstandard')

def writesets(datasets,outputdir,outformat='std'):
    """write data with all the combinations into file """
    
    if outformat=='std':
        namlis=[ele[0] for ele in datasets]
        datalis=[list(ele[1]) for ele in datasets]
        filename=os.path.join(outputdir,'stdformat_'+'_'.join(namlis)+'.txt')
        datatrsp=fhutils.transpose(datalis,'NA')

        out=open(filename,'w')
        out.write('\t'.join(namlis)+'\n')
        for row in datatrsp:
            out.write('\t'.join([str(x) for x in row])+'\n')
        out.close()
        return filename
        
    elif outformat=='evenn':
        tabnames=[]
        for name,data in datasets:
            out=open(os.path.join(outputdir,name+'_table.txt'),'w')
            tabnames.append(name+'_table.txt')
            data=list(set(data))
            data.insert(0,name)
            for row in data:
                if isinstance(row,list):
                    out.write('\t'.join([str(x) for x in row])+'\n')
                else:
                    out.write(str(row)+'\n')
            out.close()
            
        return tabnames

    elif outformat=='venneuler':
        totalitems=[]
        hdnames=[]
        for name,data in datasets:
            totalitems.append(dict([(ele,name) for ele in data]))
            hdnames.append(name)
        totalids=fhutils.flatten([list(d.keys()) for d in totalitems])
        tablecontent=[]
        for k in set(totalids):
            outrows=[k]
            for d in totalitems:
                if k in d:
                    outrows.append('1')
                else:
                    outrows.append('0')
            tablecontent.append(outrows)

        out=open(os.path.join(outputdir,name+'_table.txt'),'w')
        out.write('id\t'+'\t'.join(hdnames)+'\n')
        for row in tablecontent:
            out.write('\t'.join([str(x) for x in row])+'\n')
        out.close()
        veninputfile = os.path.join(outputdir,name+'_table.txt')
        return veninputfile
        
        
    else:
        print 'nothing to do'



def rrunner(scriptstring,clean=False):
    """help function if no rpy is available - now disabled """
    scriptfile=str(os.getpid())+'execute.R'
    out=open(scriptfile,'w')
    out.write(scriptstring)
    out.close()

    command  ='R CMD BATCH --no-restore --slave --no-save '+scriptfile
    ret=fhutils.execwrapper(command)
    if ret == 0 and clean == True:
        os.remove(scriptfile)
        os.remove(scriptfile+'out')
    else:
        os.rename(scriptfile,scriptfile+str(fhutils.dtk()))
        os.rename(scriptfile+'out',scriptfile+'.out'+str(fhutils.dtk()))


def pyrvennerable(datasets,figurename='defaultrvenn.pdf',outputdir=''):

    filename= writesets(datasets,outputdir=outputdir)
    robjects.r("rm(list = ls()); graphics.off()")
    robjects.r("""pathnames <- list.files(pattern="[.]R$", path=Sys.getenv('FHR'), full.names=TRUE)""")
    robjects.r("sapply(pathnames, FUN=source)")
    fh_vennerable=robjects.r("fh_vennerable")
    fh_vennerable(inputfilename=filename,outputfilename=figurename)



def pyvenneuler(datasets,figurename='defaultrvenn.tiff',outputdir=''):

    filename= writesets(datasets,outputdir=outputdir,outformat='venneuler')
    robjects.r("rm(list = ls()); graphics.off()")
    robjects.r("""pathnames <- list.files(pattern="[.]R$", path=Sys.getenv('FHR'), full.names=TRUE)""")
    robjects.r("sapply(pathnames, FUN=source)")
    fh_venneuler=robjects.r("fh_venneuler")
    fh_venneuler(inputfilename=filename,outputfilename=figurename)
    

def pyrvenn(datasets,figurename='defaultrvenn.tiff',outputdir=''):

    filename= writesets(datasets,outputdir=outputdir)
    robjects.r("rm(list = ls()); graphics.off()")
    robjects.r("""pathnames <- list.files(pattern="[.]R$", path=Sys.getenv('FHR'), full.names=TRUE)""")
    robjects.r("sapply(pathnames, FUN=source)")
    fh_venndiag=robjects.r("fh_venndiag")
    fh_venndiag(inputfilename=filename,outputname=figurename)

def pyevenn(datasets,figurename='defaultevenn.png',outputdir=''):

    outputdir=os.path.abspath(outputdir)
    
    if not os.path.exists(os.path.join(outputdir,'evenn')):    
        os.mkdir(os.path.join(outputdir,'evenn'))
        os.mkdir(os.path.join(outputdir,'evenn','input'))
        os.mkdir(os.path.join(outputdir,'evenn','output'))
    else:
        fhutils.execwrapper('rm -r '+os.path.join(outputdir,'evenn'))
        os.mkdir(os.path.join(outputdir,'evenn'))
        os.mkdir(os.path.join(outputdir,'evenn','input'))
        os.mkdir(os.path.join(outputdir,'evenn','output'))
        
    inputdir=os.path.join(outputdir,'evenn','input')
    print inputdir
    outputdir=os.path.join(outputdir,'evenn','output')
    
    tabnames = writesets(datasets,outputdir=inputdir,outformat='evenn')

    nomvector=robjects.vectors.StrVector(tabnames)
    robjects.r("rm(list = ls()); graphics.off()")
    robjects.r("""pathnames <- list.files(pattern="[.]R$", path=Sys.getenv('FHR'), full.names=TRUE)""")
    robjects.r("sapply(pathnames, FUN=source)")
    fh_evenn=robjects.r("fh_evenn")
    fh_evenn(inputdir,nomvector,outputdir)
    
    files=os.listdir(outputdir)
    for folder in files:
        if os.path.isdir(os.path.join(outputdir,folder)):
            vennout=os.listdir(os.path.join(outputdir,folder))
            for fi in vennout:
                if fi=='venn_diagram.png':
                    fi=os.path.join(outputdir,folder,'venn_diagram.png')
                    os.rename(fi,figurename)



def significancetriple(common,set1,set2,set3,s1_s2,s1_s3,s2_s3,unique_total=None, name='NA'):
    universe=22746
    if not os.path.exists('vennstat/'):
        os.mkdir('vennstat')

    if unique_total:
        universe=unique_total
    scriptstring='\n'.join(['pv3=phyper({common}-1,{set3},{universe}-{set3},{s1_s2},lower.tail = FALSE, log.p = FALSE)'.format(common=common,set3=set3,universe=universe,s1_s2=s1_s2),
    'pv1=phyper({common}-1,{set1},{universe}-{set1},{s2_s3},lower.tail = FALSE, log.p = FALSE)'.format(common=common,set1=set1,universe=universe,s2_s3=s2_s3),
    'pv2=phyper({common}-1,{set2},{universe}-{set2},{s1_s3},lower.tail = FALSE, log.p = FALSE)'.format(common=common,set2=set2,universe=universe,s1_s3=s1_s3),
    'p.value.overall = max(pv1, pv2, pv3)',
    "print(paste('total pvalue: ',p.value.overall,'pvalue 1',pv1,'pvalue 2',pv2,'pvalue 3',pv3,sep='\t'))"])
    robjects.r(scriptstring)

def significancedual(common,set1,set2,unique_total = None, name='NA'):
    universe=22746
    if not os.path.exists('vennstat/'):
        os.mkdir('vennstat')



    if unique_total:
        universe=unique_total
    scriptstring='\n'.join(['''sink(\"{name}\", append=TRUE, split=TRUE)\n'''.format(name=name+'.txt'),
    "pvov=phyper({common}-1,{set1},{universe}-{set1},{set2},lower.tail = FALSE, log.p = FALSE)".format(common=common,set1=set1,universe=universe,set2=set2),
    "print(paste('pvalue 1',pvov,sep=' '))",
    "pvov=phyper(min({set1},{set2}),{set1},{universe}-{set1},{set2})-phyper({common}-1,{set1},{universe}-{set1},{set2})".format(common=common,set1=set1,universe=universe,set2=set2),
    "print(paste('pvalue 1',pvov,sep=' '))",
    "sink()"])
    robjects.r(scriptstring)




def dbvenn(tablelist,columnid,sqldb,vennengine='evenn',outputfile='defaultdb_venn.pdf',outputdir=None):
    if not outputdir:
        outputdir=os.getcwd()+'/'
    db=SQLiteTools(database =sqldb,stype = 'standard',test =0)
    datalis=[]
    for table in tablelist:
        coldata = db.sqlcolget(tabinfo=[table,columnid],distinct=True)
        datalis.append((table,tuple(set(coldata))))
    venn_runner(dataset=datalis,outputfilename=outputfile,vennengine=vennengine,outputdir=outputdir)
    

def unitest(lis):
    a = len(lis)
    b = len(set(lis))
    if a!=b:
        print ' non unique list - duplicates eliminated -check list'


def venn_runner(dataset,outputfilename='vennrunner.txt',vennengine='',outputdir=''):
    outputdir = os.path.abspath(outputdir)
    outputfilename=os.path.join(outputdir,outputfilename)

    logger.info('#########\nvenn run started#########\n')
    
    if isinstance(dataset,list):
        datadic=dict(dataset)

    uniqueinfo=[]
    commoninfo=[]
    for i in range(0,len(datadic)):
        for v in itertools.combinations(datadic.keys(),i+1):
            combo=[set(datadic[x]) for x in v ]
            tmp=combo[0]
            excl=combo[0]
            for ele in combo[1:]:
                tmp=tmp&ele
                excl=excl-ele
            commoninfo.append((v,tmp))
            uniqueinfo.append((v,excl))
    tabinfo=[]
    for name,ele in commoninfo:
        logger.info('total in {name}: {lenset}'.format(name=' & '.join(name),lenset=len(ele)))
        tabinfo.append(['_&_'.join(name)]+list(ele))
    
    for name,ele in uniqueinfo:
        logger.info('total in {name}: {lenset}'.format(name=' not '.join(name),lenset=len(ele)))
        tabinfo.append([' not '.join(name)]+list(ele))
        
    tabinfotrsp=fhutils.transpose(tabinfo,'')
    out=open(outputfilename,'w')
    for ele in tabinfotrsp:
        out.write('\t'.join([str(x) for x in ele])+'\n')
        
    out.close()
    
    if vennengine=='evenn':
        logger.error('NOT WORKING EVENN')
        pyevenn(dataset,figurename=fhutils.renamefilename(outputfilename,midtag='_'+vennengine,suffix='png'),outputdir =outputdir)
    elif vennengine=='rvenn':
        pyrvenn(dataset,figurename=fhutils.renamefilename(outputfilename,midtag='_'+vennengine,suffix='tiff'),outputdir = outputdir)
    elif vennengine=='venneuler':
        pyvenneuler(dataset,figurename=fhutils.renamefilename(outputfilename,midtag='_'+vennengine,suffix='pdf'),outputdir=outputdir)
    elif vennengine=='rvennerable':
        logger.error('NOT WORKING rvennerable')
        pyrvennerable(dataset,figurename=fhutils.renamefilename(outputfilename,midtag='_'+vennengine,suffix='pdf'),outputdir=outputdir)
    else:
        print 'no venn pdf'

