from __future__ import print_function
from builtins import range
from dbtools.SQLitebase import SQLiteTools
import unittest
import sys

class TestUtils(unittest.TestCase):
    """
    Unitests for SQLite class

    """
    def setUp(self):
            self.seq = list(range(10))

    def testSqlexec(self):
        """function to test above class
         database is created if not existing in current work dir"""
        s = SQLiteTools(database='testdb.sqlite', stype='rowquery', test=0)
        s.querylimit = -1
        s.tab2sql(tabinfo=('newtab', 'nam', 'yes'), data=[(1, 2), (2, 3), (4, 5), (5, 6), (6, 7), (7, 8)],
                  typeinfo=['INTEGER', 'TEXT'])
        q = s.sql2tab(['newtab', 'nam', 'yes'])
        self.assertEqual(q.data, [(1, u'2'), (2, u'3'), (4, u'5'), (5, u'6'), (6, u'7'), (7, u'8')])
        self.assertEqual(q.typeinfo , [u'INTEGER', u'TEXT'])
        q.write('testfile.txt')

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

        s.updatevalues(tabinfo=['newtab', 'nam', 'yes'], data=[(8, 9), (98, 11)])
        a = s.sql2tab(['newtab', 'nam', 'yes'])
        self.assertEqual( [(1, u'2'), (2, u'3'), (4, u'5'), (5, u'6'), (6, u'7'), (7, u'8'), (8, u'9'), (98, u'11')] , a.data)

        s.insertvalues(tabinfo=['newtab', 'nam', 'yes'], data=[(800, 9), (900, 11)])
        a = s.sql2tab(['newtab', 'nam', 'yes'])
        self.assertEqual( [(1, u'2'), (2, u'3'), (4, u'5'), (5, u'6'), (6, u'7'), (7, u'8'), (8, u'9'), (98, u'11'), (800, u'9'),
                (900, u'11')] , a.data)
        print('ALL TESTS PASSED')

if __name__ == '__main__':
    unittest.main()