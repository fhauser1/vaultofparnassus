# -*- encoding: utf-8 -*-

"""GENERAL FUNCTIONS FOR DATE TIME LABELLING; LOGGING; EXECUTION OF OTHER PROGRAMS"""

from future import standard_library
standard_library.install_aliases()
from builtins import map
from builtins import zip
from builtins import str
from builtins import range
from builtins import object
from time import localtime, strftime
import subprocess
import itertools
import logging.handlers
import sys

try:
    import pickle as pickle
except:
    import pickle

import tempfile

import operator
from itertools import groupby
import csv
import collections
import copy
import numpy
import logging.config

import os
import re
import yaml
import pandas

# ################# DATE TIME TAGS #####################


def dtk(formatstr="%d%b%Y%H%M%S"):
    formatted = strftime(formatstr, localtime())
    return str(formatted)


def is_numeric(lit):
    """
    Return value of numeric literal string or original string
    http://rosettacode.org/wiki/Determine_if_a_string_is_numeric#Python

    """

    if not lit:  # give empty stuff back
        return lit

    if isinstance(lit, int) or isinstance(lit, float):  # return value if already float or int
        return lit

    if lit.isdigit():
        return int(lit)

    # Hex/Binary
    if lit[0] == '-':
        litneg = lit[1:]
    else:
        litneg = lit

    if not litneg:
        return lit

    if litneg[0] == '0':
        if litneg[1] in 'xX':
            return int(lit, 16)
        elif litneg[1] in 'bB':
            return int(lit, 2)
        else:
            try:
                return int(lit, 8)
            except ValueError:
                pass

    # Int/Float/Complex
    try:
        return int(lit)
    except ValueError:
        pass
    try:
        return float(lit)
    except ValueError:
        pass
    return lit


def unifiobj(filepath):
    dirname, filename = os.path.split(filepath)
    prefix, suffix = os.path.splitext(filename)
    fileobj = tempfile.NamedTemporaryFile(delete=True, suffix=suffix, prefix=prefix + "_", dir=dirname)
    return fileobj


def renamefilename(filename, prefix=None, midtag=None, suffix=None, extension=None):
    if isinstance(filename, list):
        filename = filename[0]
        midtag += 'merge'
    pathfull, filename = os.path.split(filename)
    corename, oldsuffix = os.path.splitext(filename)

    newfilename = ''
    if prefix:
        newfilename += prefix
    newfilename += corename
    if midtag:
        newfilename += midtag
    if suffix:
        newfilename += '.' + suffix
    else:
        newfilename += oldsuffix
    if extension:
        newfilename += extension
    if pathfull:
        newfilename = os.path.normpath(pathfull + '/' + newfilename)
    else:
        newfilename = newfilename
    return newfilename


def splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path:  # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts


# counts the element in a list of strings and then returns list with tuples (count,number of counts)

def liscount(lis):
    counts = [lis.count(a) for a in set(lis)]
    freqcount = [(a, counts.count(a)) for a in set(counts)]
    return freqcount


def liselecount(lis):
    """count elements in list"""
    liset = set(lis)
    tulis = tuple(lis)
    new = [(a, tulis.count(a)) for a in liset]
    return new


def liselecountf(lis, filename):
    """count elements in list and write to file"""
    out = open(filename + '.txt', 'w')
    liset = set(lis)
    tulis = tuple(lis)
    new = [(a, tulis.count(a)) for a in liset]
    for st in new:
        out.write('\t'.join([str(x) for x in st]) + '\n')
    out.close()
    return new


def mergelist(lis):
    newlis = []
    for tu in lis:
        newlis += list(tu)
    return newlis


def filterconsecutive(mtchlis, minlength=1):
    confirmed = []
    for tu in groupby(enumerate(mtchlis), lambda i_x: i_x[0] - i_x[1]):
        consecutive = list(map(operator.itemgetter(1), tu[1]))
        if len(consecutive) >= minlength:
            confirmed.append((min(consecutive), max(consecutive)))

    return confirmed


