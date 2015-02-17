# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first

from functional_tests import FunctionalTest, ROOT, USERS
import time
from selenium.webdriver.support.ui import WebDriverWait
class AnswerQuestion (FunctionalTest):

    def setUp(self):      
        self.url = ROOT + '/default/user/login'        
        get_browser=self.browser.get(self.url)

        username = self.browser.find_element_by_name("username")    
        username.send_keys(USERS['USER3'])   

        password = self.browser.find_element_by_name("password")    
        password.send_keys(USERS['PASSWORD3'])    
 
        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()    
	time.sleep(1)
        
        self.url = ROOT + '/answer/get_question/action'        
        get_browser=self.browser.get(self.url)
	time.sleep(1)

    def test_answer(self):
        for x in range(0,5):
            #self.browser.find_element_by_xpath("(//input[@name='ans'])[2]").click()
            toclick = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_xpath("(//input[@name='ans'])[2]"))
            toclick.click()
            urgency = self.browser.find_element_by_id("userquestion_urgency")
            urgency.send_keys("9")
            importance = self.browser.find_element_by_id("userquestion_importance")
            importance.send_keys("10")
            self.browser.find_element_by_id("userquestion_changecat").click()
    
            category = self.browser.find_element_by_id("userquestion_category")
            category.send_keys("Strategy")
            self.browser.find_element_by_id("userquestion_changescope").click()
        
            #activescope = self.browser.find_element_by_id("userquestion_activescope")
            #activescope.select_by_visible_text("2 Continental")

            #continent = self.browser.find_element_by_id("userquestion_continent")
            #continent.select_by_visible_text("Africa (AF)")

            #self.browser.find_element_by_id("userquestion_answerreason").clear()
            self.browser.find_element_by_id("userquestion_answerreason").send_keys("test phase6 user 3")
            #driver.find_element_by_css_selector("input.btn").click()        

            #answer.send_keys("1")
   
            submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
            submit_button.click()
	    time.sleep(1)

            body = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_tag_name('body'))	
            self.assertIn('This action is not yet agreed', body.text)
            self.browser.find_element_by_xpath("//input[@value='Next Action']").click()
	    time.sleep(1)

        
