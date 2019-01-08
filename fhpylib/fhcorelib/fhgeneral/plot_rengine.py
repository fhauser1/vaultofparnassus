import fhutils
import os

import rpy2
import rpy2.robjects
from rpy2.robjects.packages import importr
from rpy2.robjects.packages import SignatureTranslatedAnonymousPackage
import rpy2.robjects.lib.ggplot2 as ggplot2
from rpy2 import rinterface

from fhstats import pyobj2dataframe


def rpygraphinit():
    srcpath = os.environ.get('FHR')
    rconsole = rpy2.robjects.r
    rconsole("graphics.off()")  # reset cleanup and start rm(list = ls());
    rconsole("rm(list = ls())")  # reset cleanup
    rsrc = os.path.join(srcpath, 'plotting_routines.R')
    srcfile = ''.join(("source(\'", rsrc, "\')"))
    rconsole(srcfile)
    return rconsole


def pygraph(outgraph, figname, width, height, gformat):
    rconsole = rpy2.robjects.r
    rconsole.library('ggplot2')
    rconsole.library('lattice')
    grdevices = importr('grDevices')
    gformat2device = {'pdf': grdevices.pdf, 'png': grdevices.png}
    gdevplotter = gformat2device[gformat]
    gdevplotter(file=figname, width=width, height=height)
    rconsole.plot(outgraph)
    grdevices.dev_off()


def fusegroupcolumns(tabdata, group):
    """
    function which merges the columns
    in the group statement into
    one column with fused name
    this allows to group later
    in ggplot2
    """

    if isinstance(tabdata, list):
        tmpdata = fhutils.Table()
        tmpdata.columnames = tabdata[0]
        tmpdata.data = tabdata[1:]
        tabdata = tmpdata.iclone()

    newcolumnames = list(tabdata.columnames)
    groupjoin = ''.join([str(x) for x in group])
    newcolumnames.append(groupjoin)
    ntab = fhutils.Table()
    ntab.columnames = newcolumnames
    for row in tabdata.iterrows():
        mergecolumn = ''.join([str(row[ele]) for ele in group])
        newrowlist = [row[ele] for ele in tabdata.columnames] + [mergecolumn]
        ntab.data.append(newrowlist)
    return ntab, groupjoin


def setupdata(tabdata, doscale, group, error, dofit=None):
    if doscale:
        doscale = rpy2.robjects.vectors.FloatVector(tuple(doscale))

    if group in ('', 'NA', '1'):
        group = rinterface.NACharacterType()

    elif isinstance(group, tuple) or isinstance(group, list):
        group = rpy2.robjects.vectors.StrVector(list(group))
        tabdata, group = fusegroupcolumns(tabdata, group)

    if isinstance(dofit, tuple):
        dofit = rpy2.robjects.vectors.StrVector(tuple(dofit))
    else:
        dofit = rpy2.robjects.vectors.StrVector(tuple((0, 0)))

    if error in ('', 'NA'):
        error = rinterface.NACharacterType()

    dataframe = pyobj2dataframe(tabdata)

    return dataframe, doscale, group, error, dofit


def ggscatterplot(tabdata, xvar='xaxis', yvar='yaxis', group='', error='', figname='defaultscatterplot.pdf',
                  main='title',
                  colormode='grey', graphncol=0, width=7, height=7, gformat='pdf', doscale=False, dolabelflip=False,
                  reducepnt=False, dofit=False):
    rconsole = rpygraphinit()
    rggscatterplot = rconsole("rggscatterplot")
    dopdfgraph = rconsole("dopdfgraph")
    dataframe, doscale, group, error, dofit = setupdata(tabdata, doscale, group, error, dofit)
    outgraph = rggscatterplot(tabdata=dataframe, xvar=xvar, yvar=yvar, error=error, main=main, group=group,
                              colormode=colormode, graphncol=graphncol,
                              doscale=doscale, dolabelflip=dolabelflip, reducepnt=reducepnt, dofit=dofit)
    dopdfgraph(outgraph, figname, width=width, height=height, gformat=gformat)