def tryint(s):
    try:
        return int(s)
    except ValueError:
        return s


def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [tryint(c) for c in re.split('([0-9]+)', s)]


def natsorted(l):
    """ Sort the given list in the way that humans expect.
    """
    l.sort(key=alphanum_key)
    return l


def flatten(listoflists):
    """Flatten one level of nesting"""
    merged = list(itertools.chain.from_iterable(listoflists))

    return merged


def fullflatten(listoflists):
    for el in listoflists:
        if isinstance(el, collections.Iterable) and not isinstance(el, str) and not isinstance(el, str):
            for sub in fullflatten(el):
                yield sub
        else:
            yield el


def uniquify(seq, idfun=None):
    # order preserving
    if idfun is None:
        def idfun(x):
            return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        if marker in seen:
            continue
        seen[marker] = 1
        result.append(item)
    return result


# ############## array list manipulation ###############

def transpose_raw(lists):
    if not lists:
        return []
    return list(map(lambda *row: list(row), *lists))


def transpose(lists, defval=0):
    if not lists:
        return []
    return list(map(lambda *row: [elem or defval for elem in row], *lists))


def pytranspose(listarray):
    return list(map(list, zip(*listarray)))


def grouper(n, iterable, fillvalue=None):
    """grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"""
    args = [iter(iterable)] * n
    return list(itertools.zip_longest(fillvalue=fillvalue, *args))


# lis=[('a1','b','c'),('a','b2','c'),('a','b','c3'),('a','b4','c'),('a','b5','c'),('a','b6','c')]
# print grouper(4,lis)


def setup_logging(logconfig='', loglevel='INFO', logfolder=''):
    """
    Setup logging configuration
    
    """

    if os.path.isfile(logconfig):
        # os.path.join(os.path.split(__file__)[0],'logging.yaml')
        config = yaml.load(logconfig.read())
        logging.config.dictConfig(config)
    else:
        LOGGING = {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'verbose': {
                    'format': '%(levelname)s %(asctime)s %(module)s %(funcName)s %(message)s'
                },
                'simple': {
                    'format': '%(levelname)s %(asctime)s %(message)s'
                },
            },
            # 'filters': {
            # 'special': {
            # '()': 'project.logging.SpecialFilter',
            # 'foo': 'bar',
            # }
            # },
            'handlers': {

                'null': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stdout',
                    'formatter': 'simple',
                },
                'console': {
                    'level': 'INFO',
                    'class': 'logging.StreamHandler',
                    'formatter': 'simple'
                },
                'error_file_handler': {'formatter': 'verbose',
                                       'backupCount': 5,
                                       'level': 'ERROR',
                                       'encoding': 'utf8',
                                       'class': 'logging.handlers.RotatingFileHandler',
                                       'maxBytes': 1000000,
                                       'filename': os.path.join(logfolder, 'errors.log')
                },
                'info_file_handler': {'formatter': 'verbose',
                                      'backupCount': 5,
                                      'level': 'INFO',
                                      'encoding': 'utf8',
                                      'class': 'logging.handlers.RotatingFileHandler',
                                      'maxBytes': 1000000,
                                      'filename': os.path.join(logfolder, 'info.log')
                },
            },

            'loggers': {
                'fhstandard': {
                    'handlers': ['console', 'info_file_handler', 'error_file_handler'],
                    'propagate': True,
                    'level': loglevel,
                },
            }
        }

        logging.config.dictConfig(LOGGING)

    

def execwrapper(command, pipe=False, info_message='Info ', error_message='Error ', logname='fhstandard'):
    """wrapper for all the commandline functions - should catch all the errors properly """

    if pipe:
        retcode = execpipe(command=command, info_message=info_message, error_message=error_message, logname=logname)
    else:
        retcode = execcommand(command, info_message='Info ', error_message='Error ', logname=logname)
    return retcode


