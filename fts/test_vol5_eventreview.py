# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first

from functional_tests import FunctionalTest, ROOT, USERS, NUMCYCLES
import time
from ddt import ddt, data, unpack
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class TestEventPage(FunctionalTest):

    def testarchving(self):
        self.url = ROOT + '/default/user/login'        
        get_browser=self.browser.get(self.url)
        mailstring = USERS['USER1'] + '@user.com'
        email = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name("email"))
        email.send_keys(mailstring)

        password = self.browser.find_element_by_name("password")    
        password.send_keys(USERS['PASSWORD1'])    
  
        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        time.sleep(1)
        submit_button.click()  
        time.sleep(1)  
        self.url = ROOT + '/'        
        get_browser=self.browser.get(self.url)
        time.sleep(1)
        driver.find_element_by_link_text("Healthcare Review").click()
        reviewlink1 = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_link_text("Healthcare Review")) 
        revewlink1.click()
        reviewlink2 = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_xpath("//input[@value='Review Event']")) 
        revewlink2.click()
        reviewlink3 = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_xpath("//input[@value='Archive']")) 
        revewlink3.click()
        reviewlink4 = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_xpath("(//button[@type='button'])[4]")) 
        revewlink4.click()
        reviewlink5 = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_xpath("//input[@value='View Event']")) 
        revewlink5.click()
        time.sleep(3)
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Archived and Shared', body.text)
        
        self.url = ROOT + '/default/user/logout'
        get_browser=self.browser.get(self.url)
        time.sleep(1)
        



