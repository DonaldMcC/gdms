# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first

import time
from functional_tests import FunctionalTest, ROOT, USERS
from ddt import ddt, data, unpack
import functional_tests
import time
from selenium.webdriver.support.ui import WebDriverWait

@ddt
class AnswerQuestion (FunctionalTest):

    def setUp(self):  
        self.url = ROOT + '/default/user/login'
        get_browser=self.browser.get(self.url)

    @data((USERS['USER2'], USERS['PASSWORD2']),
          (USERS['USER3'], USERS['PASSWORD3']),
          (USERS['USER4'], USERS['PASSWORD4']))
    @unpack
    def test_challenge(self, user, passwd):
        username = self.browser.find_element_by_name("username")
        username.send_keys(user)

        password = self.browser.find_element_by_name("password")
        password.send_keys(passwd)

        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")

        submit_button.click()
        time.sleep(1)

        self.url = ROOT + "/viewquest/index/3"
        #self.url = functional_tests.questref

        get_browser=self.browser.get(self.url)
        time.sleep(2)
        challreason = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_name("challreason"))	
        #self.browser.find_element_by_name("challreason").clear()
        challreason.clear()
        challreason.send_keys("this is just wrong")
        self.browser.find_element_by_xpath("//input[@value='Challenge']").click()

        time.sleep(3)
        #target = self.browser.find_element_by_css_selector("#target")
        #self.assertIn('Challenge accepted', target.text)
        body = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_tag_name('body'))
        self.assertIn('Challenge accepted', body.text)