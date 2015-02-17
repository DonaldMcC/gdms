# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first

from functional_tests import FunctionalTest, ROOT, USERS
import time

class AnswerQuestion (FunctionalTest):

    def setUp(self):       
        self.url = ROOT + '/default/user/login'        
        get_browser=self.browser.get(self.url)

        username = self.browser.find_element_by_name("username")    
        username.send_keys(USERS['USER1'])   

        password = self.browser.find_element_by_name("password")    
        password.send_keys(USERS['PASSWORD1'])    
  
        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()    
	time.sleep(1)
        
        self.url = ROOT + '/admin'        
        get_browser=self.browser.get(self.url)

    def test_addevtquests(self):
        #self.url = ROOT + '/stdquests/stdquest'
        self.url = ROOT + '/eventquests/addevtquests'
        get_browser=self.browser.get(self.url)
        #time.sleep(120)

        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Strategy Event Quests Added', body.text)

    def test_addndsquests(self):
        #self.url = ROOT + '/stdquests/stdquest'
        self.url = ROOT + '/eventquests/addndsquests'
        get_browser=self.browser.get(self.url)

        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('NDS questions have been added', body.text)

    def test_addhealthquests(self):
        #self.url = ROOT + '/stdquests/stdquest'
        self.url = ROOT + '/eventquests/addhealthquests'
        get_browser=self.browser.get(self.url)

        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Health questions have been added', body.text)

    def test_addoththquests(self):
        #self.url = ROOT + '/stdquests/stdquest'
        self.url = ROOT + '/eventquests/addothquests'
        get_browser=self.browser.get(self.url)
        time.sleep(120)

        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Other questions have been added', body.text)


        
