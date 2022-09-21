# -*- encoding: utf-8 -*-
from __future__ import division  # forces float output for division
from __future__ import print_function
from __future__ import absolute_import

from builtins import zip
from builtins import str
from builtins import range
from builtins import object
import os
import math
import sys

import numpy
import uncertainties
from uncertainties import ufloat
import rpy2

from rpy2 import rinterface, rinterface_lib
import rpy2.rlike.container as rlc
from rpy2 import robjects
import scipy.stats

from . import fhutils

# python based common statistical measurements

def fhmean(numbers):
    return sum(numbers) / len(numbers)


def fhmedian(numbers):
    """

    Return the median of the list of numbers.
    note: np.median as alternarive

    """
    # Sort the list and take the middle element.

    n = len(numbers)
    copy = numbers[:]  # So that "numbers" keeps its original order
    copy.sort()
    if n & 1:  # There is an odd number of elements
        return copy[n // 2]
    else:
        return (copy[n // 2 - 1] + copy[n // 2]) / 2


def fhstdev(numbers):
    m = fhmean(numbers)
    v = 0.0
    for i in range(0, len(numbers)):
        v += (numbers[i] - m) ** 2
    v *= 1.0 / (len(numbers) - 1.0)
    v = math.sqrt(v)
    return v


def var(numbers):
    value = numpy.var(numbers)
    return value


def setupcohen(m, sd):
    """
    prepare values for cohen
    """
    if isinstance(m, list) or isinstance(m, tuple):
        f_m = numpy.mean(m)
        f_sd = numpy.std(m, ddof=1)

    elif isinstance(m, uncertainties.UFloat):
        f_m = m.nominal_value
        f_sd = m.std_dev
    else:
        f_m = m
        f_sd = sd
        assert f_sd, 'ERROR NO STANDARDDEVIATION ' + str(f_sd)
    return f_m, f_sd


def fhcohensd(m1, m2, sd1=None, sd2=None):
    """
    Cohen effectsize 
    m1,m2 list of values or mean values as ufloat or float +- sd
    """
    f_m1, f_sd1 = setupcohen(m1, sd1)
    f_m2, f_sd2 = setupcohen(m2, sd2)

    effsize = (f_m1 - f_m2) / numpy.sqrt((f_sd1 ** 2 + f_sd2 ** 2) / 2.0)
    return effsize


# ################ ERROR PROPAGATION UNCERTAINITIES ###############


def checkufloat(numlis):
    if not isinstance(numlis, list):
        raise NameError('INVALID - MUST BE LIST')
    weightslist = []
    avg = []
    for ele in numlis:
        if isinstance(ele, uncertainties.UFloat):
            avg.append(ele.nominal_value)
            weightslist.append(ele.std_dev)
        else:
            avg.append(ele)

    if len(set([num for num in weightslist if num == 0.0])) == 1:  # delete weights if all weights are zero
        weightslist = []
    return avg, weightslist


def ufmeanstd(values, asufloat=False):
    """
    average of values with errors and propagating this error
    not using yet weighted by error approach
    """

    # ignore nan 
    if not values:
        return values
    
    # ignore only one value - convert to ufloat
    if isinstance(values,list) and len(values)==1:
        ufvalue = values[0]
        if not isinstance(ufvalue,uncertainties.UFloat):
            ufvalue = ufloat(ufvalue, 0.0)

    # handle mixture of ufloat and float 
    elif sum([1 for ele in values if isinstance(ele, uncertainties.UFloat)]) != len(values):
        valueconvert = [ele for ele in values if not isinstance(ele, uncertainties.UFloat)]
        valueufloat = [ele for ele in values if isinstance(ele, uncertainties.UFloat)]

        if len(valueconvert) == len(values):  # standard mean calculation
            meanuc = numpy.mean(values)
            ufstd = numpy.std(values, ddof=1)  # use n-1 by default as in R
            ufvalue = ufloat(meanuc, ufstd)

        elif len(valueufloat) == len(values):
            ufvalue = numpy.mean(valueufloat)

        else:
            print('WARNING MIXED VALUES WITH AND WITHOUT ERROR')
            meanuc = numpy.mean(valueconvert)
            ufstd = numpy.std(valueconvert, ddof=1)  # use n-1 by default as in R
            noerrorvalue = ufloat(meanuc, ufstd)
            witherrorvalues = numpy.mean(valueufloat)
            ufvalue = numpy.mean([witherrorvalues, noerrorvalue])

    # if all values are ufloat    
    else:
        ufvalue = numpy.mean(values)

    if not asufloat:
        ufvalue = (ufvalue.nominal_value, ufvalue.std_dev)
        
    return ufvalue


def propagatetable(datatable, groupcolumn, measurecolumn, errorcolumn):
    """
    primitive aggregate i.e. averaging function
    for a table with error values
    propagates error using ufloat
    mechanism
    NA filtered out by default - no control
    """

    if isinstance(groupcolumn, str):
        groupcolumn = (groupcolumn,)

    if isinstance(groupcolumn, str):
        groupcolumn = (groupcolumn,)

    keyvalue = []
    for row in datatable.iterrows():
        tmp = []
        for col in groupcolumn:
            tmp.append(row[col])
        if row[measurecolumn] in ('NA',):
            continue
        elif row[errorcolumn] in ('NA',):
            value = row[measurecolumn]
        else:
            value = ufloat(row[measurecolumn], row[errorcolumn])
        keyvalue.append((tuple(tmp), value))

    keyvalue = fhutils.keylis2dic(keyvalue)

    resultable = fhutils.Table('propagate')
    resultable.columnames = list(groupcolumn) + [measurecolumn, errorcolumn]

    for k, valuelist in list(keyvalue.items()):
        valuelist = [ele for ele in valuelist if ele != 'NA']  # NA filtered out
        ufavg = ufmeanstd(valuelist, asufloat=True)
        row = list(k)
        if isinstance(ufavg, uncertainties.UFloat):
            row += [ufavg.nominal_value, ufavg.std_dev]
        else:
            row += [ufavg, 0]

        resultable.append(row)
    resultable.sortrow()

    return resultable


############################# rpy2 helpers ##################################

def fhtab2dataframe(valuelis, columnames=True, rownames=False):
    """

    create rpy2-R data frame from table or list
    to be used in R

    """

    if isinstance(valuelis, robjects.vectors.DataFrame):
        return valuelis

    elif isinstance(valuelis, fhutils.Table):
        pytab = fhutils.Table('data')
        assert '-' not in valuelis.columnames, valuelis.columnames
        pytab.columnames = valuelis.columnames
        pytab.data = valuelis.data

    else:
        pytab = fhutils.Table('data')
        if columnames:  # if columnames provided extracted from the list
            assert '-' not in valuelis[0], valuelis[0]
            pytab.columnames = valuelis[0]
            pytab.data = valuelis[1:]
        else:  # add arbitrary columnames
            pytab.columnames = ['v' + str(i) for i in range(0, len(valuelis[0]))]
            pytab.data = valuelis

    tablist = []
    for col in pytab.columnames:
        coldata = pytab.getcolumn(col)
#        print (coldata,'coldata',col,'col')
        nv = []
        for ele in coldata:
            if isinstance(ele, list) or isinstance(ele, tuple):
                ele = ele[0]
            if isinstance(ele, int) or isinstance(ele, float):
                nv.append(float(ele))
            elif ele.isdigit():
                nv.append(float(ele))
            elif ele == 'NA':
                nv.append(rinterface_lib.sexp.NARealType())
            else:
                nv.append(fhutils.is_numeric(ele))  # try to convert into most likely type
        if sum([1 for ele in nv if isinstance(ele, float) or isinstance(ele, int)]) < len(nv):
            tablist.append((col, robjects.vectors.StrVector([str(x) for x in nv]))) # enforce str for all elements
#            tablist.append((col, robjects.vectors.StrVector(nv)))
        else:
            tablist.append((col, robjects.vectors.FloatVector(nv)))

    dataframe = robjects.DataFrame(rlc.OrdDict(tablist))
    if rownames:
        dfrmgen = robjects.r('data.frame')
        dataframe = dfrmgen(dataframe, row_names=1)
    return dataframe


def dataframe2fhtab(dataframe):
    table = fhutils.Table()

    colnames = list(dataframe.colnames)
    rownames = list(dataframe.rownames)
    col2data = []
    for cn, col in list(dataframe.items()):
        if isinstance(col, robjects.vectors.FactorVector) is True:
            colevel = tuple(col.levels)
            col = tuple(col)
            ncol = []
            for i in col:
                k = i - 1
                ncol.append(colevel[k])
        else:
            ncol = tuple(col)
        
        col2data.append((cn, ncol))

    col2data.append(('rownames', rownames))
    col2data = dict(col2data)

    table.columnames = ['rownames'] + colnames
    for cname in table.columnames:
        table.data.append(tuple(col2data[cname]))
    table.data = fhutils.pytranspose(table.data)
    return table


def dataframetodic(dataframe):
    dfrmdic = []
    colnames = list(dataframe.colnames)
    rownames = list(dataframe.rownames)
    k = 0
    for row in dataframe.iter_row():

        for i in range(0, len(row)):
            dfrmdic.append(((rownames[k], colnames[i]), row[i][0]))
        k += 1
    return dict(dfrmdic)


def dictorlist(pydic):
    rdic = robjects.vectors.ListVector(pydic)
    return rdic


def rlisttodic(rlist):
    tmp = []
    for ele in list(rlist.items()):
        key = ele[0]
        value = list(ele[1])
        if len(value) == 1:
            value = value[0]
        tmp.append((key, value))
    return dict(tmp)


######### python interface to statistic functions in R ###############

def rpystatinit():
    """
    Init R scripts i.e. load scripts in R environment
    """
    rconsole = rpy2.robjects.r
    srcpath = os.environ.get('FHR')
    rsrc = os.path.join(srcpath, 'rfhstats.R')
    srcfile = ''.join(("source(\'", rsrc, "\')"))
    rconsole(srcfile)
    return rconsole


def executecode(codestring):
    robjects.r(codestring)


def rpydatadescr(numbers):
    rconsole = rpystatinit()
    rdatadescr = rconsole("rdatadescr")
    numbers = [float(ele) for ele in numbers]
    numbers = robjects.vectors.FloatVector(numbers)
    desc = rdatadescr(numbers)
    desc = rlisttodic(desc)
    return desc


def statoverview(valuelis, group='NA', filename='overview_data.txt', gformat='pdf'):
    """
    overview statistics
    R psych::describe which shows:
    item name ,item number, nvalid, mean, sd, 
    median, mad, min, max, skew, kurtosis, se
    """
    rconsole = rpystatinit()
    
    rgeneralstats = rconsole("rgeneralstats")
    dataframe = fhtab2dataframe(valuelis)
    
    from rpy2.robjects.packages import importr
    
    grdevices = importr('grDevices')
    grdevices.pdf(file=fhutils.renamefilename(filename, suffix=gformat))

    gdic = {'NA': rinterface_lib.sexp.NARealType()}
    group = gdic.get(group, group)

    data = rgeneralstats(data=dataframe, group=group)
    grdevices.dev_off()
    out = open(filename, 'w')
    out.write(str(data))
    out.close()


def pysummary(valuelis, measurevar='', groupvars='', outputformat='long', na_rm=False, conf_interval=.95):
    """
    Summarize data with summarySE function

    """

    rconsole = rpystatinit()
    rsummaryse = rconsole("summarySE")
    dataframe = fhtab2dataframe(valuelis)
    if isinstance(groupvars, tuple) is True or isinstance(groupvars, list) is True:
        groupvars = robjects.vectors.StrVector(tuple(groupvars))

    aggregate = rsummaryse(data=dataframe, measurevar=measurevar, groupvars=groupvars, na_rm=na_rm,
                          conf_interval=conf_interval)
    if outputformat == 'wide':
        rlongtowide = robjects.r("rlongtowide")
        measurevars = robjects.vectors.StrVector(tuple((measurevar, 'N', 'sd', 'sum', 'min', 'max')))
        aggregate = rlongtowide(aggregate, measurevars, groupvars)

    aggregate = dataframe2fhtab(aggregate)

    return aggregate


def pycorrelation(valuelis, numericvars=list(), filename='correlation_data.txt', method="pearson",
                  adjust="holm"):
    """
    correlation test using R function 
    """
    rconsole = rpystatinit()
    rcorrelation = rconsole("rcorrelation")
    dataframe = fhtab2dataframe(valuelis)
    data = rcorrelation(data=dataframe, numericvars=robjects.vectors.StrVector(tuple(numericvars)), method=method,
                        adjust=adjust)

    out = open(filename, 'w')
    out.write(str(data))
    out.close()


#### R based statistics ######

class Fhdata(object):
    """
    given a list with data:
    
    - provides access to standard statistics
    - allows to filter outliers
    - can return ufloat with sd or sem
    - reports outliers/statistics
    
    """

    def __init__(self, data=[]):
        self.data = data
        self.mean = False
        self.sd = False
        self.sem = False
        self.median = False
        self.mad = False
        self.nswil = False
        self.n = len(self.data)
        self.outliers = []

    def __add__(self, other):
        data = self.data + other.data
        return Fhdata(data)


    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)


    def rstats(self):
        """
        calculate summary statistics
        """
        if len(self.data)>1:
            descr = rpydatadescr(list(set(self.data)))
            self.mean = numpy.mean(self.data)
            self.sd = numpy.std(self.data, ddof=1)
            self.sem = scipy.stats.sem(self.data)
            self.median = numpy.median(self.data)
            self.mad = descr['nmad']
            self.nswil = descr['nswil']
            self.n = len(self.data)
        elif len(self.data)==1:
            self.mean = self.data[0]
            self.sd = 0.0
            self.sem = False
            self.median = False
            self.mad = False
            self.nswil = False
            self.n = len(self.data)
        else:
            self.mean = False
            self.sd = False
            self.sem = False
            self.median = False
            self.mad = False
            self.nswil = False
            self.n = False
            
            


    def filteroutliers(self):
        rconsole = rpystatinit()
        outlieridx = []
        filtered = []
        outlieridentified = rconsole("outlieridentified")
        rdata = tuple([float(ele) for ele in self.data])
        nonnull = sum([1 for ele in rdata if ele == 0.0])

        # only more than three rep and less than 30 and non null not all
        if 3 <= len(rdata) <= 30 and nonnull != len(rdata):
            rvector = robjects.vectors.FloatVector(rdata)
            outlis = outlieridentified(rvector)
            filtered = outlis[0]
            outlieridx = outlis[1]

        if outlieridx and filtered:

            tdata = []
            odata = []
            for k in range(0, len(self.data)):
                if k + 1 in [i for i in outlieridx]:
                    odata.append(self.data[k])
                else:
                    tdata.append(self.data[k])

            outdata = list(tdata)

            if len([ele for ele in filtered if ele not in [t for t in outdata]]) != 0:
                print([ele for ele in outdata])
                print(filtered)
                raise NameError('unequal filtering')
            elif len(outdata) > len(filtered):
                raise NameError('more data than given')
        else:
            outdata = self.data
            odata = []

        self.data = list(outdata)
        self.outliers = list(odata)
        self.n = len(self.data)
        self.rstats()  # recalculate stats for filtered data

    def getufloat(self, dosem=False):
        if dosem is True:
            ev = self.sem
        else:
            ev = self.sd

        if isinstance(ev, float):
            m = ufloat(self.mean, ev)
        else:
            m = self.mean

        return m

    def reportdata(self):
        info = [[ele, 'o'] for ele in self.data] + [[ele, '*'] for ele in self.outliers]
        return info

    def reportsummary(self):
        tu = [self.mean, self.sd, self.sem, self.median, self.mad, self.n, self.nswil]
        return tu


def removeoutliers(datalis, dataidx):
    """
    removes outliers of data
    """
    rconsole = rpystatinit()
    outlieridentified = rconsole("outlieridentified")
    rdata = tuple([ele[dataidx] for ele in datalis])

    nonnull = sum([1 for ele in rdata if ele == 0.0])
    # only more than three rep and less than 30 and non null not all
    if 3 <= len(rdata) <= 30 and nonnull != len(rdata):
        rvector = robjects.vectors.FloatVector(rdata)
        outlis = outlieridentified(rvector)
        filtered = outlis[0]
        outlieridx = outlis[1]
    else:
        return datalis, []

    if outlieridx and filtered:

        tdata = []
        odata = []
        for k in range(0, len(datalis)):
            if k + 1 in [i for i in outlieridx]:
                odata.append(datalis[k])
            else:
                tdata.append(datalis[k])

        outdata = list(tdata)

        if len([ele for ele in filtered if ele not in [t[dataidx] for t in outdata]]) != 0:
            print([ele[dataidx] for ele in outdata])
            print(filtered)
            raise NameError('unequal filtering')
        elif len(outdata) > len(filtered):
            raise NameError('more data than given')
    else:
        outdata = datalis
        odata = []
    # if len(datalis) != len(outdata):
    #     print '######>>>>> outlier removed'
    return outdata, odata


def shapirowillk(valuelist):
    rconsole = rpystatinit()
    
    rshapirowillk = rconsole('rshapirowillk')
    pv = rshapirowillk(robjects.vectors.FloatVector(valuelist))
    return pv


def pynormtest(valuelis, numericvars=list(), filename='normtest_data.txt', gformat='pdf'):
    rconsole = rpystatinit()
    rnormcheck = rconsole("rnormcheck")
    dataframe = fhtab2dataframe(valuelis)

    from rpy2.robjects.packages import importr
    grdevices = importr('grDevices')
    grdevices.pdf(file=fhutils.renamefilename(filename, suffix=gformat))
    data = rnormcheck(data=dataframe, numericvars=robjects.vectors.StrVector(tuple(numericvars)))
    grdevices.dev_off()

    out = open(filename, 'w')
    out.write('\n'.join(
        ['######## glvma fit results ########', str(data[0]), '######## LM-fit results ########', str(data[1])]))
    out.close()


def pynlsfit(valuelis, formulastr='', startvalues=list(), filename='nlsfit.txt', gformat='pdf'):
    """
    nonlinear fit of function to data
    """
    rconsole = rpystatinit()
    rnonlinfit = rconsole("rnonlinfit")
    dataframe = fhtab2dataframe(valuelis)

    from rpy2.robjects.packages import importr

    grdevices = importr('grDevices')
    graphplotfile = fhutils.renamefilename(filename, suffix=gformat)
    grdevices.pdf(file=graphplotfile)
    nlfit = rnonlinfit(data=dataframe, formulastr=formulastr, startvalues=robjects.ListVector(dict(startvalues)))
    grdevices.dev_off()

    nlfit = rlisttodic(nlfit)
    return nlfit

#########################################################################

def wavgstd(values, asufloat=False):
    """

    Returns the weighted average and standard deviation.
    values, weights -- Numpy ndarrays with the same shape.

    """

    values, weights = checkufloat(values)

    if weights and asufloat is True:
        weights = numpy.array(weights)
        values = numpy.array(values)
        average = numpy.average(values, weights=weights)
        variance = numpy.dot(weights, (values - average) ** 2.0) / weights.sum()  # Fast and numerically precise

        if asufloat:
            ufstdev = uncertainties.sqrt(variance)
            ufvalue = ufloat((average, ufstdev))

        else:
            ufvalue = (average, uncertainties.sqrt(variance))

    else:
        if asufloat:
            if isinstance(values[0], uncertainties.UFloat):
                ufvalue = numpy.mean(values)
            else:
                ufvalue = ufloat(str(numpy.mean(values)))  # assign minimal error if no std deviation

        elif asufloat is False:
            ufvalue = (numpy.mean(values), numpy.std(values, ddof=1))

        else:
            raise NameError('ILL DEFINED VARIABLES')

    return ufvalue


def logratio2foldchange(logratio):
    if logratio in ('-inf', float('-inf')):
        print('WARNING -inf value set to 10E-10')
        logratio = -10E-10

    elif logratio == 'inf':
        logratio = float('inf')
    else:
        logratio = float(logratio)
    retval = 2 ** logratio

    if retval < 1:
        val = -1.0 / retval
    else:
        val = retval
    return val


def foldchange2logratio(foldchange):
    if foldchange < 0.0:
        val = 1.0 / -foldchange
    else:
        val = foldchange
    retval = numpy.log2(val)
    return retval


def bin_values(lis, bins, relative=False):
    bins = list(bins)
    bins.sort()
    lis.sort()
    maxrb = max(bins)
    minlb = min(bins)
    maxval = max(lis)
    minval = min(lis)
    bintup = list(zip(bins, bins[1:]))
    if minval < minlb:
        lowerunder = (minval, minlb)
        bintup.insert(0, (minval, minlb))
    else:
        lowerunder = ()
    if maxval > maxrb:
        upperover = (maxrb, maxval)
        bintup.insert(0, (maxrb, maxval))
    else:
        upperover = ()

    bincount = []
    maxborder = bintup[len(bintup) - 1]
    minborder = bintup[0]

    for num in lis:

        for lb, rb in bintup:
            if lb < num <= rb:
                bincount.append(((lb, rb), num))
                break

            elif num > maxrb:
                bincount.append((maxborder, num))
                break

            elif num <= minlb:
                bincount.append((minborder, num))
                break

    bincountdic = dict([(k, len(v)) for k, v in list(fhutils.keylis2dic(bincount).items())])

    bincount = [(k, bincountdic.get(k, 0)) for k in bintup]
    bincount = [(str(k[0]) + '-' + str(k[1]), v) for k, v in bincount if k not in (lowerunder, upperover)]
    lowerout = bincountdic.get(lowerunder, 0)
    upperout = bincountdic.get(upperover, 0)
    if lowerout != 0:
        bincount.insert(0, ('<' + str(lowerunder[1]), lowerout))
    if upperout != 0:
        bincount.append(('>' + str(upperover[0]), upperout))

    check = sum([ele[1] for ele in bincount])
    if check != len(lis):
        print('\t'.join(('input:', lis, '\n', 'bins:', bins, '\n', 'binned', bincount, '\n', len(lis), check)))
        raise NameError('MISSING OR TO MANY NUMBERS IN BINCOUNT')
    if relative:
        bincount = [(bino[0], (100.0 / sum([ele[1] for ele in bincount])) * bino[1]) for bino in bincount]
    print('\n'.join(['total count (100%): ' + str(sum([ele[1] for ele in bincount]))] + [
        bino[0] + ' percent: ' + str((100.0 / sum([ele[1] for ele in bincount])) * bino[1]) for bino in bincount]))

    return bincount


################ comparison among groups treatments ####################

def pywelchttest(mean1, sd1, n1, mean2, sd2, n2, alternative="two.sided", mu=0, var_equal=False, conf_level=0.95):
    rconsole= rpystatinit()
    rwelchtest = rconsole("rwelchtest")
    pv = rwelchtest(mean1, sd1, n1, mean2, sd2, n2, alternative=alternative, mu=mu, var_equal=var_equal,
                    conf_level=conf_level)
    return pv


def pyanova(table, formula, term, filename='anovaimage', gformat='pdf'):
    
    from rpy2.robjects.packages import importr
    rconsole=rpystatinit()
    ranova = rconsole("ranova")

    grdevices = importr('grDevices')
    grdevices.pdf(file=fhutils.renamefilename(filename, suffix=gformat))

    dataframe = fhtab2dataframe(table)
    results = ranova(data=dataframe, formulastring=formula, term=term)
    aovw = dataframe2fhtab(results[0])
    tukey = dataframe2fhtab(results[1])

    grdevices.dev_off()

    return aovw, tukey


def pykruskalwallis(table, formula, term, filename='kruskalimage', gformat='pdf'):
    rconsole=rpystatinit()
    rkruskal = rconsole("rkruskal")

    dataframe = fhtab2dataframe(table)
    results = rkruskal(data=dataframe, formulastring=formula, term=term)
    results = dataframe2fhtab(results)
    newtab = fhutils.Table('kruskal')
    newtab.columnames = ['group1', 'group2', 'p-value']
    for row in results:
        for i in range(1, len(results.columnames)):
            newtab.append((row[0], results.columnames[i], row[i]))

    return newtab

def pyrmultcomp(table,measurevar,groupvar,contrastsvector = 'none'):
    rconsole=rpystatinit()
    rmultcomp = rconsole("rmultcomp")
    dataframe = fhtab2dataframe(table)
    contrastsvector = tuple([ "{tu1} - {tu2} = 0".format(tu1 = tu[0],tu2=tu[1]) for tu1,tu2 in contrastsvector])
    contrastsvector = robjects.vectors.StrVector(contrastsvector)
    results = rmultcomp(data=dataframe, measurevar=measurevar,groupvar=groupvar, contrastsvector=contrastsvector)
    results = dataframe2fhtab(results)
    newtab = fhutils.Table('multcomp')
    newtab.columnames = ['group1', 'group2', 'p-value']
    for row in results:
        print(row)
    return newtab

def pyrnparcomp(table,measurevar,groupvar):
    rconsole=rpystatinit()
    rnparcomp = rconsole("rnparcomp")
    dataframe = fhtab2dataframe(table)
    results = rmultcomp(data=dataframe, measurevar=measurevar,groupvar=groupvar)
    results = dataframe2fhtab(results)
    newtab = fhutils.Table('nparcomp')
    newtab.columnames = ['group1', 'group2', 'p-value']
    for row in results:
        print(row)
    return newtab

def pairwisettest(datatable,padjmethod="none"):
    """
    all against all comparison
    using t-test for anova without 
    interaction significance
    
    """
    dataframe = fhtab2dataframe(datatable)
    pass