def gglineplot(tabdata, xvar='xaxis', yvar='yaxis', group='', error='', figname='defaultscatterplot.pdf', main='title',
               colormode='grey', graphncol=0, width=7, height=7, gformat='pdf', doscale=False, dolabelflip=False,
               reducepnt=False, dofit=False):

    rconsole = rpygraphinit()
    rgglineplot = rconsole("rgglineplot")
    dopdfgraph = rconsole("dopdfgraph")
    dataframe, doscale, group, error, dofit = setupdata(tabdata, doscale, group, error, dofit)
    outgraph = rgglineplot(tabdata=dataframe, xvar=xvar, yvar=yvar, error=error, main=main, group=group,
                           colormode=colormode, graphncol=graphncol,
                           doscale=doscale, dolabelflip=dolabelflip, reducepnt=reducepnt, dofit=dofit)
    dopdfgraph(outgraph, figname, width=width, height=height, gformat=gformat)


def ggbarplot(tabdata=None, xvar='xaxis', yvar='yaxis', group='', error='', figname='defaultscatterplot.pdf',
              main='title', colormode='grey', cordflip=False, graphncol=0, width=7, height=7, gformat='pdf',
              doscale=False, dolabelflip=True):

    if not tabdata:
        tabdata = []
    rconsole = rpygraphinit()
    rggbarplot = rconsole("rggbarplot")
    dopdfgraph = rconsole("dopdfgraph")
    dataframe, doscale, group, error, dofit = setupdata(tabdata, doscale, group, error)
    outgraph = rggbarplot(tabdata=dataframe, xvar=xvar, yvar=yvar, group=group, error=error, main=main,
                          colormode=colormode,
                          cordflip=cordflip, graphncol=graphncol, doscale=doscale, dolabelflip=dolabelflip)
    dopdfgraph(outgraph, figname, width=width, height=height, gformat=gformat)


def ggbeeswarm(tabdata=None, xvar='xaxis', yvar='yaxis', group='', error='', figname='defaultscatterplot.pdf',
               main='title', colormode='grey', cordflip=False, graphncol=0, width=7, height=7, gformat='pdf',
               doscale=False, dolabelflip=True):

    if not tabdata:
        tabdata = []

    rconsole = rpygraphinit()
    rggbeeswarm = rconsole("rggbeeswarm")
    dopdfgraph = rconsole("dopdfgraph")
    dataframe, doscale, group, error, dofit = setupdata(tabdata, doscale, group, error)
    outgraph = rggbeeswarm(tabdata=dataframe, xvar=xvar, yvar=yvar, group=group, error=error, main=main,
                           colormode=colormode, cordflip=cordflip, graphncol=graphncol, doscale=doscale,
                           dolabelflip=dolabelflip)
    dopdfgraph(outgraph, figname, width=width, height=height, gformat=gformat)


def ggboxplot(tabdata=None, xvar='xaxis', yvar='yaxis', group='', error='', figname='defaultscatterplot.pdf',
              main='title', colormode='grey', cordflip=False, graphncol=0, width=7, height=7, gformat='pdf',
              doscale=False, dolabelflip=True):

    if not tabdata:
        tabdata = []

    rconsole = rpygraphinit()
    rggboxplot = rconsole("rggboxplot")
    dopdfgraph = rconsole("dopdfgraph")
    dataframe, doscale, group, error, dofit = setupdata(tabdata, doscale, group, error)
    outgraph = rggboxplot(tabdata=dataframe, xvar=xvar, yvar=yvar, group=group, error=error, main=main,
                          colormode=colormode, cordflip=cordflip, graphncol=graphncol, doscale=doscale,
                          dolabelflip=dolabelflip)
    dopdfgraph(outgraph, figname, width=width, height=height, gformat=gformat)