def execcommand(command, info_message='Info ', error_message='Error ', logname='fhstandard'):
    retcode = 999
    logger = logging.getLogger(logname)

    try:
        retcode = subprocess.call(command, shell=True)
        if retcode < 0:
            emessage = error_message + u"Error " + command + u" was terminated by signal: " + str(
                retcode)
            logger.error('\n'.join((emessage, command)))
            return retcode
        elif retcode > 0:
            emessage = error_message + u"Error " + command + u" stopped with signal: " + str(retcode)
            logger.error('\n'.join((emessage, command)))
            return retcode
        else:
            imessage = info_message + u";Info " + command + u" returned " + str(retcode)
            logger.info(imessage)
            return retcode

    except OSError as e:
        emessage = error_message + u"; Execution of " + command + u" failed: " + str(e)
        logger.error('\n'.join((emessage, command)))
        return retcode


def execpipe(command, info_message='Info ', error_message='Error ', logname='fhstandard'):
    logger = logging.getLogger(logname)

    # command = shlex.split(command)
    # child = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell = False).communicate()
    child = subprocess.Popen(str(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
    stdout, stderr = child
    if stderr:
        emessage = error_message + "Error " + command + " stopped with: " + str(stderr)
        logger.error('\n'.join((emessage, command)))
    else:
        infomessage = info_message + "Command run - sending pipe"
        logger.info(infomessage)
    return stdout



def folderremove(folderpath):
    command = 'rm -r '+folderpath
    execcommand(command)


# ############### DICTIONARY METHODS ############################

from collections import defaultdict


def keylis2dic(tulis):
    """
    
    dictionary with key to list to avoid eliminating multiple mapping
    
    """
    d = defaultdict(list)
    for x, y in tulis:
        d[x].append(y)
    return d


def keylis2shelve(tulis, filename):
    import shelve

    d = shelve.open(filename, writeback=True)
    for x, y in tulis:
        d.setdefault(x, []).append(y)
    d.sync()
    return d


def dict_create(filename, startpos, keypos, valpos, true='false'):
    dic = {}
    infolis = []
    infi = open(filename, 'rU')
    inline = infi.readlines()
    for i in range(startpos, len(inline)):
        vcol = inline[i].split('\t')
        key = vcol[keypos].strip()
        key = key.split('.')[0]
        value = vcol[valpos].strip()
        dic[key] = value
        infolis.append((key, value))
    infi.close()

    if true == 'true':
        return dic, infolis
    else:
        return dic


def dict_create_2(filename, startpos, keypos, valpos, true='false'):
    dic = {}
    infolis = []
    infi = open(filename, 'rU')
    inline = infi.readlines()
    infi.close()
    for i in range(startpos, len(inline)):
        vcol = inline[i].split('\t')
        key = vcol[keypos].strip()
        value = vcol[valpos].strip()
        dic[key] = value
    infi.close()
    if true == 'true':
        return dic, infolis
    else:
        return dic


def invert_dict_fast(d):
    return dict(zip(iter(d.values()), iter(d.keys())))


def invert_listdic(d):
    inv = {}
    for k, v in d.items():
        v = list(set(v))
        if len(v) > 1:
            for nk in v:
                inv.setdefault(nk, []).append(k)
        else:
            nk = v[0]
            inv.setdefault(nk, []).append(k)
    inv = dict([(k, v) if len(v) > 1 else (k, v[0]) for k, v in list(inv.items())])
    return inv


def dictinvert(d):
    inv = {}
    if [1 for ele in list(d.values()) if isinstance(ele, list)] or [1 for ele in list(d.values()) if isinstance(ele, tuple)]:
        inv = invert_listdic(d)
        return inv

    elif len(set(d.keys())) == len(list(d.keys())) and len(set(d.values())) == len(list(d.values())):
        inv = invert_dict_fast(d)

    else:
        for k, v in d.items():
            keys = inv.setdefault(v, [])
            keys.append(k)
    return inv


def dicwriter(dic, filenam):
    tgf = open(filenam + dtk() + '.txt', 'w')
    items = list(dic.items())
    tgf.write('field_1' + '\t' + 'field_2' + '\n')
    for i in range(0, len(items)):
        tgf.write(items[i][0] + '\t' + str(items[i][1]) + '\n')
    tgf.close()


def dicdump(dic, filename):
    with file(filename, 'w') as tgtfi:
        pickle.dump(dic, tgtfi)


def dicld(filename, new=False):
    if os.path.isfile(filename) is False and new == True:
        dicdump({}, filename)
    with open(filename, 'rb') as difi:
        dic = pickle.load(difi)
    return dic


# #### YAML #####

def yamldump(dic, filename):
    with open(filename, 'w') as f:
        yaml.dump(dic, f)


def yamlld(filename):
    if os.path.isfile(filename) is False:
        dic = {}
        yamldump(dic, filename)
    else:
        with open(filename, 'r') as f:
            dic = yaml.load(f)
    return dic



class ConfigStore(object):
    """
    Standard container for storing 
    usual configurations
    Helpful or obstruction ???
    """

    def __init__(self, configdic):
        super(ConfigStore, self).__init__()
        self.configdic = configdic
        if 'config' in configdic:
            self.param = self.configdic['config']
        else:
            self.param = self.configdic
        if 'data' in configdic:
            self.data = self.configdic['data']
        else:
            self.data = self.configdic

    def __str__(self):
        strep = ''
        for k, v in list(self.__dict__.items()):
            strep += '\t' + str(k) + '\t' + str(v) + '\n'
        return strep

    @property
    def projectdir(self):
        if 'projectdir' in self.param:
            projectdir = self.param['projectdir']
        else:
            projectdir = 'NA'
        return projectdir

    @property
    def resultdir(self):
        resultdir = os.path.join(self.projectdir, self.param['result'])
        return resultdir

    @property
    def datadir(self):
        datadir = os.path.join(self.projectdir, self.param['data'])
        return datadir


def loadconfig(yamlfile):
    config = yamlld(yamlfile)
    confobj = ConfigStore(config)
    return confobj


# ###### SIMPLE WRAPPER FOR pandas #######################

class PDframe(object):
    """
    
    very simple dataframe wrapper
    due to inability to inherit from pandas
    dataframe class more an overlay of functions
    
    
    """

    def __init__(self, name=''):
        self.name = name
        self.data = pandas.DataFrame

    def __iter__(self):
        return iter(self.data.iterrows())


    def read(self, filename, sep='\t', quotechar='\"', columnames=False, rownames=False, donumeric=False,
             dounicode=False):

        if rownames is True:
            index_col = 0
        else:
            index_col = None

        if columnames is True:
            header = 0
        else:
            header = None

        with open(filename, 'r') as infi:
            try:
                dialect = csv.Sniffer().sniff(infi.read(1024))
                infi.seek(0)
                dialect.delimiter = sep
                self.data = pandas.read_table(infi, sep=sep, header=header, index_col=index_col)


            except:
                infi.seek(0)
                self.data = pandas.read_table(infi, sep=sep, header=header, index_col=index_col)
        return self

    def iterrows(self):
        for row in self.data.iterrows():
            yield row


# ###### SIMPLE FUNCTIONS FOR READING WRITING TABLES #######################


class Table(object):
    """docstring for TableIO"""

    def __init__(self, name=''):
        self.data = []
        self.columnames = []
        self.rownames = []
        self.index = 0
        self.name = name
        self.isyaml = False

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __str__(self):
        strep = '\t'.join([str(x) for x in self.columnames]) + '\n'
        for row in self.data:
            strep += '\t'.join([str(x) for x in row]) + '\n'
        return strep

    def __getitem__(self, key):
        return self.data[key]

    def __add__(self, lis):
        self.data += lis
        return self

    def iclone(self):
        newself = copy.deepcopy(self)
        return newself

    def merge(self, tab, by_x, by_y):

        valuecolumns = list(tab.columnames)
        valuecolumns.remove(by_y)

        placeholder = ['NA' for ele in valuecolumns]
        valuedic = dict([(row[0], row[1:]) for row in tab.getcolumn([by_y] + valuecolumns)])
        assert len(valuedic) == len(tab), 'Duplicates in matching keys - table to add needs unique keys to match'

        for row_tab1 in self.data:
            assert len(row_tab1) == len(self.columnames), str(row_tab1) + '\n' + str(len(row_tab1)) + '\n' + str(
                len(self.columnames)) + '\n' + str(self.columnames)
            rowdic = dict(list(zip(self.columnames, row_tab1)))
            key1 = rowdic[by_x]
            matchrow = valuedic.get(key1, [])
            if matchrow:
                row_tab1 += matchrow
            else:
                row_tab1 += placeholder

        if tab.columnames and self.columnames:
            adcol = tab.columnames
            adcol.remove(by_y)
            self.columnames += adcol

        return self

    def iterrows(self):

        for row in self.data:
            if self.columnames:
                assert len(row) == len(self.columnames), str(row) + '\n' + str(len(row)) + '\n' + str(
                    len(self.columnames)) + '\n' + str(self.columnames)
                rowdic = dict(list(zip(self.columnames, row)))

            else:
                rowdic = dict(list(zip([i for i in range(0, len(row))], row)))

            yield rowdic

    def getcolumn(self, column):

        pos = []
        data = [row for row in self.data if row]  # filter empty rows out
        for row in data:
            assert len(row) == len(self.columnames), str(row) + '_' + str(self.columnames) + '_' + str(
                len(row)) + '_' + str(len(self.columnames))
        if isinstance(column, list) is False and isinstance(column, tuple) is False:
            column = [column, ]

        for ele in column:
            if isinstance(ele, str) and ele in self.columnames:
                pos.append(self.columnames.index(ele))
            # elif isinstance(ele, str) and ele in self.columnames:
            #     pos.append(self.columnames.index(ele))

            elif isinstance(ele, int) and 0 <= ele <= len(self.columnames):
                pos.append(ele)
            else:
                raise NameError('UNKNOWN COLUMN - select either index or columname' + str(ele))

        npdata = numpy.array(data)
        tmpdata = npdata[:, tuple(pos)]
        tmpdata = [tuple(ele) for ele in tmpdata.tolist()]  # tolist does not keep row as tuple

        return tmpdata

    def sortrow(self, idx=None):
        dat = list(self.data)
        if idx:
            if isinstance(idx,tuple):
                dat.sort(key=operator.itemgetter(*idx))
            else:
                dat.sort(key=operator.itemgetter(idx))
        else:
            dat.sort()
        self.data = list(dat)

    def append(self, lis):
        self.data.append(lis)


    def write(self, filename, sep='\t', columnames=True):
        out = open(filename, 'w')
        if self.columnames and columnames == True:
            out.write(sep.join([str(x) for x in self.columnames]) + '\n')
        out.write('\n'.join([sep.join([str(col) for col in row]) for row in self.data]))
        out.close()

    def write_html(self, filename):
        out = open(filename, 'w')
        out.write("""<!DOCTYPE html>
        <html>
        <head>
        <link rel="stylesheet" type="text/css" href="http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/css/jquery.dataTables.css">
        <script src="http://code.jquery.com/jquery-1.9.1.js"></script>
        <script src="http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/jquery.dataTables.js"></script>
        <script type="text/javascript" charset="utf-8">
        $(document).ready(function() {
        $('#pydata').dataTable();
        } );
        </script>
        </head>\n<body>\n<table id="pydata">\n""")

        if self.columnames:
            out.write(
                '<thead>\n<TR>' + ''.join(['<TH>' + str(x) + '</TH>' for x in self.columnames]) + '</TR></thead>\n')

        out.write('<tbody>\n<TR>' + '</TR>\n<TR>'.join(
            [''.join(['<TD>' + str(col) + '</TD>' for col in row]) for row in self.data]))
        out.write("""\n</tbody>\n</table>
      
        </body>\n</html>""")

        out.close()

    def read(self, filename, sep='\t', quotechar='\"', columnames=False, rownames=False, donumeric=False,
             dounicode=False):

        with open(filename, 'r') as infi:

            try:
                dialect = csv.Sniffer().sniff(infi.read(1024))
                infi.seek(0)
                dialect.delimiter = sep
                csvhandle = csv.reader(infi, dialect=dialect)

            except:
                infi.seek(0)
                csvhandle = csv.reader(infi, delimiter=sep, quotechar=quotechar)

            if columnames:
                self.columnames = [ele.strip() for ele in next(csvhandle)]
            elif isinstance(columnames, list) or isinstance(columnames, tuple):
                self.columnames = columnames
                next(csvhandle)

            self.data = [[ele.strip() for ele in row] for row in csvhandle if row]

        if donumeric:
            self.data = [[is_numeric(col) for col in row] for row in self.data]

        if dounicode:
            self.data = [[str(str(col), errors='ignore') for col in row] for row in self.data]

        if rownames:
            self.rownames = [row[0] for row in self.data]
            self.data = [row[1:] for row in self.data]
            self.columnames = list(self.columnames[1:])

        if not self.columnames:
            self.columnames = [i for i in range(0, len(self.data[0]))]

        return self

    def parse(self, filename, sep='\t', quotechar='\"', columnames=False, rownames=False, filtercolumn=None,
              filtervalue=False):

        if filtervalue:
            if isinstance(filtervalue, list) is False and isinstance(filtervalue, tuple) is False:
                filtervalue = [filtervalue, ]

        with open(filename, 'r') as infi:
            try:
                dialect = csv.Sniffer().sniff(infi.read(1024))
                infi.seek(0)
                dialect.delimiter = sep
                csvhandle = csv.reader(infi, dialect=dialect)

            except:
                infi.seek(0)
                csvhandle = csv.reader(infi, delimiter=sep, quotechar=quotechar)

            if columnames:
                self.columnames = [ele.strip() for ele in next(csvhandle)]
            elif isinstance(columnames, list) or isinstance(columnames, tuple):
                self.columnames = columnames
                next(csvhandle)

            for row in csvhandle:
                row = [ele.strip() for ele in row]
                if filtercolumn:
                    assert len(row) == len(self.columnames), 'ERROR COLUMNAMES ROW MATCHING'
                    col2val = dict(list(zip(self.columnames, row)))
                    if col2val[filtercolumn] not in filtervalue:
                        continue
                yield row

    def transpose(self):
        tmp = self.data
        tmp.insert(0, self.columnames)
        tmp = list(map(list, zip(*tmp)))
        self.columnames = tmp.pop(0)
        self.data = tmp

    def filterrow(self, filterinfo):
        """
        filterinfo: tuple with columname and tuple with filterarguments
        only one filter allowed i.e run repeatedly
        NOTE this returns now a new table 
        which is an exact copy of the original table
        except the data are filtered out
        
        """

        column, filtervalue = filterinfo

        data = []

        if isinstance(filtervalue, list) is False and isinstance(filtervalue, tuple) is False:
            filtervalue = [filtervalue, ]
        for row in self.iterrows():

            if row[column] in filtervalue:
                data.append([row[col] for col in self.columnames])
            else:
                continue

        newtable = Table(self.name)
        newtable.data = data
        newtable.columnames = self.columnames
        newtable.rownames = self.rownames
        newtable.index = self.index
        newtable.isyaml = False
        return newtable


    def filtercolumn(self, filterinfo):
        newdata = self.getcolumn(filterinfo)
        newtable = self.iclone()
        newtable.data = newdata
        newtable.columnames = filterinfo
        return newtable


    def gettablematrix(self):
        datalis = []
        for i in range(0, len(self.rownames)):
            for c in range(0, len(self.columnames)):
                ri = self.rownames[i]
                ci = self.columnames[c]
                datapt = self.data[i][c]
                datalis.append(((ri, ci), datapt))

        self.data = dict(datalis)

        return self.data

    def puttablematrix(self):
        rownames = []
        colnames = []
        for k, v in list(self.data.items()):
            rownames.append(k[0])
            colnames.append(k[1])
        colnames = list(set(colnames))
        rownames = list(set(rownames))
        colnames.sort()
        rownames.sort()
        newdata = []

        for r in rownames:
            tmp = [r]
            for c in colnames:
                tmp.append(self.data[(r, c)])
            newdata.append(tuple(tmp))
        self.data = newdata
        self.columnames = ['rc'] + colnames


    def addrowindex(self,indexcolumn = 'idx'):
        data = []
        i = 1
        for row in self.data:
            nrow = list(row)
            nrow.insert(0, i)
            data.append(tuple(nrow))
            i += 1
        self.data = data
        self.columnames = tuple([indexcolumn] + list(self.columnames))


    def convert2yaml(self, keycolumn):
        yamldata = []
        for row in self.data:
            row = dict(list(zip(self.columnames, row)))
            key = row[keycolumn]
            val = dict(row)
            del val[keycolumn]
            yamldata.append((key, val))

        self.data = dict(yamldata)
        self.isyaml = True
        return self.data

    def convertyaml2list(self, columnames):
        data = []
        assert isinstance(self.data, dict), NameError('data is not dict - probably not yaml?')
        valuecolumn = columnames[1:]
        for k, v in list(self.data.items()):
            row = [k] + [v[vget] for vget in valuecolumn]
            data.append(row)
        self.data = data
        self.columnames = columnames
        self.isyaml = False

        return self.data


def read_table(filename, sep='\t', tablename='', columnames=False, rownames=False, donumeric=False, dounicode=False):
    """
    table reader wrapper
    """

    table = Table(name=tablename)
    table.read(filename, sep=sep, columnames=columnames, rownames=rownames, donumeric=donumeric, dounicode=dounicode)
    return table


def write_table(data, filename, sep='\t', columnames=None):
    if not columnames:
        columnames = []

    table = Table()
    table.data = data
    table.columnames = columnames
    table.write(filename, sep=sep)
    return table


def read_panda(filename, sep='\t', tablename='', columnames=False, rownames=False, donumeric=False, dounicode=False):
    if not tablename:
        tablename = os.path.splitext(os.path.split(filename)[1])[0]
    pdtable = PDframe(name=tablename)
    pdtable.read(filename, sep=sep, columnames=columnames, rownames=rownames, donumeric=donumeric, dounicode=dounicode)
    return pdtable


def list2table(lis, colrow=None):
    tabobj = Table()
    if colrow:
        tabobj.colnames = lis[colrow]
        lis.remove(lis[colrow])
    tabobj.data = lis
    return tabobj


def table2list(tabobj, colrow=0):
    lis = [tabobj.colnames]
    lis += tabobj.data
    return lis


def table2dic(table, keycolumn, valuecolumn):
    
    if isinstance(valuecolumn,str):
        valuecolumn = [valuecolumn,]
    info = []
    for row in table.iterrows():
        key = row[keycolumn]
        value = dict([(val,row[val]) for val in valuecolumn if val in table.columnames])
        info.append((key,value))
    info = keylis2dic(info)
    return info




