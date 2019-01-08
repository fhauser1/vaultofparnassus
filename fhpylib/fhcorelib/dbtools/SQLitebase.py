# -*- encoding: utf-8 -*-


"""
####################################################################

SQLitebase.py

%  Created by  Felix Hauser  on 2013-10-02.
%  Copyright (c) 2010-2013. All rights reserved.
%
%  This program is free software; you can redistribute it and/or modify
%  it under the terms of the GNU General Public License as published by
%  the Free Software Foundation; either version 2 of the License, or
%  (at your option) any later version.
%
%  This program is distributed in the hope that it will be useful,
%  but WITHOUT ANY WARRANTY; without even the implied warranty of
%  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
%  GNU General Public License for more details.
####################################################################
%  For Usage see & run testSqlexec() at the end of the program

common arguments used:
database : path for database (second db ca be attached)
test: True/False for printing SQL
stype: when set to 'rowquery' a Row object is returned

three main input types see test function at the bottom for usages

tabinfo -> list with tablename, column1,.........
filterinfo -> list with columname, filterarg,........
ignoreinfo-> list with columname, ignorearg,........

NOTE: supported are 
- raw sql queries (with format arguments and list arguments i.e WHERE col IN {0} )
- single table based drop, insert, create, select, where col in, where col (!)= 
- NOT AVAILABLE are any joins etc.
"""
import sqlite3
from fhgeneral.fhutils import Table, keylis2dic

RESERVED_WORDS = set([
    'all', 'analyse', 'analyze', 'and', 'any', 'array',
    'as', 'asc', 'asymmetric', 'authorization', 'between',
    'binary', 'both', 'case', 'cast', 'check', 'collate',
    'column', 'constraint', 'create', 'cross', 'current_date',
    'current_role', 'current_time', 'current_timestamp',
    'current_user', 'default', 'deferrable', 'desc',
    'distinct', 'do', 'else', 'end', 'except', 'false',
    'for', 'foreign', 'freeze', 'from', 'full', 'grant',
    'group', 'having', 'ilike', 'in', 'initially', 'inner',
    'intersect', 'into', 'is', 'isnull', 'join', 'leading',
    'left', 'like', 'limit', 'localtime', 'localtimestamp',
    'natural', 'new', 'not', 'notnull', 'null', 'off', 'offset',
    'old', 'on', 'only', 'or', 'order', 'outer', 'overlaps',
    'placing', 'primary', 'references', 'right', 'select',
    'session_user', 'set', 'similar', 'some', 'symmetric', 'table',
    'then', 'to', 'trailing', 'true', 'union', 'unique', 'user',
    'using', 'verbose', 'when', 'where'])

SQL_TEMPLATEDIC = {'drop': u'DROP TABLE {tablenamestr}',
                   'insert': u'INSERT INTO {tablenamestr}  {columnamestr} VALUES {valuestr}',
                   'create': u'CREATE TABLE {tablenamestr}  {columdefinition}',
                   'select': u'SELECT {qcolumnames} FROM {tablenamestr} ',
                   'dselect': u'SELECT DISTINCT {qcolumnames} FROM {tablenamestr}',
                   'exclude': u' {ignorecolumn} != {ignorearg}',
                   'excludein': u' {ignorecolumn} NOT IN {ignorearg}',
                   'filter': u' {filtercolumn} = {filterarg}',
                   'filterin': u' {filtercolumn} IN {filterarg}',
                   'update': u'INSERT OR REPLACE INTO {tablenamestr} values {valuestr}',
                   'unindex': u'CREATE UNIQUE INDEX IDX_{tablenamestr}_{indexcolumn} ON {tablenamestr} ({indexcolumn})',
                   'index': u'CREATE INDEX IDX_{tablenamestr}_{indexcolumn} ON {tablenamestr} ({indexcolumn})',
                   'foreignkey': u'FOREIGN KEY({tgtcolumn}) REFERENCES {tablenamestr}({refcolumn})',
                   'pragma': u"PRAGMA table_info({tablenamestr})"}