def gghistogram(tabdata, xvar='xaxis', yvar='yaxis', group='', error='', figname='defaultscatterplot.pdf', main='title',
                colormode='grey', cordflip=False, graphncol=0, width=7, height=7, gformat='pdf', doscale=False,
                dolabelflip=False):
    rconsole = rpy2.robjects.r
    rgghistogram = rconsole("rgghistogram")
    dopdfgraph = rconsole("dopdfgraph")
    dataframe, doscale, group, error, dofit = setupdata(tabdata, doscale, group, error)
    outgraph = rgghistogram(tabdata=dataframe, xvar=xvar, yvar=yvar, group=group, error=error, main=main,
                            colormode=colormode, cordflip=cordflip, graphncol=graphncol, doscale=doscale,
                            dolabelflip=dolabelflip)
    dopdfgraph(outgraph, figname, width=width, height=height, gformat=gformat)


def ggdensity(tabdata, xvar='xaxis', yvar='yaxis', group='', error='', figname='defaultscatterplot.pdf', main='title',
              colormode='grey', cordflip=False, graphncol=0, width=7, height=7, gformat='pdf', doscale=False,
              dolabelflip=False):

    rconsole = rpygraphinit()
    rggdensity = rconsole("rggdensity")
    dopdfgraph = rconsole("dopdfgraph")
    dataframe, doscale, group, error, dofit = setupdata(tabdata, doscale, group, error)

    outgraph = rggdensity(tabdata=dataframe, xvar=xvar, yvar=yvar, group=group, error=error, main=main,
                          colormode=colormode, cordflip=cordflip, graphncol=graphncol, doscale=doscale,
                          dolabelflip=dolabelflip)
    dopdfgraph(outgraph, figname, width=width, height=height, gformat=gformat)


def ggheatplot(tabdata, xvar='xaxis', yvar='yaxis', group='', error='', figname='defaultheatplot.pdf', main='title',
               colormode='grey', graphncol=0, width=7, height=7, gformat='pdf', doscale=False, dolabelflip=False,
               reducepnt=False, dofit=False):

    rconsole = rpygraphinit()
    rggheatplot = rconsole("rggheatplot")
    dopdfgraph = rconsole("dopdfgraph")
    dataframe, doscale, group, error, dofit = setupdata(tabdata, doscale, group, error)
    outgraph = rggheatplot(tabdata=dataframe, xvar=xvar, yvar=yvar, error=error, main=main, group=group,
                           colormode=colormode, doscale=doscale, dolabelflip=dolabelflip)
    dopdfgraph(outgraph, figname, width=width, height=height, gformat=gformat)


def simpleheatmap(tabdata, figname='defaultheatplot.pdf', main='title',
                  colormode='jet', gformat='pdf', scale='none', dendrogram='both'):
    """
    scale:  none, row, both, col
    """

    rconsole = rpy2.robjects.r
    rsimpleheatmap = rconsole("rsimpleheatmap")
    dopdfgraph = rconsole("dopdfgraph")
    rdataframe = pyobj2dataframe(tabdata, rownames=True, columnames=True)

    from rpy2.robjects.packages import importr

    grdevices = importr('grDevices')
    grdevices.pdf(file=fhutils.renamefilename(figname, suffix=gformat))

    roworder = {'both': True, 'row': True, 'column': False}[dendrogram]
    colorder = {'both': True, 'row': False, 'column': True}[dendrogram]

    rsimpleheatmap(tabdata=rdataframe, scale=scale, dendros=dendrogram, roworder=roworder, colorder=colorder)
    grdevices.dev_off()


# ################### OLD NO LONGER MAINTAINED #################################

