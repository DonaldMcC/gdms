# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first
# this should now answer both a question and an issue


from functional_tests import FunctionalTest, ROOT, USERS
import time
from ddt import ddt, data, unpack
from selenium.webdriver.support.ui import WebDriverWait

@ddt
class AnswerAction (FunctionalTest):

    def setUp(self):      
        self.url = ROOT + '/default/user/login'        
        get_browser = self.browser.get(self.url)

    @data((USERS['USER2'], USERS['PASSWORD2'], 'not yet agreed'),
          (USERS['USER3'], USERS['PASSWORD3'], 'not yet agreed'),
          (USERS['USER4'], USERS['PASSWORD4'], 'is Agreed'))
    @unpack
    def test_answer_issue(self, user, passwd, result):
        # This is a bit of a repeat of above with different url - but it might change otherwise will loop

        mailstring = user + '@user.com'

        email = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name("email"))
        email.send_keys(mailstring)

        password = self.browser.find_element_by_name("password")
        password.send_keys(passwd)

        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()
        time.sleep(1)
        
        self.url = ROOT + '/answer/get_question/issue'
        time.sleep(1)
        get_browser=self.browser.get(self.url)

        # self.browser.find_element_by_xpath("(//input[@name='ans'])[2]").click()
        toclick = WebDriverWait(self, 15).until(lambda self: self.browser.find_element_by_xpath("(//input[@name='ans'])[2]"))
        toclick.click()
        urgency = self.browser.find_element_by_id("userquestion_urgency")
        urgency.send_keys("7")
        importance = self.browser.find_element_by_id("userquestion_importance")
        importance.send_keys("8")
        self.browser.find_element_by_id("userquestion_changecat").click()

        category = self.browser.find_element_by_id("userquestion_category")
        category.send_keys("Strategy")
        self.browser.find_element_by_id("userquestion_changescope").click()

        # self.browser.find_element_by_id("userquestion_answerreason").clear()
        self.browser.find_element_by_id("userquestion_answerreason").send_keys("the right answer selenium testing")
        # driver.find_element_by_css_selector("input.btn").click()

        # answer.send_keys("1")

        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()
        time.sleep(2)

        body = self.browser.find_element_by_tag_name('body')
        self.assertIn(result, body.text)

        self.url = ROOT + '/default/user/logout'
        get_browser = self.browser.get(self.url)
