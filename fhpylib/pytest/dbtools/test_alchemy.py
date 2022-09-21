from dbtools.Alchemy import MerlinTools
from fhgeneral.fhutils import read_panda


def testSqlexec():
    """function to test above class
     database is created if not existing in current work dir"""
    s=MerlinTools(database ='testalchemydb.sqlite',stype = 'standard',test =True)
    tabp = read_panda('testfiles/tab1.txt',columnames = True,rownames=True)
        
    s.tab2sql(tabp)
    
    q=s.sql2tab(**{'tabinfo':('tab1','e','r'),'filterinfo':['t',('1','2')]})
    for row in q:
        print '2',row
    
    
    s.tab2sql(tabinfo=('newtab','nam','yes'),data=[(1,2),(2,3),(4,5),(5,6),(6,7),(7,8)],typeinfo=['INTEGER','TEXT'])
    q = s.sql2tab(['newtab','nam'])
    for row in q:
        print '1 sql2tab',row
    
    print s.executesql('SELECT * FROM newtab')
    
    
    q=s.sql2tab(**{'tabinfo':('newtab','nam','yes'),'filterinfo':['nam',('1','2')]})
    for row in q:
        print '2 sql2tab',row
    q=s.sql2tab(**{'tabinfo':('newtab','nam','yes'),'ignoreinfo':['nam',('1','2')]})
    for row in q:
        print '3 sql2tab',row
    q=s.sql2tab(**{'tabinfo':('newtab','nam','yes'),'filterinfo':['nam',('1','2','3','4','5')],'ignoreinfo':['nam',('1','2')]})
    for row in q:
        print '4 sql2tab',row
        
    q=s.sql2tab(**{'tabinfo':('newtab','nam','yes'),'filterinfo':['nam','1']})
    for row in q:
        print '5 sql2tab',row
    q=s.sql2tab(**{'tabinfo':('newtab','nam','yes'),'ignoreinfo':['nam','1']})
    for row in q:
        print '6sql2tab',row
    q=s.sql2tab(**{'tabinfo':('newtab','nam','yes'),'filterinfo':['nam','1'],'ignoreinfo':['yes',('5','3')]})
    for row in q:
        print '7 sql2tab',row
    q=s.sql2tab(**{'tabinfo':('newtab','nam','yes'),'filterinfo':['nam',('1','2','3','4')],'ignoreinfo':['yes','5']})
    for row in q:
        print '8 sql2tab',row
    s.tab2sql(['newdiv','keyi','vali'],dict([(1,88),(2,3),(4,5)]),['INTEGER','TEXT'])
    q=s.sqltab2dic(['newdiv','keyi','vali'])
    print '9 sqltab2dic',q
    print '10 sqlcolget',s.sqlcolget(['newdiv','vali'])
    s.updatetable(tabinfo = ['newdiv','keyi','vali'],data=[(28,99),(10,11),(15,11)])
            
    
if __name__ == '__main__':
    testSqlexec()