def gobar_plot(tabdata, godata, figname='defaulgoplotplotname.pdf', title='xaxis'):
    _datacolumn, tmpfile = datawriter(tabdata)
    if figname == 'defaulgoplotplotname.pdf':
        figname = 'goplot_' + godata[0] + '_' + str(godata[1]) + '.pdf'
        profiletable = 'goplot_' + godata[0] + '_' + str(godata[1]) + '.txt'


    else:
        figname = figname.strip('.pdf') + godata[0] + '_' + str(godata[1]) + '.pdf'
        profiletable = figname.strip('.pdf') + godata[0] + '_' + str(godata[1]) + '.txt'

    if title == 'xaxis':
        title = os.path.split(figname)[1].strip('.pdf')

    scriptstring = """tabdata<-read.table(file='{inputfile}',sep='\\t',header=TRUE)\n
    require(org.At.tair.db)\n
    require(goTools)\n
    require(goProfiles)\n
    x <- org.At.tairENTREZID\n
    mapped_genes <- mappedkeys(x)\n
    agilis <- tabdata$column1\n
    agilis <- unique(agilis)\n
    egenes <- intersect(agilis, mapped_genes)\n
    arabfuncat <- basicProfile(genelist = egenes, onto = "{goontology}", level = {level}, orgPackage = "org.At.tair.db", empty.cats = FALSE)\n
    capture.output(printProfiles(arabfuncat),file='{profiletable}')\n
    pdf(file = "{figname}")\n
    par(oma=c(2,2,2,2),mar=c(2,11,2,0.1), cex=0.8,ps=10)\n
    plotProfiles(arabfuncat, aTitle = "{title}", labelWidth = 60)\n
    dev.off()\n"""
    scriptstring = scriptstring.format(inputfile=tmpfile, goontology=godata[0], level=godata[1], figname=figname,
                                       title=title, profiletable=profiletable)
    # rrunner(scriptstring=scriptstring,datafile=tmpfile)
    rpy2.robjects.r(scriptstring)


def gopie_plot(tabdata, godata, figname='defaulgoplotplotname.pdf', title='xaxis'):
    _datacolumn, tmpfile = datawriter(tabdata)
    if figname == 'defaulgoplotplotname.pdf':
        figname = 'goplot_' + godata[0] + '_' + str(godata[1]) + '.pdf'

    if title == 'xaxis':
        title = godata[0] + '_' + str(godata[1])
    scriptstring = """tabdata<-read.table(file='{inputfile}',sep='\\t',header=TRUE)\n
    require(org.At.tair.db)\n
    require(goTools)\n
    require(goProfiles)\n
    x <- org.At.tairENTREZID\n
    mapped_genes <- mappedkeys(x)\n
    agilis <- tabdata$column1\n
    agilis <- unique(agilis)\n
    egenes <- intersect(agilis, mapped_genes)\n
    arabfuncat <- basicProfile(genelist = egenes, onto = "{goontology}", level = {level}, orgPackage = "org.At.tair.db", empty.cats = FALSE)\n
    slices <- arabfuncat${goontology}$Frequency\n
    lbls <- arabfuncat${goontology}$Description\n
    pdf(file = "{figname}")\n
    par(oma=c(1,1,1,1),cex=0.5,pty='m')\n
    plotProfiles(arabfuncat, aTitle = "MF_2", labelWidth = 60)\n
    pie(slices, labels = lbls, main = "Pie Chart of {goontology}", col = rainbow(length(lbls)))\n
    dev.off()\n"""
    scriptstring = scriptstring.format(inputfile=tmpfile, goontology=godata[0], level=godata[1], figname=figname,
                                       title=title)
    # rrunner(scriptstring=scriptstring,datafile=tmpfile)
    rpy2.robjects.r(scriptstring)


def seqlogo(tabdata, figname='defaullogoplotplotname.pdf', title='xaxis'):
    scriptstring = '\n'.join(
        ["library(Biostrings)", "patterns <- DNAStringSet(c({tabdata})) # Sample set of DNA fragments.",
         " pwm <- PWM(patterns) # Computes a PWM for DNA fragments", "library(seqLogo)", "pdf(file = '{figname}')",
         "seqLogo(t(t(pwm) * 1/colSums(pwm))) # Plots pwm as sequence logo", "dev.off()"])

    scriptstring = scriptstring.format(tabdata='\'' + "','".join(list(tabdata)) + '\'', figname=figname)
    # rrunner(scriptstring=scriptstring,datafile=None)
    rpy2.robjects.r(scriptstring)


