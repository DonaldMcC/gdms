# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first


from functional_tests import FunctionalTest, ROOT, USERS
from ddt import ddt, data, unpack
import time
from selenium.webdriver.support.ui import WebDriverWait

@ddt
class ClearQuests (FunctionalTest):

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

    def test_search(self):
        self.url = ROOT + '/search/newsearch.html'
        get_browser = self.browser.get(self.url)

        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Search string', body.text)

        searchstring = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name("searchstring"))
        searchstring.send_keys('strategy')

        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()
        time.sleep(2)

        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Search results', body.text)

        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('global strategy', body.text)

