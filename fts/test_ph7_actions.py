# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first

import time
from selenium.webdriver.support.ui import WebDriverWait
from functional_tests import FunctionalTest, ROOT, USERS
import functional_tests


class AnswerQuestion (FunctionalTest):

    def setUp(self):
        # John opens his browser and goes to the home-page of the tukker app        
        self.url = ROOT + '/default/user/login'        
        get_browser=self.browser.get(self.url)

        username = self.browser.find_element_by_name("username")    
        username.send_keys(USERS['USER4'])   

        password = self.browser.find_element_by_name("password")    
        password.send_keys(USERS['PASSWORD4'])    
  
        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")

        submit_button.click()    
        time.sleep(1)

        self.url = ROOT + "/review/index/action/agreed/priority/0"
        get_browser=self.browser.get(self.url)
        time.sleep(1)

    def test_action_review(self):
        #self.browser.find_element_by_link_text("Actions").click()
        #toclick = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_link_text("Actions"))
        #toclick.click()
        #time.sleep(1)
        self.browser.find_element_by_id("sortorder1 Priority").click()
        time.sleep(1)
        self.browser.find_element_by_css_selector("input.btn").click()
        time.sleep(1)
        self.browser.find_element_by_id("viewscope_showcat").click()
        time.sleep(1)
        self.browser.find_element_by_id("sortorder2 Due Date").click()
        time.sleep(1)
        self.browser.find_element_by_css_selector("input.btn").click()
        time.sleep(1)

        self.browser.find_element_by_id("sortorder3 Resolved Date").click()
        time.sleep(1)
        self.browser.find_element_by_css_selector("input.btn").click()
        time.sleep(1)
        self.browser.find_element_by_id("sortorder4 Submit Date").click()
        time.sleep(1)
        self.browser.find_element_by_css_selector("input.btn").click()
        time.sleep(1)
        self.browser.find_element_by_id("sortorder5 Responsible").click()
        time.sleep(1)
        self.browser.find_element_by_css_selector("input.btn").click()
        time.sleep(1)
        self.browser.find_element_by_id("viewscope_showscope").click()
        time.sleep(1)
        self.browser.find_element_by_css_selector("input.btn").click()