def test():
    tabdata = [('xaxis', 'yaxis'), (5, 5), (8, 6), (5, 6), (3, 4)]
    gghistogram(tabdata, xvar='xaxis', yvar='', group='', error='', figname='defaultscatterplot.pdf', main='title',
                colormode='grey', cordflip=False, graphncol=0, width=7, height=7, gformat='pdf', doscale=False,
                dolabelflip=False)


# ##############################  OLD FUNCTIONS ################################################

def datawriter(tabdata):
    tmpfile = str(os.getpid()) + 'datatmpfile.txt'
    datacolumn = []

    out = open(tmpfile, 'w')
    if isinstance(tabdata[0], list) or isinstance(tabdata[0], tuple):
        for i in range(0, len(tabdata[0])):
            datacolumn.append('column' + str(i))
        out.write('\t'.join(datacolumn) + '\n')
        for xele in tabdata:
            out.write('\t'.join([str(x) for x in xele]) + '\n')

    else:
        out.write('column1\n')
        for xele in tabdata:
            out.write(str(xele) + '\n')
        datacolumn.append('column1')

    out.close()

    return datacolumn, os.path.abspath(tmpfile)


def rrunner(scriptstring, datafile, clean=True):
    scriptfile = str(os.getpid()) + 'execute.R'
    out = open(scriptfile, 'w')
    out.write(scriptstring)
    out.close()

    command = 'R CMD BATCH --no-restore --slave --no-save ' + scriptfile
    ret = fhutils.execwrapper(command)
    if ret == 0:
        if datafile:
            os.remove(datafile)
        os.remove(scriptfile)
        os.remove(scriptfile + 'out')
    else:
        if datafile:
            os.rename(datafile, datafile + str(fhutils.dtk()))
        os.rename(scriptfile, scriptfile + str(fhutils.dtk()))
        os.rename(scriptfile + 'out', scriptfile + '.out' + str(fhutils.dtk()))


def barplot(tabdata, grouplabels, outputfile, xlegend='Number of genes', ylegend='Frequence class'):
    # rpy2.robjects.r("rm(list = ls()); graphics.off()")
    # rpy2.robjects.r("""pathnames <- list.files(pattern="[.]R$", path=Sys.getenv('FHR'), full.names=TRUE)""")
    # rpy2.robjects.r("sapply(pathnames, FUN=source)")
    fh_barplot = rpy2.robjects.r("fh_barplot")
    tabdata = rpy2.robjects.vectors.FloatVector(tabdata)
    grouplabels = rpy2.robjects.vectors.StrVector(grouplabels)
    fh_barplot(tabdata, grouplabels, outputfile, xlegend, ylegend)


def hist_plot(tabdata, binalgorithm="Sturges", breaks=None, figname='defaulhistplotname.pdf', xlegend='xaxis',
              ylegend='yaxis'):
    if not tabdata:
        print 'no values in tabdata'
        return

    if isinstance(tabdata[0], basestring) and isinstance(tabdata[len(tabdata) - 1], basestring):
        barplot(tabdata, freq=True, figname=figname, xlegend=xlegend, ylegend=ylegend)
        return

    # datacolumn,tmpfile=datawriter(tabdata)
    # rpy2.robjects.r("rm(list = ls()); graphics.off()")
    # rpy2.robjects.r("""pathnames <- list.files(pattern="[.]R$", path=Sys.getenv('FHR'), full.names=TRUE)""")
    # rpy2.robjects.r("sapply(pathnames, FUN=source)")
    fh_histogram = rpy2.robjects.r("fh_histogram")
    tabdata = rpy2.robjects.vectors.IntVector(tabdata)
    if breaks:
        breaks = rpy2.robjects.vectors.IntVector(breaks)
    fh_histogram(tabdata=tabdata, outputfile=figname, binalgorithm=binalgorithm, breaks=breaks, xlegend=xlegend,
                 ylegend=ylegend)