class DBTable(Table):
    """
    DBTable object containing data including commands as dict
    
    """

    def __init__(self, tablename, columnames, data, typeinfo=(), indexinfo=(), filterinfo=(), ignoreinfo=(),
                 place_arg=()):


        self.tablename = tablename
        self.columnames = columnames
        self.data = data
        self.typenames = ''
        # sql specific slots  #
        self.typeinfo = typeinfo
        self.indexinfo = indexinfo
        self.command = {}
        self.filterinfo = filterinfo  # list with columname and filter argument
        self.ignoreinfo = ignoreinfo  # list with columname and filter argument
        # combined or simple object for filling in placeholders of SQL
        self.place_arg = place_arg
        self.curInd = 0
        self.create_tmp = []

    def __validate_columnames(self):
        allcolumnames = self.columnames
        for ele in allcolumnames:
            assert ele not in RESERVED_WORDS, ''.join((str(ele), ' NOT allowed because reserved'))

    def __format_filterarg(self, filterinfo):
        """
        unify input for filter arguments
        all converted to dict columname:values
        
        """
        if isinstance(filterinfo, list) or isinstance(filterinfo, tuple):
            filtercolumn = [filterinfo[i] for i in range(0, len(filterinfo), 2)]
            filterarg = [filterinfo[i] for i in range(1, len(filterinfo), 2)]
            assert len(filtercolumn) == len(filterarg), 'ERROR IN FILTERARGUMENTS'
            filterhash = dict(zip(filtercolumn, filterarg))
        else:
            filterhash = filterinfo
        return filterhash

    def set_parameter(self):

        if isinstance(self.data, dict):
            self.data = self.data.items()
        if self.filterinfo:
            self.filterinfo = self.__format_filterarg(self.filterinfo)
        if self.ignoreinfo:
            self.ignoreinfo = self.__format_filterarg(self.ignoreinfo)
        self.__validate_columnames()

    def __str__(self):
        """for debuging printing all values"""
        s = ['\n\n\n###### TABLE PARAMETER #######\n', self.tablename, 'tablename\n',
             self.typeinfo, 'typeinfo\n', self.indexinfo, 'indexinfo\n', self.command, 'command\n',
             self.filterinfo, 'filterinfo\n', self.ignoreinfo, 'ignoreinfo\n',
             self.place_arg, 'place_arg\n', '\n\n\n###### END PARAMETER #######\n']
        s = '\t'.join([str(x) for x in s])
        strep = '\t'.join([str(x) for x in self.columnames]) + '\n'
        for row in self.data:
            strep += '\t'.join([str(x) for x in row]) + '\n'
        s = s + strep
        return s


