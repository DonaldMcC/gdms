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

        username = self.browser.find_element_by_name("username")    
        username.send_keys(USERS['USER3'])   

        password = self.browser.find_element_by_name("password")    
        password.send_keys(USERS['PASSWORD3'])    
  
        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()  
        time.sleep(1)  
        
        self.url = ROOT + "/review/my_answers"
        get_browser=self.browser.get(self.url)
        time.sleep(1)

    def test_action_review(self):
        #self.browser.find_element_by_id("viewscope_showscope").click()
        toclick = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_id("viewscope_showscope"))  
        toclick.click()

        #self.browser.find_element_by_id("scope2 Continental").click()
        toclick = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_id("scope2 Continental"))  
        toclick.click()

        #self.browser.find_element_by_css_selector("input.btn").click()
        toclick = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_css_selector("input.btn"))  
        toclick.click()

        #self.browser.find_element_by_id("viewscope_showcat").click()
        toclick = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_id("viewscope_showcat"))  
        toclick.click()
        
        #self.browser.find_element_by_css_selector("input.btn").click()
        toclick = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_css_selector("input.btn"))  
        toclick.click()

        #self.browser.find_element_by_id("asortorder2 Resolved Date").click()
        toclick = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_id("asortorder2 Resolved Date"))  
        toclick.click()

        #self.browser.find_element_by_css_selector("input.btn").click()
        toclick = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_css_selector("input.btn"))  
        toclick.click()
        
        #self.browser.find_element_by_id("asortorder3 Category").click()
        toclick = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_id("asortorder3 Category"))  
        toclick.click()
        
        #self.browser.find_element_by_css_selector("input.btn").click()
        toclick = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_css_selector("input.btn"))  
        toclick.click()

        #self.browser.find_element_by_id("viewscope_showcat").click()
        toclick = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_id("viewscope_showcat"))  
        toclick.click()

        #self.browser.find_element_by_css_selector("input.btn").click()     
        toclick = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_css_selector("input.btn"))  
        toclick.click


