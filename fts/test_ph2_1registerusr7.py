from functional_tests import FunctionalTest, ROOT, USERS
import time
from selenium.webdriver.support.ui import WebDriverWait

class TestRegisterPage (FunctionalTest):
    def setUp(self):
        # John opens his browser and goes to the home-page of the tukker app        
        self.url = ROOT + '/default/user/register'        
        get_browser=self.browser.get(self.url)

    #def test_can_view_register_page(self):        
    #    # Let's check if the website was loaded ok => response code == 200
    #    response_code = self.get_response_code(self.url)        
    #    self.assertEqual(response_code, 200)    

    #def test_has_right_title(self):                    
    #    title = self.browser.title        
    #    self.assertEqual(u'Networked Decision Making', title)

    def test_put_values_in_register_form(self):    
        first_name = self.browser.find_element_by_name("first_name")    
        first_name.send_keys(USERS['USER7'])    
        
        last_name = self.browser.find_element_by_name("last_name")    
        last_name.send_keys(USERS['USER7'])    
        
        email = self.browser.find_element_by_name("email")    
        email.send_keys("user7@user.com")    

        username = self.browser.find_element_by_name("username")    
        username.send_keys(USERS['USER7'])   

        password = self.browser.find_element_by_name("password")    
        password.send_keys(USERS['PASSWORD7'])    

        verify_password = self.browser.find_element_by_name("password_two")    
        verify_password.send_keys(USERS['PASSWORD7'])    

        register_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        register_button.click()    
    
        #welcome_message = self.browser.find_element_by_css_selector(".flash")
        welcome_message = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_css_selector(".flash"))
        self.assertIn('Welcome to Net Decision Making', welcome_message.text)
