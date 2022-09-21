"""
Alchemy.py

Created by dummy on 2011-07-25.
Copyright (c) 2011 All rights reserved.
"""
### built in  modules ###
import sys
import os

### external modules
import sqlalchemy
from sqlalchemy import Column, Integer, String,Float, MetaData, ForeignKey,Sequence, select
from sqlalchemy.sql import and_, or_, not_
from fhgeneral import fhutils
import pandas

### fh modules ###

### local modules ###

### global settings ####


class MerlinTools(object):
    """Query assembly methods for Database type based on SQLAlchemy
    
        init parameters:
        database : path to database
        relevant functions are: 
        - updatetable
        - tab2sql
        - sql2tab
        - sqlcolget
        -sqltab2dic
        
        """ 
    def __init__(self,database, stype = 'standard' ,drivername = 'sqlite',username=None, password=None, host=None, port=None,test = False ):
        self.stype = stype
        self.test = test
        self.database = database
        self.drivername = drivername
        self.username=username
        self.password=password
        self.host=host
        self.port=port

        if not database:
            self.database = 'sqlite:///:memory:'
        else:
            self.database = sqlalchemy.engine.url.URL(drivername=self.drivername, username=self.username, password=self.password, host=self.host, port=self.port, database=self.database, query=None)
        self.nonempty = True
        if self.stype =='relax':
            self.nonempty= False

        self.type2alchemy={'INTEGER':Integer,'TEXT':String,'FLOAT':Float}
        
    def dbconnect(self):
        engine = sqlalchemy.create_engine(self.database, echo=self.test)
        
        metadata = sqlalchemy.MetaData()
        return engine,metadata
    
    def generate_paramdic(self,data,tabinfo):
        paramlis = []
        if isinstance(data,dict):
            data=data.items()
        for tup in data:
            new=dict(zip(tabinfo[1:],tup))
            paramlis.append(new)
        return paramlis
    
    
    def parseinput(self,tabinfo= None, data = None, typeinfo = None, indexinfo = None):
        if isinstance(tabinfo,list) or isinstance(tabinfo,tuple):
            tablename = tabinfo[0]
            columnames = tabinfo[1:]
            tabledata =fhutils.PDframe(tablename)
            tabledata.data = fhutils.PDframe(tablename).data(data, columns=columnames, index=indexinfo)
        elif isinstance(tabinfo,fhutils.Table):
            tabledata = fhutils.PDframe(tabinfo.name)
            tabledata.data = fhutils.PDframe(tabinfo.name).data(tabinfo.data, columns=columnames,index=indexinfo)
        elif isinstance(tabinfo,fhutils.PDframe):
            tabledata = tabinfo
        else:
            tabledata = tabinfo
        return tabledata
            
            
        
        

    def tab2sql (self ,tabinfo= None, data = None, typeinfo = None, indexinfo = None):
        """
        loading list of tuples i.e table or dict  into sql table
        tabinfo: tuple with table name and following column names
        typeinfo(optional): list with datatypes of columns
        indexinfo (optional):list with columnames for indexing
        datas: list of tuples for each row or dic
        NOTE:
        -no update of the table but first drop table with the given name
        """
        
        engine,metadata=self.dbconnect() 
        tabledata = self.parseinput(tabinfo, data, typeinfo, indexinfo)
        try:
            tab = sqlalchemy.Table(tabledata.name, metadata, autoload_with=engine)
            tab.drop(bind=engine,checkfirst = True)
        except:
            print 'no table removed'
        
        tabledata.data.to_sql(tabledata.name,engine)
        


    def updatetable(self,tabinfo = None , data = None, filterinfo = None, ignoreinfo = None, distinct = False):
        engine = sqlalchemy.create_engine(self.database, echo=self.test)
        engine,metadata=self.dbconnect()
        t=sqlalchemy.Table(tabinfo[0], metadata, autoload=True, autoload_with=engine)
        ins = t.insert()
        paramlis = self.generate_paramdic(data,tabinfo)
        engine.execute(ins,paramlis)
    
    
    
        
    def sql2tab(self,tabinfo = None , data = None, filterinfo = None, ignoreinfo = None, distinct = False):
        """ return function of tab2sql (see above)
         for getting table information back including typeinfo
        mainly for moving between databases"""
        
        # engine = sqlalchemy.create_engine(self.database, echo=self.test)
        engine,metadata=self.dbconnect()
        t=sqlalchemy.Table(tabinfo[0], metadata, autoload=True, autoload_with=engine)
        columnlist=[]
        for i in range(1,len(tabinfo)):
            columnlist.append(t.c[tabinfo[i]])
        query = select(columnlist,distinct=distinct)
        
        if filterinfo:
            query=query.where(t.c[tabinfo[1]].in_(filterinfo[1]))
        if ignoreinfo:
            query=query.where(not_(t.c[tabinfo[1]].in_(ignoreinfo[1])))
            
        result = engine.execute(query)
        return result
        
    def sqltab2dic(self, tabinfo ,filterinfo = None, ignoreinfo = None, distinct = True ):
        """
        retrieving python dictionary from table
        tabinfo: tuple with table name and following column names (key,value; only two allowed)
        ignore,ignorecolumn: optional parameter - if set SQL: ...WHERE ignorecolumn != 'ignore'
        distinct: if true : SQL: SELECT DISTINCT ...
        dic: dictionary
        """
        newtable=self.sql2tab(tabinfo, filterinfo = filterinfo, ignoreinfo = ignoreinfo, distinct = distinct)
        tulis = [row for row in newtable]
        dic=dict(tulis)
        if len(tulis)!=len(dic):
            print 'sqltab2dic: duplicates eliminated uncontrolled in {0} in database {1}'.format(newtable.tablename,self.database)
            val = [item[0] for item in tulis]
            valset = set(val)
            infos = [(item, val.count(item)) for item in valset if val.count(item)>1]
            print infos

        return dic  
    
    
    def sqlcolget(self,tabinfo ,data = None, filterinfo = None, ignoreinfo = None, distinct = False):
        """fetching entire columns"""

        newtable=self.sql2tab(tabinfo, filterinfo = filterinfo, ignoreinfo = ignoreinfo, distinct = distinct)
        tulis = [row[0] for row in newtable]

        return tulis
    
    
    def executesql(self, query=None):
        """
        -query:  string with SQL , optional with {} format labels
        -format_arg: list or tuple with strings for formating the SQL
        - placeholder : list which is used for setting values in ?
        - returns DBTable object with data in DBTable.data and columnames in DBTable.columnames
        """
        engine,metadata=self.dbconnect()
        pdtable = fhutils.PDframe()
        pdtable.data = pandas.read_sql_query(query, engine)
        return pdtable
        
