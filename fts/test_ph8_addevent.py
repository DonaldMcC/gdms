# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first


from functional_tests import FunctionalTest, ROOT, USERS
import time
from selenium.webdriver.support.ui import WebDriverWait

class AddEvent (FunctionalTest):

    def setUp(self):
        self.url = ROOT + '/default/user/login'        
        get_browser=self.browser.get(self.url)

        #username = self.browser.find_element_by_name("username")
        mailstring = USERS['USER2'] + '@user.com'
        email = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name("email"))
        email.send_keys(mailstring)

        password = self.browser.find_element_by_name("password")    
        password.send_keys(USERS['PASSWORD2'])    
  
        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()  
        time.sleep(1)  
        
        self.url = ROOT + '/event/new_event'        
        get_browser=self.browser.get(self.url)
        time.sleep(1)


    def test_has_right_heading(self):        
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Create Event', body.text)

    def test_question(self):     

        event_name = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_id('evt_evt_name'))
        event_name.send_keys("Ph8 test event")

        #locationid = self.browser.find_element_by_id('event_locationid')
        #locationid.send_keys("Unspecified")

        eventdesc = self.browser.find_element_by_id('evt_description')
        eventdesc.send_keys("Ph8 test event fuller description")
        time.sleep(2)
        # eventshared = self.browser.find_element_by_id("evt_evt_shared").click()
        #driver.find_element_by_css_selector("input.btn").click()
        #submit_button = self.browser.find_element_by_css_selector("input.btn").click()
        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        time.sleep(2)
        submit_button.click()
        time.sleep(5)

        welcome_message = self.browser.find_element_by_css_selector(".w2p_flash")
        self.assertIn('Event Created', welcome_message.text)
