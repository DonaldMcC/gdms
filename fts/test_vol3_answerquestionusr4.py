# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first


from functional_tests import FunctionalTest, ROOT, USERS
import time
from selenium.webdriver.support.ui import WebDriverWait

class AnswerQuestion (FunctionalTest):


    def setUp(self):
        # John opens his browser and goes to the home-page of the tukker app        
        self.url = ROOT + '/default/user/login'        
        get_browser=self.browser.get(self.url)

        username = self.browser.find_element_by_name("username")    
        username.send_keys(USERS['USER4'])   

        password = self.browser.find_element_by_name("password")    
        password.send_keys(USERS['PASSWORD4'])    

        # John klicks on the register button    
        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")

        submit_button.click()    
	time.sleep(1)
        
        self.url = ROOT + '/answer/get_question/quest'        
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
            #category.select_by_visible_text("Strategy")
            self.browser.find_element_by_id("userquestion_changescope").click()
        
            activescope = self.browser.find_element_by_id("userquestion_activescope")
            if x % 2 == 1:
                activescope.send_keys("3 National")
            else:
                activescope.send_keys("2 Continental")

            #self.browser.find_element_by_id("userquestion_answerreason").clear()
            self.browser.find_element_by_id("userquestion_answerreason").send_keys("the right answer selenium testing")

            time.sleep(1)

            continent = self.browser.find_element_by_id("userquestion_continent")
            continent.send_keys("Europe (EU)")

            time.sleep(1)

            #self.browser.find_element_by_id("userquestion_answerreason").clear()
            self.browser.find_element_by_id("userquestion_answerreason").send_keys("ph5 user4 ")


            if x % 2 == 1:
                country = self.browser.find_element_by_id("countryopt")
                country.send_keys("United Kingdom (EU)")
    

            #answer.send_keys("1")

            # John klicks on the register button    
            submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
            submit_button.click()
	    time.sleep(2)



            body = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_tag_name('body'))	
            self.assertIn('Well done', body.text)


            self.browser.find_element_by_xpath("//input[@value='Next Question']").click()
	    time.sleep(1)

        
