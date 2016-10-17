from functional_tests import FunctionalTest, ROOT, USERS
import time
from selenium.webdriver.support.ui import WebDriverWait


class TestLoginPage (FunctionalTest):
    def setUp(self):
        # John opens his browser and goes to the home-page of the tukker app        
        self.url = ROOT + '/default/user/login'        
        get_browser=self.browser.get(self.url)
        time.sleep(1)

    def test_put_values_in_login_form(self):       

        mailstring = USERS['USER2'] + '@user.com'

        email = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name("email"))
        email.send_keys(mailstring)

        password = self.browser.find_element_by_name("password")    
        password.send_keys(USERS['PASSWORD2'])    

        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click() 
        time.sleep(1)   
  
        welcome_message = self.browser.find_element_by_css_selector(".w2p_flash")
        self.assertIn('Welcome to Net Decision Making', welcome_message.text)
        #self.assertEqual(u'Welcome to Net Decision Making\n\xd7', welcome_message.text)
