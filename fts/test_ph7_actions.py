# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first

import time
from selenium.webdriver.support.ui import WebDriverWait
from functional_tests import FunctionalTest, ROOT, USERS


class AnswerQuestion (FunctionalTest):

    def setUp(self):
        # John opens his browser and goes to the home-page of the tukker app        
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

        self.url = ROOT + "/review/newindex/action/agreed/priority/0"
        get_browser = self.browser.get(self.url)
        time.sleep(1)

    def test_action_review(self):
        self.browser.find_element_by_css_selector("input.btn").click()