class SQLiteTools(object):
    """Query assembly methods for SQLite database only
    
    Predefined SQLite queries and database loading methods 
        init parameters:
        @database : path to database
        @stype : optional parameter, if set to 'rowquery' query returns row object if set too relax ---> null allowed
        @ test : more verbose when 1 or 2
        @ querylimit : if above 50 query terms in list for filter or exclude a table is generated temporary
        relevant functions are: 
        - updatetable
        - tab2sql
        - sql2tab
        - sqlcolget
        
        """

    def __init__(self, database, stype='standard', test=0, querylimit=50):


        self.stype = stype
        self.test = test
        self.database = database
        self.database2 = None
        self.attachedname = None
        self.querylimit = querylimit

        self.nonempty = True
        if self.stype == 'relax':
            self.nonempty = False

    def dbconnect(self):
        """basic connect function"""

        if isinstance(self.database, tuple):
            self.database2 = self.database[1]
            self.attachedname = self.database[2]
            self.database = self.database[0]

        if self.stype == 'rowquery':
            con = sqlite3.connect(self.database)
            con.row_factory = sqlite3.Row
            cur = con.cursor()

        else:
            con = sqlite3.connect(self.database)
            cur = con.cursor()

        if self.database2:
            attachsql = ''.join(["ATTACH DATABASE \'", self.database2, "\' AS {attached} "]).format(
                attached=self.attachedname)
            cur.execute(attachsql)
            if self.test > 0:
                print 'attaching database: ' + attachsql
                print self.attachedname
                print self.database2

        if self.test >= 1:
            print '\nconnecting to database'
        return con, cur

    def current_tables(self):
        con, cur = self.dbconnect()
        cur.execute("""SELECT name from sqlite_master where type = \'table\' and name!=\'sqlite_sequence\'""")
        rescol = cur.fetchall()
        cur.close()
        con.close()
        tables = [ele[0] for ele in rescol]
        if self.test >= 1:
            print '\nconnection to database closed'
        return tables

    @staticmethod
    def valuestrgen(placeholder_arg):
        """assembly function for placeholders in sql"""
        if placeholder_arg and (isinstance(placeholder_arg, list) or isinstance(placeholder_arg, tuple)):
            valuestr = ['?' for _ele in placeholder_arg]
            valuestr = ''.join(['(', ','.join(valuestr), ')'])
        elif placeholder_arg and isinstance(placeholder_arg, dict):
            valuestr = ' (?,?) '
        else:
            valuestr = '?'
        return valuestr

    @staticmethod
    def colnamestrgen(columnames):
        """generation of columnames string for insert sql and others"""
        if columnames and (isinstance(columnames, tuple) or isinstance(columnames, list)):
            columnamestr = '(' + ','.join(columnames) + ')'
        else:
            columnamestr = '(' + columnames + ')'
        return columnamestr

    @staticmethod
    def reformrowquery(tabobj):
        tabobj.data = [[row[column] for column in tabobj.columnames] for row in tabobj.data]
        return tabobj


    def sql_insert(self, tabobj):
        """formating of INSERT statement """
        insert_query = SQL_TEMPLATEDIC['insert'].format(tablenamestr=tabobj.tablename,
                                                        columnamestr=self.colnamestrgen(tabobj.columnames),
                                                        valuestr=self.valuestrgen(tabobj.columnames))
        if self.test:
            print insert_query
        tabobj.command.update({'insert_query': insert_query})
        return insert_query

    def sql_update(self, tabobj):
        """formating of UPDATE statement and adding to command dict """
        update_query = SQL_TEMPLATEDIC['update'].format(tablenamestr=tabobj.tablename,
                                                        valuestr=self.valuestrgen(tabobj.columnames))
        tabobj.command.update({'update_query': update_query})
        return update_query

    @staticmethod
    def sql_drop(tabobj):
        """formating of DROP statement  and adding to command dict """
        drop_query = SQL_TEMPLATEDIC['drop'].format(tablenamestr=tabobj.tablename)
        tabobj.command.update({'drop_query': drop_query})
        return drop_query

    def sql_create(self, tabobj):
        """formating of CREATE statement and adding to command dict """
        if not tabobj.data:
            raise NameError('NO DATA IN TABLE ')
        if not tabobj.typeinfo or tabobj.typeinfo == 'auto' or len(tabobj.typeinfo) != len(tabobj.columnames):
            if self.test > 0:
                print '\nnno or auto or differing length of columnames and typeinfo'

            for row in tabobj:
                tmp = []
                for col in row:
                    if isinstance(col, int):
                        tmp.append('INTEGER')
                    elif isinstance(col, float):
                        tmp.append('FLOAT')
                    elif isinstance(col, str):
                        tmp.append('TEXT')
                    else:
                        tmp.append('TEXT')

                if tmp == tabobj.typenames:
                    break
                else:
                    tabobj.typenames = tmp
        else:
            tabobj.typenames = tabobj.typeinfo

        if self.nonempty:
            tabobj.typenames = [ele + ' NOT NULL' for ele in tabobj.typenames]

        typelis = zip(list(tabobj.columnames), list(tabobj.typenames))
        typelis = [(typelis[0][0], typelis[0][1] + ' PRIMARY KEY ASC NOT NULL ')] + typelis[1:]
        columdefinition = ''.join(['(', ','.join([' '.join(ele) for ele in typelis]) + ')'])
        create_query = SQL_TEMPLATEDIC['create'].format(tablenamestr=tabobj.tablename, columdefinition=columdefinition)

        return create_query

    @staticmethod
    def sql_select(tabobj, distinct):
        """formating of SELECT statement and adding to command dict """

        if distinct:
            qkey = 'dselect'
        else:
            qkey = 'select'
        select_query = SQL_TEMPLATEDIC[qkey].format(
            qcolumnames=','.join([tabobj.tablename + '.' + ele for ele in tabobj.columnames]),
            tablenamestr=tabobj.tablename)
        return select_query

    def sql_excludesel(self, tabobj):
        """formating of WHERE COLUMN  != ARG /NOT IN LIST statement and adding to command dict """
        excludesql = []
        place_arg = []
        for k, v in tabobj.ignoreinfo.items():
            if isinstance(v, tuple) or isinstance(v, list):
                if len(v) < self.querylimit:
                    excludesel_sql = SQL_TEMPLATEDIC['excludein'].format(ignorecolumn=k, ignorearg=self.valuestrgen(v))
                    place_arg += list(v)
                else:
                    selectquery = '(' + SQL_TEMPLATEDIC['select'].format(qcolumnames=k, tablenamestr=k + 'itmp') + ')'
                    excludesel_sql = SQL_TEMPLATEDIC['excludein'].format(ignorecolumn=k, ignorearg=selectquery)
                    tabobj.create_tmp.append((k, v, 'itmp'))

            else:
                excludesel_sql = SQL_TEMPLATEDIC['exclude'].format(ignorecolumn=k, ignorearg=self.valuestrgen(v))
                place_arg += [v, ]

            excludesql.append(excludesel_sql)

        if len(excludesql) > 1:
            excludesel_sql = ' '.join(['WHERE', ' AND '.join(excludesql)])
        else:
            excludesel_sql = ' WHERE ' + excludesql[0]
        return excludesel_sql, place_arg

    def sql_filtersel(self, tabobj):
        """formating of WHERE COLUMN  = ARG / IN LIST statement and adding to command dict """
        filtersql = []
        place_arg = []
        for k, v in tabobj.filterinfo.items():
            if isinstance(v, tuple) or isinstance(v, list):
                if len(v) < self.querylimit:
                    filter_sql = SQL_TEMPLATEDIC['filterin'].format(filtercolumn=k, filterarg=self.valuestrgen(v))
                    place_arg += list(v)
                else:
                    selectquery = '(' + SQL_TEMPLATEDIC['select'].format(qcolumnames=k, tablenamestr=k + 'ftmp') + ')'
                    filter_sql = SQL_TEMPLATEDIC['filterin'].format(filtercolumn=k, filterarg=selectquery)
                    tabobj.create_tmp.append((k, v, 'ftmp'))

            else:
                filter_sql = SQL_TEMPLATEDIC['filter'].format(filtercolumn=k, filterarg=self.valuestrgen(v))
                place_arg += [v, ]

            filtersql.append(filter_sql)

        if len(filtersql) > 1:
            filter_sql = ' '.join([' WHERE ', ' AND '.join(filtersql)])
        else:
            filter_sql = ' WHERE ' + filtersql[0]

        return filter_sql, place_arg

    @staticmethod
    def sql_index(tabobj):
        """formating of INDEX statement """
        index_query = []
        for indexcolumn in tabobj.indexinfo:
            index_query.append(SQL_TEMPLATEDIC['index'].format(tablenamestr=tabobj.tablename, indexcolumn=indexcolumn))
        return index_query

    def select_sql(self, tabobj, distinct):
        """assembling SQL from different pieces"""
        if self.test > 1:
            print tabobj

        select_cmd = [self.sql_select(tabobj, distinct)]
        place_arg = []
        if tabobj.place_arg:
            if isinstance(tabobj.place_arg, tuple) or isinstance(tabobj.place_arg, list):
                place_arg += list(tabobj.place_arg)
            else:
                place_arg += [tabobj.place_arg, ]

        if tabobj.ignoreinfo:
            excludesel_sql, tplace_arg = self.sql_excludesel(tabobj)
            place_arg += tplace_arg

            if ('WHERE') not in select_cmd:
                select_cmd.append(('WHERE'))
            else:
                select_cmd.append(('AND'))
            select_cmd.append(excludesel_sql.split('WHERE')[1])
            
        if tabobj.filterinfo:
            filter_sql, tplace_arg = self.sql_filtersel(tabobj)
            place_arg += tplace_arg
            if ('WHERE') not in select_cmd:
                select_cmd.append(('WHERE'))
            else:
                select_cmd.append(('AND'))

            select_cmd.append(filter_sql.split('WHERE')[1])

            if self.test >= 1:
                print '\n No ignore tuple provided , Filter tuple provided'
                print tabobj.place_arg

        select_cmd = ' '.join([ele for ele in select_cmd])
        tabobj.command.update({'select_query': select_cmd})
        tabobj.place_arg = place_arg
        if self.test > 1:
            print '\n\n\n AFTER LOADING QUERY '
            print tabobj

        return tabobj

    def sqlexecute(self, commandlist, tablename):
        """
        CORE SQL EXECUTE function

        """

        con, cur = self.dbconnect()
        data = []
        columnames = []
        typeinfo = []
        for cmd, placeholder, action in commandlist:
            if action == 'query':
                if placeholder:
                    cur.execute(cmd, placeholder)
                else:
                    cur.execute(cmd)
                data += cur.fetchall()
            if action == 'commit':
                cur.execute(cmd)
                con.commit()
            if action == 'insert':
                con.executemany(cmd, placeholder)
                con.commit()

        if tablename:
            cur.execute(SQL_TEMPLATEDIC['pragma'].format(tablenamestr=tablename))
            metadata2 = cur.fetchall()
            typeinfo = [item[2] for item in metadata2]
            columnames = [item[1] for item in metadata2]

        cur.close()
        con.close()

        return data, columnames, typeinfo

    def querysqlwrapper(self, tabobj, metadata=False):
        """
        assembly commands for execution

         """
        if self.test >= 1:
            print tabobj.command['select_query'], tabobj.place_arg
        if self.test > 1:
            print tabobj
        commandlist = []
        if tabobj.create_tmp:
            for k, v, ty in tabobj.create_tmp:
                tmptab = DBTable(tablename=k + ty, columnames=(k,), data=[(ele,) for ele in v])
                self.tablegenerate(tmptab)

        commandlist.append((tabobj.command['select_query'], tabobj.place_arg, 'query'))

        if tabobj.create_tmp:
            for k, v, ty in tabobj.create_tmp:
                tmptab = DBTable(tablename=k + ty, columnames=[k, ], data=[(ele,) for ele in v])
                commandlist.append((self.sql_drop(tmptab), None, 'commit'))

        if metadata:
            getmetadata = tabobj.tablename
        else:
            getmetadata = False
        data, columnames, typeinfo = self.sqlexecute(commandlist, getmetadata)
        tabobj.data = data

        if metadata:
            tabobj.columnames = [unicode(ele) for ele in tabobj.columnames]
            if tabobj.columnames == [u'*', ]:
                tabobj.columnames = columnames
                tabobj.typeinfo = typeinfo
            elif tabobj.columnames == [unicode(ele) for ele in columnames]:
                tabobj.typeinfo = typeinfo

            elif not tabobj.columnames:
                tabobj.columnames = columnames
                tabobj.typeinfo = typeinfo

            else:
                # enforce order from columnames in tableobj if necessary 
                tabobj.data = [[row[column] for column in tabobj.columnames] for row in tabobj.iterrows()]

        if self.test >= 1:
            print '\nconnection to database closed'

        return tabobj


    def tablegenerate(self, tabobj):
        """seq of sqls to generate table """

        if self.test >= 1:
            print self.sql_create(tabobj)
            print self.sql_insert(tabobj), tabobj.data

        self.stype = 'create'
        commandlist = []
        if tabobj.tablename in self.current_tables():
            print '\nremoving old ' + tabobj.tablename
            commandlist.append((self.sql_drop(tabobj), None, 'commit'))
        else:
            print '\nnothing to remove'

        commandlist.append((self.sql_create(tabobj), None, 'commit'))

        if isinstance(tabobj.data, sqlite3.Row):
            tabobj.data = self.reformrowquery(tabobj)

        # handle cases where table only has one column
        # if len(tabobj.columnames) == 1 :
        # tabobj.data = [(ele,) for ele in tabobj.data]

        commandlist.append((self.sql_insert(tabobj), tabobj.data, 'insert'))

        if tabobj.indexinfo:
            index_query = self.sql_index(tabobj)
            for idx in index_query:
                commandlist.append((idx, None, 'commit'))


        # execute of all commands
        self.sqlexecute(commandlist, tablename=False)

        if self.test >= 1:
            print '\n table ' + tabobj.tablename + ' generated'
        if self.test >= 1:
            print '\nconnection to database closed'

    # ############################################################################
    # functions to use 


    def executesql(self, query=None, format_arg=None, placeholder=None):
        """
        -query:  string with SQL , optional with {} format labels
        -format_arg: list or tuple with strings for formating the SQL
        - placeholder : list which is used for setting values in ?
        - returns DBTable object with data in DBTable.data and columnames in DBTable.columnames
        """
        if not placeholder: placeholder = []
        if not format_arg: format_arg = []
        newtable = DBTable(tablename='sql', columnames=[], data=[])
        newtable.set_parameter()
        if format_arg:
            query = query.format(*format_arg)

        newtable.command = {'select_query': query}
        if placeholder:
            newtable.place_arg = placeholder
        commandlist = [(query, placeholder, 'query')]
        data, _columnames, _typeinfo = self.sqlexecute(commandlist, tablename=False)
        newtable.data = data
        if self.stype == 'rowquery' and newtable.data:
            newtable.columnames = newtable.data[0].keys()
        return newtable


    def tab2sql(self, tabinfo=None, data=None, typeinfo=None, indexinfo=None, place_arg=None):
        """
        loading list of tuples i.e table or dict  into sql table
        tabinfo: tuple with table name and following column names
        typeinfo(optional): list with datatypes of columns
        indexinfo (optional):list with columnames for indexing
        data: list of tuples for each row or dic
        NOTE:
        -no update of the table but first drop table with the given name
        - index is primitive i.e. INDEX .....
        """
        if not place_arg: place_arg = []
        if not indexinfo: indexinfo = []
        if not typeinfo: typeinfo = []
        if not data: data = []
        if not tabinfo: tabinfo = []

        if isinstance(tabinfo, Table):
            newtable = DBTable(tablename=tabinfo.name, columnames=tabinfo.columnames, data=tabinfo.data,
                               typeinfo=typeinfo, indexinfo=indexinfo, place_arg=place_arg)
        else:
            newtable = DBTable(tablename=tabinfo[0], columnames=tabinfo[1:], data=data, typeinfo=typeinfo,
                               indexinfo=indexinfo, place_arg=place_arg)
        newtable.set_parameter()

        self.tablegenerate(newtable)


    def sql2tab(self, tabinfo=None, data=None, filterinfo=None, ignoreinfo=None, place_arg=None, distinct=False):
        """ return function of tab2sql (see above)
         for getting table information back including typeinfo
        mainly for moving between databases"""

        if not place_arg: place_arg = []
        if not ignoreinfo: ignoreinfo = []
        if not filterinfo: filterinfo = []
        if not data: data = []
        if not tabinfo: tabinfo = []

        newtable = DBTable(tablename=tabinfo[0], columnames=tabinfo[1:], data=data, filterinfo=filterinfo,
                           ignoreinfo=ignoreinfo, place_arg=[])
        newtable.set_parameter()

        newtable = self.select_sql(newtable, distinct)
        newtable = self.querysqlwrapper(newtable, metadata=True)

        if self.test >= 1:
            print '\nconnection closed'
            print newtable.command
        return newtable


    def sqltab2dic(self, tabinfo, filterinfo=None, ignoreinfo=None, distinct=True):
        """

        retrieving python dictionary from table
        tabinfo: tuple with table name and following column names (key,value; only two allowed)
        ignore,ignorecolumn: optional parameter - if set SQL: ...WHERE ignorecolumn != 'ignore'
        distinct: if true : SQL: SELECT DISTINCT ...
        dic: dictionary

        """
        if not ignoreinfo: ignoreinfo = []
        if not filterinfo: filterinfo = []
        newtable = self.sql2tab(tabinfo, filterinfo=filterinfo, ignoreinfo=ignoreinfo, distinct=distinct)
        tulis = newtable.data
        dic = keylis2dic(tulis)
        if len(tulis) != len(dic):
            print '\nsqltab2dic: duplicates eliminated uncontrolled in {0} in database {1}'.format(newtable.tablename,
                                                                                                   self.database)
            val = [item[0] for item in tulis]
            valset = set(val)
            infos = [(item, val.count(item)) for item in valset if val.count(item) > 1]
            print infos[0]

        return dic

    def sqlcolget(self, tabinfo, data=None, filterinfo=None, ignoreinfo=None, distinct=False):
        """fetching entire columns"""
        if not filterinfo: filterinfo = []
        if not data: data = []
        if not ignoreinfo: ignoreinfo = []

        newtable = DBTable(tablename=tabinfo[0], columnames=tabinfo[1:], data=data, filterinfo=filterinfo,
                           ignoreinfo=ignoreinfo)
        newtable.set_parameter()

        newtable = self.sql2tab(tabinfo, filterinfo=filterinfo, ignoreinfo=ignoreinfo, distinct=distinct)
        if self.test >= 1:
            print '\nconnection closed'
            print newtable.command
        rescol = [ele[0] for ele in newtable]
        return rescol

    def updatevalues(self, tabinfo, data):
        newtable = DBTable(tablename=tabinfo[0], columnames=tabinfo[1:], data=data)
        newtable.set_parameter()
        update_sql = self.sql_update(newtable)
        commandlist = [(update_sql, newtable.data, 'insert')]
        if self.test:
            print update_sql
        newtable = self.sqlexecute(commandlist, newtable.tablename)
        if self.test >= 1:
            print '\nconnection closed'
            print '\nupdate done '

    def insertvalues(self, tabinfo, data):
        newtable = DBTable(tablename=tabinfo[0], columnames=tabinfo[1:], data=data)
        newtable.set_parameter()
        sql_insert = self.sql_insert(newtable)
        commandlist = [(sql_insert, newtable.data, 'insert')]
        if self.test:
            print sql_insert
        newtable = self.sqlexecute(commandlist, newtable.tablename)


    def get_table_list(self):
        """Returns a list of table names in the current database."""
        tablelist = self.sqlcolget(tabinfo=['sqlite_master', 'name'], filterinfo=['type', 'table'],
                                   ignoreinfo=['name', 'sqlite_sequence'])
        return tablelist

        
        

