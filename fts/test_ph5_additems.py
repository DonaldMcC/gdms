# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first
# this is a copy of test_2addaction just to create another action and item to test quick approval


from functional_tests import FunctionalTest, ROOT, USERS
from ddt import ddt, data, unpack
import time
from selenium.webdriver.support.ui import WebDriverWait

@ddt
class AddBasicAction (FunctionalTest):

    def setUp(self):
        self.url = ROOT + '/default/user/login'        
        get_browser = self.browser.get(self.url)

        mailstring = USERS['USER2'] + '@user.com'
        email = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name("email"))
        email.send_keys(mailstring)

        password = self.browser.find_element_by_name("password")    
        password.send_keys(USERS['PASSWORD2'])    

        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()
        time.sleep(1)    

    @data(('/submit/new_question/action', 'Ph5 quick action '), ('/submit/new_question/issue', 'Ph5 quick issue'))
    @unpack
    def test_question(self, urltxt, itemtext):
        self.url = ROOT + urltxt
        get_browser = self.browser.get(self.url)
        time.sleep(2)  # still getting blank category for some reason but not if loaded manually
        # questiontext = self.browser.find_element_by_name('questiontext')
        questiontext = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name('questiontext'))
        questiontext.send_keys(itemtext)

        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()
        time.sleep(1)
  
        welcome_message = self.browser.find_element_by_css_selector(".w2p_flash")
        self.assertIn('Details Submitted', welcome_message.text)
