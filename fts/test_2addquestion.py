# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first


from functional_tests import FunctionalTest, ROOT, USERS
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys


class AddBasicQuestion (FunctionalTest):


    def setUp(self):     
        self.url = ROOT + '/default/user/login'        
        get_browser=self.browser.get(self.url)
        time.sleep(2)

        #username = self.browser.find_element_by_name("username")
        username = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_name("username"))   
        username.send_keys(USERS['USER2'])       

        password = self.browser.find_element_by_name("password")    
        password.send_keys(USERS['PASSWORD2'])    

        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()
        time.sleep(1)  
        
        self.url = ROOT + '/submit/new_question'        
        get_browser=self.browser.get(self.url)
        time.sleep(1)


    #def test_can_view_submit_page(self):        
    #    response_code = self.get_response_code(self.url)        
    #    self.assertEqual(response_code, 200)    

    #def test_has_right_title(self):
    #    title = self.browser.title
    #    self.assertEqual('Networked Decision Making', title)

    #def test_has_right_heading(self):        
    #    body = self.browser.find_element_by_tag_name('body')
    #    self.assertIn('Submit Question', body.text)

    def test_question(self):
        time.sleep(2) #still getting blank category for some reason but not if loaded manually        
        #questiontext = self.browser.find_element_by_name('questiontext')
        questiontext = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_name('questiontext'))
        questiontext.send_keys("Selenium to be or not to be")


        #numanswers = self.browser.find_element_by_name('numanswers')
        #numanswers = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_name('numanswers'))
        #numanswers.send_keys("2")


        #ans1 = self.browser.find_element_by_name('ans1')
        ans1 = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_id("question_answers"))
        ans1.send_keys("be")
        ans1.send_keys(Keys.RETURN)

        #ans2 = self.browser.find_element_by_name('ans2')
        ans2 = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_xpath("(//input[@id='question_answers'])[2]"))
        ans2.send_keys("not to be")

        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()
        time.sleep(1)
  
        welcome_message = self.browser.find_element_by_css_selector(".flash")
        self.assertEqual(u'Details Submitted\n\xd7', welcome_message.text)

        time.sleep(120)
