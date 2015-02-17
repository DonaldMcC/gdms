# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first


from functional_tests import FunctionalTest, ROOT, USERS
import time
from selenium.webdriver.support.ui import WebDriverWait

class AnswerAction (FunctionalTest):


    def setUp(self):
     
        self.url = ROOT + '/default/user/login'        
        get_browser=self.browser.get(self.url)

        #username = self.browser.find_element_by_name("username")
        username = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_name("username"))       
        username.send_keys(USERS['USER4'])   

        password = self.browser.find_element_by_name("password")    
        password.send_keys(USERS['PASSWORD4'])    


        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click() 
        time.sleep(1)
   
        
        self.url = ROOT + '/answer/get_question/issue'
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

      
    #def test_has_right_heading(self):        
    #    body = self.browser.find_element_by_tag_name('body')
    #    self.assertIn('Answer', body.text)

    def test_answer_action(self):
        #self.browser.find_element_by_xpath("(//input[@name='ans'])[2]").click()
        #self.browser.find_element_by_xpath("(//input[@name='ans'])[2]").click()
        toclick = WebDriverWait(self, 15).until(lambda self : self.browser.find_element_by_xpath("(//input[@name='ans'])[2]"))
        toclick.click()
        urgency = self.browser.find_element_by_id("userquestion_urgency")
        urgency.send_keys("7")
        importance = self.browser.find_element_by_id("userquestion_importance")
        importance.send_keys("8")
        self.browser.find_element_by_id("userquestion_changecat").click()
    
        category = self.browser.find_element_by_id("userquestion_category")
        category.send_keys("Strategy")
        self.browser.find_element_by_id("userquestion_changescope").click()
        
        #activescope = self.browser.find_element_by_id("userquestion_activescope")
        #activescope.select_by_visible_text("2 Continental")

        #continent = self.browser.find_element_by_id("userquestion_continent")
        #continent.select_by_visible_text("Africa (AF)")

        #self.browser.find_element_by_id("userquestion_answerreason").clear()
        self.browser.find_element_by_id("userquestion_answerreason").send_keys("the right answer selenium testing")
        #driver.find_element_by_css_selector("input.btn").click()        

        #answer.send_keys("1")
 
        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()
        time.sleep(1)

        body = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_tag_name('body'))	
        self.assertIn('This action', body.text)

