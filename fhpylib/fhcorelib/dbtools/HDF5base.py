import os
import tables

class HdfTools(object):
 
    
    
    def __init__(self,database ):
        self.database = database
        
    def dbconnect(self):
        """basic connect function"""
        if os.path.isfile(self.database):
            self.h5file = tables.openFile(self.database,'r+')
            
        else:
            self.h5file = tables.openFile(self.database, 'w')
        return self.h5file
    
    def dbclose(self):
        """basic disconnect function"""
        self.h5file.flush()
        self.h5file.close()    
    
    
    def tablegen(self,datafile,tabinfo,typeinfo,strsize=16):
        typedic={'INTEGER':tables.IntCol(),
        'FLOAT':tables.Float32Col(),
        'TEXT':tables.StringCol(strsize)}
        columnames=tabinfo[1:]
        table_name=tabinfo[0]
        tmp = zip(columnames,typeinfo)
        description_name=[]
        for cn,ti in tmp:
            nti=typedic.get(ti,tables.StringCol(strsize))
            description_name.append((cn,nti))
        description_name=dict(description_name)
        
        self.dbconnect()
        if table_name in self.h5file.root:
            h5file.removeNode('/', table_name)
            
        table = self.h5file.createTable('/', tabinfo[0], description_name)
        pointer = table.row
        infi=open(datafile,'rU')
        for line in infi:
            col=line.split()
            for i in range(1,len(tabinfo)):
                val=col[i-1]
                if typeinfo[i-1] =='INTEGER':
                    val=int(val)
                elif typeinfo[i-1] =='FLOAT':
                    val=float(val)
                elif typeinfo[i-1] =='TEXT':
                    val=str(val)
                else:
                    val=str(val)
                
                pointer[tabinfo[i]]=val
            pointer.append()
        table.flush()
        self.dbclose()
        
        
    def filterparse(self, tabinfo, filterinfo=None, excludeinfo=None):
        if not excludeinfo:
            excludeinfo = []
        if not filterinfo:
            filterinfo = []

        condfilter=[]
        if filterinfo:
            filterinfo=[(filterinfo[i],filterinfo[i+1]) for i in range(0,len(filterinfo),2)]
            for col,tu in filterinfo:
                if isinstance(tu,tuple):
                    filterinfo='|'.join(['('+str(col)+'=='+str(tu[i])+')' for i in range(0,len(tu))])
                else:
                    filterinfo='('+str(col)+'=='+str(tu)+')'
                condfilter.append(filterinfo)
            
        if excludeinfo:
            excludeinfo=[(excludeinfo[i],excludeinfo[i+1]) for i in range(0,len(excludeinfo),2)]
            for col,tu in excludeinfo:
                if isinstance(tu,tuple):
                    excludestr='|'.join(['('+str(col)+'!='+str(tu[i])+')' for i in range(0,len(tu))])
                else:
                    excludestr='('+str(col)+'!='+str(tu)+')'
                condfilter.append(excludestr)  
        condfilter='&'.join(condfilter)      
        columnames=tabinfo[1:]
        table_name=tabinfo[0]
            
            
        active_h5file=self.dbconnect()
        table=active_h5file.getNode('/',table_name)
        if not filterinfo and not excludeinfo:
            for row in table:
                data=[row[key] for key in columnames]
                yield data
        else:            
            for row in table.where(condfilter):
                data=[row[key] for key in columnames]
                yield data
        
    def executehd5f(self,tabinfo,filterstr):
        columnames=tabinfo[1:]
        table_name=tabinfo[0]
            
            
        active_h5file=self.dbconnect()
        table=active_h5file.getNode('/',table_name)
        
        for row in table.where(filterstr):
            data=[row[key] for key in columnames]
            yield data

 

