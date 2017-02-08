# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first
# this should now answer both a question and an issue


from functional_tests import FunctionalTest, ROOT, USERS
import time
from ddt import ddt, data, unpack
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


@ddt
class AnswerAction (FunctionalTest):

    def setUp(self):      
        self.url = ROOT + '/default/user/login'        
        get_browser = self.browser.get(self.url)

    @data((USERS['USER2'], USERS['PASSWORD2'], 'not yet agreed'), (USERS['USER3'], USERS['PASSWORD3'], 'not yet agreed'),
          (USERS['USER4'], USERS['PASSWORD4'], 'is Agreed'))
    @unpack
    def test_answer_action(self, user, passwd, result):
        #username = self.browser.find_element_by_name("username")
        #username = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_name("username"))
        #username.send_keys(user)
        mailstring = user + '@user.com'

        email = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name("email"))
        email.send_keys(mailstring)

        password = self.browser.find_element_by_name("password")
        password.send_keys(passwd)

        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()
        time.sleep(1)

        self.url = ROOT + '/answer/get_question/action'
        get_browser=self.browser.get(self.url)

        ansstring = "(//input[@name='ans'])[2]"
        time.sleep(1)
        wait = WebDriverWait(self.browser, 12)
        element = wait.until(EC.element_to_be_clickable((By.XPATH, ansstring)))
        element.click()

        urgency = self.browser.find_element_by_id("userquestion_urgency")
        urgency.send_keys("7")
        importance = self.browser.find_element_by_id("userquestion_importance")
        importance.send_keys("8")
        self.browser.find_element_by_id("userquestion_changecat").click()
    
        category = self.browser.find_element_by_id("userquestion_category")
        category.send_keys("Strategy")
        self.browser.find_element_by_id("userquestion_changescope").click()

        #self.browser.find_element_by_id("userquestion_answerreason").clear()
        self.browser.find_element_by_id("userquestion_answerreason").send_keys("the right answer selenium testing")
        #driver.find_element_by_css_selector("input.btn").click()        

        #answer.send_keys("1")

        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()
        time.sleep(2)

        body = self.browser.find_element_by_tag_name('body')
        self.assertIn(result, body.text)

        self.url = ROOT + '/default/user/logout'
        get_browser=self.browser.get(self.url)
