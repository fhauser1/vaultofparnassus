from dbtools.SQLitebase import SQLiteTools
import unittest
import sys

class TestUtils(unittest.TestCase):
    """
    Unitests for SQLite class

    """
    def setUp(self):
            self.seq = range(10)

    def testSqlexec(self):
        """

        Simple function to run examples 
        for using the SQLite wrappers
        the SQLite database is created if not existing in current working directory

        """
        # Prepare the connection to the database
        s = SQLiteTools(database='testdb.sqlite', stype='rowquery', test=0)
        s.querylimit = -1
        
        # Generate the 'newtab' table in the database
        # and fill it with the data
        s.tab2sql(tabinfo=('newtab', 'nam', 'yes'), data=[(1, 2), (2, 3), (4, 5), (5, 6), (6, 7), (7, 8)],
                  typeinfo=['INTEGER', 'TEXT'])
        # Query the table i.e. here get the entire table
        q = s.sql2tab(['newtab', 'nam', 'yes'])
        self.assertEqual(q.data, [(1, u'2'), (2, u'3'), (4, u'5'), (5, u'6'), (6, u'7'), (7, u'8')])
        self.assertEqual(q.typeinfo , [u'INTEGER', u'TEXT'])

        # write the table to a file
        q.write('testfile.txt')

        # perform a series of 'SELECT' queries
        # with filterinfo (~ 'WHERE) and ignoreinfo (~ WHERE NOT IN)
        # the examples use different syntax that all should work
        q = s.sql2tab(**{'tabinfo': ('newtab', 'nam', 'yes'), 'filterinfo': ['nam', ('1','2','3','4')], # ['nam', (1, 2, 3, 4)]
                         'ignoreinfo': ['yes', '5']})
        q = s.sql2tab(**{'tabinfo': ('newtab', 'nam', 'yes'), 'filterinfo': ['nam', ('1', '2')]})  #
        self.assertEqual(q.data, [(1, u'2'), (2, u'3')])
        self.assertEqual(q.typeinfo , [u'INTEGER', u'TEXT'])

        q = s.sql2tab(**{'tabinfo': ('newtab', 'nam', 'yes'), 'filterinfo': ['nam', ('1', '7'), 'yes', '8']})

        self.assertEqual( q.data , [(7, u'8')])
        self.assertEqual( q.typeinfo , [u'INTEGER', u'TEXT'])

        #
        q = s.sql2tab(tabinfo=('newtab', 'nam', 'yes'), filterinfo=['nam', '11'])

        self.assertEqual( q.data , [])
        self.assertEqual( q.typeinfo , [u'INTEGER', u'TEXT'])

        q = s.sql2tab(tabinfo=('newtab', '*'))
        self.assertEqual( q.data , [(1, u'2'), (2, u'3'), (4, u'5'), (5, u'6'), (6, u'7'), (7, u'8')])
        self.assertEqual( q.typeinfo , [u'INTEGER', u'TEXT'])

        q = s.sql2tab(**{'tabinfo': ('newtab', 'nam', 'yes'), 'ignoreinfo': ['nam', ('1', '2')]})
        self.assertEqual( q.data , [(4, u'5'), (5, u'6'), (6, u'7'), (7, u'8')])
        self.assertEqual( q.typeinfo , [u'INTEGER', u'TEXT'])

        q = s.sql2tab(**{'tabinfo': ('newtab', 'nam', 'yes'), 'filterinfo': ['nam', ('1', '2', '3', '4', '5')],
                         'ignoreinfo': ['nam', ('1', '2')]})
        self.assertEqual( q.data , [(4, u'5'), (5, u'6')])
        self.assertEqual( q.typeinfo , [u'INTEGER', u'TEXT'])

        q = s.sql2tab(**{'tabinfo': ('newtab', 'nam', 'yes'), 'filterinfo': ['nam', '1']})
        self.assertEqual( q.data , [(1, u'2')])
        self.assertEqual( q.typeinfo , [u'INTEGER', u'TEXT'])

        q = s.sql2tab(**{'tabinfo': ('newtab', 'nam', 'yes'), 'ignoreinfo': ['nam', '1']})
        self.assertEqual( q.data , [(2, u'3'), (4, u'5'), (5, u'6'), (6, u'7'), (7, u'8')])
        self.assertEqual( q.typeinfo , [u'INTEGER', u'TEXT'])

        q = s.sql2tab(
            **{'tabinfo': ('newtab', 'nam', 'yes'), 'filterinfo': ['nam', '1'], 'ignoreinfo': ['yes', ('5', '3')]})
        self.assertEqual( q.data , [(1, u'2')])
        self.assertEqual( q.typeinfo , [u'INTEGER', u'TEXT'])

        q = s.sql2tab(**{'tabinfo': ('newtab', 'nam', 'yes'), 'filterinfo': ['nam', ('1', '2', '3', '4')],
                         'ignoreinfo': ['yes', '5']})
        self.assertEqual( q.data , [(1, u'2'), (2, u'3')])
        self.assertEqual( q.typeinfo , [u'INTEGER', u'TEXT'])
        
        # Generate the second table
        s.tab2sql(['newdiv', 'keyi', 'vali'], dict([(1, 2), (2, 3), (4, 5), (5, 6)]), ['INTEGER', 'TEXT'])
        a = s.sqltab2dic(['newdiv', 'vali', 'keyi'])
        self.assertEqual( a , {u'3': [2], u'2': [1], u'5': [4], u'6': [5]})

        q = s.executesql(query='SELECT * FROM newtab where nam = ?', placeholder=('1',))
        self.assertEqual( q.data , [(1, u'2')])

        tl = s.get_table_list()
        self.assertEqual( tl , [u'newtab', u'newdiv'])

        s = SQLiteTools(database='testdb.sqlite', stype='standard', test=0)
        a = s.sql2tab(['newtab', 'nam', 'yes'])
        self.assertEqual( [(1, u'2'), (2, u'3'), (4, u'5'), (5, u'6'), (6, u'7'), (7, u'8')] , a.data)
        
        # update example
        s.updatevalues(tabinfo=['newtab', 'nam', 'yes'], data=[(8, 9), (98, 11)])
        a = s.sql2tab(['newtab', 'nam', 'yes'])
        self.assertEqual( [(1, u'2'), (2, u'3'), (4, u'5'), (5, u'6'), (6, u'7'), (7, u'8'), (8, u'9'), (98, u'11')] , a.data)

        # insert example
        s.insertvalues(tabinfo=['newtab', 'nam', 'yes'], data=[(800, 9), (900, 11)])
        a = s.sql2tab(['newtab', 'nam', 'yes'])
        self.assertEqual( [(1, u'2'), (2, u'3'), (4, u'5'), (5, u'6'), (6, u'7'), (7, u'8'), (8, u'9'), (98, u'11'), (800, u'9'),
                (900, u'11')] , a.data)
        print 'ALL TESTS PASSED'

if __name__ == '__main__':
    unittest.main()