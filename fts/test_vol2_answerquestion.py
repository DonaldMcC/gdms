# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first

from functional_tests import FunctionalTest, ROOT, USERS, NUMCYCLES
from ddt import ddt, data, unpack
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


@ddt
class AnswerQuestion (FunctionalTest):

#    def setUp(self):
#        self.url = ROOT + '/default/user/login'
#        get_browser = self.browser.get(self.url)

    @data((USERS['USER2'], USERS['PASSWORD2'], '2', 'in progress'),
          (USERS['USER3'], USERS['PASSWORD3'], '2', 'in progress'),
          (USERS['USER4'], USERS['PASSWORD4'], '2', 'Well done'))
    @unpack
    def test_answer(self, user, passwd, answer, result):
        self.url = ROOT + '/default/user/login'
        get_browser = self.browser.get(self.url)
        mailstring = user + '@user.com'
        email = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name("email"))
        time.sleep(1)
        email.send_keys(mailstring)

        password = self.browser.find_element_by_name("password")
        time.sleep(1)
        password.send_keys(passwd)
        time.sleep(1)
        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        time.sleep(1)
        submit_button.click()
        time.sleep(1)

        self.url = ROOT + '/answer/get_question/quest'
        get_browser = self.browser.get(self.url)
        time.sleep(1)
        ansstring = "(//input[@name='ans'])[" + answer + "]"

        for x in range(0, NUMCYCLES):
            wait = WebDriverWait(self.browser, 12)
            element = wait.until(EC.element_to_be_clickable((By.XPATH, ansstring)))
            element.click()
            urgency = self.browser.find_element_by_id("userquestion_urgency")
            urgency.send_keys("9")
            importance = self.browser.find_element_by_id("userquestion_importance")
            importance.send_keys("10")
            self.browser.find_element_by_id("userquestion_changecat").click()

            category = self.browser.find_element_by_id("userquestion_category")
            category.send_keys("Strategy")
            self.browser.find_element_by_id("userquestion_changescope").click()

            self.browser.find_element_by_id("userquestion_answerreason").send_keys("test_vol2")

            submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
            submit_button.click()
            time.sleep(1)

            body = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_tag_name('body'))
            self.assertIn(result, body.text)
            self.browser.find_element_by_xpath("//input[@value='Next Question']").click()
            time.sleep(1)

        self.url = ROOT + '/default/user/logout'
        get_browser = self.browser.get(self.url)
        time.sleep(3)
