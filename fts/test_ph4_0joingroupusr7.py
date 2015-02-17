# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first

import time
from functional_tests import FunctionalTest, ROOT, USERS
import functional_tests
from selenium.webdriver.support.ui import WebDriverWait

class AnswerQuestion (FunctionalTest):

    def setUp(self):  
        self.url = ROOT + '/default/user/login'        
        get_browser=self.browser.get(self.url)

        username = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_name("username"))    
        username.send_keys(USERS['USER7'])

        password = self.browser.find_element_by_name("password")    
        password.send_keys(USERS['PASSWORD7'])
  
        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()    
        time.sleep(1)
        
        self.url = ROOT + "/accessgroups"
        get_browser=self.browser.get(self.url)
        time.sleep(1)

    #this test below is ok on basis there is only ONE group to join
    def test_challenge(self):
        self.browser.find_element_by_xpath("//input[@value='Join']").click()

        time.sleep(3)
        #target = self.browser.find_element_by_css_selector("#target")
        #self.assertIn('Challenge accepted', target.text)
        body = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_tag_name('body'))
        self.assertIn('You joined the group', body.text)
