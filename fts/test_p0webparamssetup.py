# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first


from functional_tests import FunctionalTest, ROOT, USERS, testconfig
import time
from selenium.webdriver.support.ui import WebDriverWait


class AnswerQuestion (FunctionalTest):

    def setUp(self):      
        self.url = ROOT + '/default/user/login'        
        get_browser = self.browser.get(self.url)

        mailstring = USERS['USER1']+'@user.com'
        email = self.browser.find_element_by_name("email")

        email = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name("email"))
        email.send_keys(mailstring)

        password = self.browser.find_element_by_name("password")    
        password.send_keys(USERS['PASSWORD1'])    

        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()    
        time.sleep(1)

    def test_addwebparams(self):
        self.url = ROOT + '/admin/website_parameters'
        get_browser = self.browser.get(self.url)
        time.sleep(1)

        time.sleep(2)
        self.browser.find_element_by_xpath("//tr[@id='1']/td[24]/a[2]/span[2]").click()

        self.browser.find_element_by_name("website_url").clear()
        self.browser.find_element_by_name("website_url").send_keys("127.0.0.1:8081")

        self.browser.find_element_by_name("website_title").clear()
        self.browser.find_element_by_name("website_title").send_keys("Net Decision Making")


        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()
        time.sleep(1)

        body = self.browser.find_element_by_tag_name('body')
        time.sleep(1)
        self.assertIn('Website Parameters', body.text)
