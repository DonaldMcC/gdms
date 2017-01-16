from functional_tests import FunctionalTest, ROOT, USERS
from ddt import ddt, data, unpack
from selenium.webdriver.support.ui import WebDriverWait
import time


@ddt
class TestRegisterPage (FunctionalTest):
    def setUp(self):      
        self.url = ROOT + '/default/user/register'        
        get_browser = self.browser.get(self.url)

    @data((USERS['USER2'], USERS['PASSWORD2']), (USERS['USER3'], USERS['PASSWORD3']),
          (USERS['USER4'], USERS['PASSWORD4']), (USERS['USER5'], USERS['PASSWORD5']),
          (USERS['USER6'], USERS['PASSWORD6']), (USERS['USER7'], USERS['PASSWORD7']),
          (USERS['USER8'], USERS['PASSWORD8']), (USERS['USER9'], USERS['PASSWORD9']))
    @unpack
    def test_put_values_in_regester_form(self, user, passwd):

        first_name = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name("first_name"))
        first_name.clear()
        first_name.send_keys(user)

        last_name = self.browser.find_element_by_name("last_name")
        last_name.clear()
        last_name.send_keys(user)

        mailstring = user+'@user.com'
        # if user == 'Testuser2':
        #    mailstring = 'newglobalstrategy@gmail.com'
        email = self.browser.find_element_by_name("email")
        email.clear()
        email.send_keys(mailstring)

        password = self.browser.find_element_by_name("password")
        password.clear()
        password.send_keys(passwd)

        verify_password = self.browser.find_element_by_name("password_two")
        verify_password.clear()
        verify_password.send_keys(passwd)
        time.sleep(1)

        register_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        time.sleep(1)
        register_button.click()
        resultstring = 'Welcome ' + user
        time.sleep(1)
        body = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_tag_name('body'))
        self.assertIn(resultstring, body.text)

        self.url = ROOT + '/default/user/logout'
        get_browser = self.browser.get(self.url)
        time.sleep(1)
