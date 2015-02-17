from functional_tests import FunctionalTest, ROOT, USERS
from selenium.webdriver.support.ui import WebDriverWait
import time



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

    def test_put_values_in_register_form(self):  

        first_name = self.browser.find_element_by_name("first_name")    
        first_name.send_keys(USERS['USER2'])    
        
        last_name = self.browser.find_element_by_name("last_name")    
        last_name.send_keys(USERS['USER2'])    
        
        email = self.browser.find_element_by_name("email")    
        email.send_keys("user2@user.com")    

        username = self.browser.find_element_by_name("username")    
        username.send_keys(USERS['USER2'])   

        password = self.browser.find_element_by_name("password")    
        password.send_keys(USERS['PASSWORD2'])    

        verify_password = self.browser.find_element_by_name("password_two")    
        verify_password.send_keys(USERS['PASSWORD2'])    
  
        register_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        register_button.click()
        time.sleep(5)
 	
        #welcome_message = self.browser.find_element_by_css_selector(".flash")
        # welcome_message = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_css_selector(".flash"))
        # self.assertIn('Welcome to Net Decision Making', welcome_message.text)
        body = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_tag_name('body'))
        self.assertIn('Welcome user2', body.text)
