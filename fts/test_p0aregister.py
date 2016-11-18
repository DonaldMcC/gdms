from functional_tests import FunctionalTest, ROOT, USERS
import time
from ddt import ddt, data, unpack
from selenium.webdriver.support.ui import WebDriverWait


#element = WebDriverWait(driver, 10).until(lambda driver : driver.find_element_by_id("createFolderCreateBtn"))
@ddt
class TestRegisterPage (FunctionalTest):
    def setUp(self):     
        self.url = ROOT + '/default/user/register'        
        get_browser=self.browser.get(self.url)

    #def test_can_view_register_page(self):        
    #    response_code = self.get_response_code(self.url)        
    #    self.assertEqual(response_code, 200)    

    #def test_has_right_title(self):                     
    #    title = self.browser.title        
    #    #self.assertEqual(u'Net Decision Making: Registration', title)
    #    self.assertIn('Networked Decision Making', title)

    @data((USERS['USER1'], USERS['PASSWORD1']))
    @unpack
    def test_put_values_in_regester_form(self, user, passwd):

        #first_name = self.browser.find_element_by_name("first_name")
        first_name = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_name("first_name"))
        first_name.clear()
        first_name.send_keys(user)
        
        last_name = self.browser.find_element_by_name("last_name")
        last_name.clear()
        last_name.send_keys(user)

        mailstring = user+'@user.com'
        email = self.browser.find_element_by_name("email")
        email.clear()
        email.send_keys(mailstring)

        # username = self.browser.find_element_by_name("username")
        # username.clear()
        # username.send_keys(user)

        password = self.browser.find_element_by_name("password")
        password.clear()
        password.send_keys(passwd)

        verify_password = self.browser.find_element_by_name("password_two")
        verify_password.clear()
        verify_password.send_keys(passwd)

        register_button = self.browser.find_element_by_css_selector("#submit_record__row input")

        register_button.click()
        time.sleep(3)
        resultstring='Welcome '+ user
        body = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_tag_name('body'))
        self.assertIn(resultstring, body.text)



