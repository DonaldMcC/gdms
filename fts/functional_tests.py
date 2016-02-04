#!/usr/bin/env python
# this is now using the HTLMLTestrunner approach - however cant get that working to file other than by piping
# at the command line so approach for now is to get command line at main directory and run:
# python .\fts\functional_tests.py >testddmm.html  to get the file and then open in a browser
#
import unittest
import HTMLTestRunner
import sys, urllib2
sys.path.append('./fts/lib')
sys.path.append('../../gluon') # to use web2py modules

from selenium import webdriver
import subprocess
import sys
import os.path

#ROOT = 'http://localhost:8080/gdms'
#ROOT = 'http://localhost:8081/nds'
#ROOT = 'http://localhost:8081/gdms'
ROOT = 'http://www.netdecisionmaking.com/gdms'

NUMCYCLES = 6  # Reduce this for quicker runs
CACHETIME = 1  # This may revert to 120 seconds if caching in place on get question - but approach to get question needs reviewed
STARTSERVER = False

# may update these later but possibly just have 3 options for now
USERS={'USER1':'Testuser1','PASSWORD1':'user1',
        'USER2':'Testuser2','PASSWORD2':'user2','USER3':'Testuser3','PASSWORD3':'user3','USER4':'Testuser4','PASSWORD4':'user4',
       'USER5':'Testuser5','PASSWORD5':'user5','USER6':'Testuser6','PASSWORD6':'user6','USER7':'Testuser7','PASSWORD7':'user7',
       'USER8':'Testuser8','PASSWORD8':'user8','USER9':'Testuser9','PASSWORD9':'user9'}

listusers=['user2','user3','user4']
questref =  'functest questref'
votequest = 'tempvotetest'


class FunctionalTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        global STARTSERVER
        if STARTSERVER:
            self.web2py = start_web2py_server()
        #self.browser = webdriver.Firefox()
        self.browser = webdriver.Chrome('c:\python27\scripts\chromedriver.exe')
        self.browser.maximize_window()

        #self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)

    @classmethod    
    def tearDownClass(self):
        global STARTSERVER
        self.browser.close()
        if STARTSERVER:
            self.web2py.kill()

    def get_response_code(self, url):
        """Returns the response code of the given url

        url     the url to check for 
        return  the response code of the given url
        """

        handler = urllib2.urlopen(url, timeout = 5)
        return handler.getcode()


def start_web2py_server():
    #noreload ensures single process
    print os.path.curdir    
    return subprocess.Popen([
            'python', '../../web2py.py', 'runserver', '-a "passwd"', '-p 8001'
    ])

def run_functional_tests(pattern=None):
    print 'running tests'
    if pattern is None:
        tests = unittest.defaultTestLoader.discover('fts')
    else:
        pattern_with_globs = '*%s*' % (pattern,)
        tests = unittest.defaultTestLoader.discover('fts', pattern=pattern_with_globs)

    # neither of these actually write to file so just using >filename.html on the command line
    #runner = unittest.TextTestRunner()
    runner = HTMLTestRunner.HTMLTestRunner(verbosity=2)
    runner.run(tests)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        run_functional_tests()
    else:
        run_functional_tests(pattern=sys.argv[1])
 
