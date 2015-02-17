# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first

import time
from functional_tests import FunctionalTest, ROOT, USERS
from selenium.webdriver.support.ui import WebDriverWait
import functional_tests

class AnswerQuestion (FunctionalTest):

    def setUp(self):       
        self.url = ROOT + '/default/user/login'        
        get_browser=self.browser.get(self.url)

        username = self.browser.find_element_by_name("username")    
        username.send_keys(USERS['USER2'])   

        password = self.browser.find_element_by_name("password")    
        password.send_keys(USERS['PASSWORD2'])    
   
        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()   
        time.sleep(1) 

        self.url = ROOT + "/review/index/action/myy"
        get_browser=self.browser.get(self.url)

    def test_action_review(self):
        self.browser.find_element_by_id("viewscope_showscope").click()
        time.sleep(1)
        self.browser.find_element_by_id("sortorder1 Priority").click()
        time.sleep(1)
        self.browser.find_element_by_css_selector("input.btn").click()
        time.sleep(2)
        self.browser.find_element_by_link_text("A").click()


