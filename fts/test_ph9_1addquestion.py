# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first


from functional_tests import FunctionalTest, ROOT, USERS
import time
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys


class AddBasicQuestion (FunctionalTest):

    def setUp(self):
        self.url = ROOT + '/default/user/login'        
        get_browser = self.browser.get(self.url)

        mailstring = USERS['USER2'] + '@user.com'
        email = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name("email"))
        email.send_keys(mailstring)

        password = self.browser.find_element_by_name("password")    
        password.send_keys(USERS['PASSWORD2'])    
  
        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        time.sleep(1)
        submit_button.click()  
        time.sleep(1)  
        
        self.url = ROOT + '/submit/new_question'
        time.sleep(1)
        get_browser = self.browser.get(self.url)
        time.sleep(1)

    def test_question(self):
        questiontext = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name('questiontext'))
        questiontext.send_keys("Selenium phase9 Std Vote Time based")

        resmethod = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_id
        ("question_resolvemethod"))

        resmethod.send_keys("StdVote")

        # So thinking this would be time plus 5 minutes for now and just answer and save a question to test if worked 
        # may eventually move to just triggering the scoring at the end of the final response
        # move to this approach as issues with visibility and whole thing becoming a pain
        # min5 = datetime.timedelta(seconds=300)
        # curr = datetime.datetime.now() + min5

        # timestring = curr.strftime("%Y-%m-%d %H:%M:%S")
        # AddBasicQuestion time.sleep(2) #seems needed to make visible

        # due = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_id("question_duedate"))
        # due.clear()
        # time.sleep(1)
        # due.send_keys("2015-06-09 00:27:00")
        # due.send_keys(timestring)

        ans1 = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_id("question_answers"))
        ans1.send_keys("be")
        ans1.send_keys(Keys.RETURN)

        ans2 = WebDriverWait(self, 10).until(
            lambda self: self.browser.find_element_by_xpath("(//input[@id='question_answers'])[2]"))
        ans2.send_keys("not to be")

        submit_button = WebDriverWait(self, 10).until(
            lambda self: self.browser.find_element_by_css_selector("#submit_record__row input"))
        time.sleep(3)
        submit_button.click()
        time.sleep(1)

        welcome_message = self.browser.find_element_by_css_selector(".w2p_flash")
        self.assertIn('Details Submitted', welcome_message.text)
