# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first

import time
from functional_tests import FunctionalTest, ROOT, USERS
from selenium.webdriver.support.ui import WebDriverWait

class AnswerQuestion (FunctionalTest):


    def setUp(self):     
        self.url = ROOT + '/default/user/login'        
        get_browser = self.browser.get(self.url)

        mailstring = USERS['USER4'] + '@user.com'
        email = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name("email"))
        email.send_keys(mailstring)

        password = self.browser.find_element_by_name("password")    
        password.send_keys(USERS['PASSWORD4'])    
  
        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()  
        time.sleep(1)  

        self.url = ROOT + "/review/newindex/"
        get_browser = self.browser.get(self.url)
        time.sleep(1)

    def test_action_review(self):
        #self.browser.find_element_by_id("viewscope_showscope").click()
        #toclick = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_id("viewscope_showscope"))
        #toclick.click()
        #time.sleep(2)
        #self.browser.find_element_by_id("qsortorder1 Priority").click()
        #time.sleep(2)
        #self.browser.find_element_by_css_selector("input.btn").click()
        #time.sleep(2)
        #self.browser.find_element_by_id("qsortorder2 Resolved Date").click()
        #time.sleep(2)
        #self.browser.find_element_by_id("viewscope_showscope").click()
        #time.sleep(2)
        #self.browser.find_element_by_css_selector("input.btn").click()
        #time.sleep(2)
        #self.browser.find_element_by_id("qsortorder3 Submit Date").click()
        #time.sleep(2)
        #self.browser.find_element_by_css_selector("input.btn").click()
        #time.sleep(2)
        #self.browser.find_element_by_link_text("1").click()
        #time.sleep(2)
        #self.browser.find_element_by_xpath("//input[@value='Agree']").click()
        pass