# hist_plot([1,1,3,4,5,6,7,8,9],bins="bins")

def scatter_box(tabdata, figname='defaulscterboxplotname.pdf', xlabel='xaxis', ylabel='yaxis'):
    # datacolumn,tmpfile=datawriter(tabdata)

    scriptstring = """

    tabdata<-read.table(file='{inputfile}',sep='\\t',header=TRUE)
    pdf(file='{figname}')
    par(fig=c(0,0.8,0,0.8), new=TRUE)
    plot(tabdata$column1, tabdata$ycolumn2, xlab='{xlabel}',ylab='{ylabel}')
    par(fig=c(0,0.8,0.55,1), new=TRUE)
    boxplot(table(tabdata$column2), horizontal=TRUE, axes=FALSE)
    par(fig=c(0.65,1,0,0.8),new=TRUE)
    hist(tabdata$score, axes=FALSE)
    dev.off()
    """.format(inputfile=str(os.getpid()) + 'datatmpfile.txt', figname=figname, xlabel=xlabel, ylabel=ylabel)

    # rrunner(scriptstring=scriptstring,datafile=tmpfile)
    rpy2.robjects.r(scriptstring)


def scatter_hist(tabdata, figname='defaulscatterplotname.pdf', xlabel='xaxis', ylabel='yaxis'):
    _datacolumn, tmpfile = datawriter(tabdata)

    scriptstring = """

    tabdata<-read.table(file='{inputfile}',sep='\\t',header=TRUE)

    x <- tabdata$column0
    y <- tabdata$column1

    yh <- hist(y, plot = FALSE)
    xh <- hist(x, plot = FALSE)
    pdf(file='{figname}')


    par(fig=c(0,0.8,0,0.8))
    plot(x, y, xlab='{xlabel}',ylab='{ylabel}')
    par(fig=c(0,0.8,0.55,1), new=TRUE)
    barplot(xh$intensities,col= '483',space=0,horiz=F, axes = FALSE)
    par(fig=c(0.65,1,0,0.8),new=TRUE)
    barplot(yh$intensities,col= 'salmon', space=0,horiz=T, axes = FALSE)
    dev.off()
    """.format(inputfile=tmpfile, figname=figname, xlabel=xlabel, ylabel=ylabel)
    # rrunner(scriptstring=scriptstring,datafile=tmpfile)
    rpy2.robjects.r(scriptstring)


def column_plot(tabdata, freq=False, figname='defaulcolumnplotplotname.pdf', xlabel='xaxis', ylabel='yaxis'):
    _datacolumn, tmpfile = datawriter(tabdata)

    scriptstring = "tabdata<-read.table(file='{inputfile}',sep='\\t',header=TRUE)\n"

    if freq:
        scriptstring += """tabdata<-as.tabdata.frame(table(tabdata))\n"""
        plotcolumn = 'tabdata$Freq'
        grouplabels = 'as.vector(tabdata$tabdata),las=2'
    else:
        plotcolumn = 'tabdata$column1,tabdata$column2'
        grouplabels = 'NULL'

    scriptstring += """pdf(file='{figname}')\n
    par(oma=c(2,2,2,2),las=2 ,mar=c(11,2,2,0.1), cex=0.8,ps=10)\n
    barplot({plotcolumn}, col='blue', xlab='{xlabel}',ylab='{ylabel}',names.arg={grouplabels},plot=TRUE)\n
    dev.off()\n"""
    scriptstring = scriptstring.format(inputfile=tmpfile, plotcolumn=plotcolumn, figname=figname, xlabel=xlabel,
                                       ylabel=ylabel, grouplabels=grouplabels)
    # rrunner(scriptstring=scriptstring,datafile=tmpfile)
    rpy2.robjects.r(scriptstring)