# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first

from functional_tests import FunctionalTest, ROOT, USERS
import time
from selenium.webdriver.support.ui import WebDriverWait

class NoQuestion (FunctionalTest):

    def setUp(self):    
        self.url = ROOT + '/default/user/login'        
        get_browser=self.browser.get(self.url)

        #username = self.browser.find_element_by_name("username")
        username = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_name("username"))   
        username.send_keys(USERS['USER2'])    

        password = self.browser.find_element_by_name("password")    
        password.send_keys(USERS['PASSWORD2'])    


        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()    
        time.sleep(1)

        self.url = ROOT + '/answer/get_question'        
        get_browser=self.browser.get(self.url)
        time.sleep(1)


    #def test_can_view_submit_page(self):        
    #    # Let's check if the website was loaded ok => response code == 200
    #    response_code = self.get_response_code(self.url)        
    #    self.assertEqual(response_code, 200)    

    #def test_has_right_title(self):
    #    # Check the title is Net Decision Making Press Release
    #    title = self.browser.title
    #    self.assertEqual('Networked Decision Making', title)

    def test_has_right_heading(self):
        #time.sleep(2)      
        #body = self.browser.find_element_by_tag_name('body')
        body = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_tag_name('body'))
        self.assertIn('all questions', body.text)

