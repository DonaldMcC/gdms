from functional_tests import FunctionalTest, ROOT, USERS, questref
import functional_tests
import time
from ddt import ddt, data, unpack
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

@ddt
class AnswerQuestion (FunctionalTest):

    @data((USERS['USER2'], USERS['PASSWORD2'], '2', 'in progress', 'yes'),
          (USERS['USER3'], USERS['PASSWORD3'], '2', 'in progress', 'no'),
          (USERS['USER4'], USERS['PASSWORD4'], '2', 'in progress', 'no'),
          (USERS['USER5'], USERS['PASSWORD5'], '2', 'in progress', 'no'))
    @unpack
    def test_answer(self, user, passwd, answer, result, owner):
        self.url = ROOT + '/default/user/login'
        get_browser = self.browser.get(self.url)
        time.sleep(1)
        mailstring = user + '@user.com'
        email = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name("email"))
        email.send_keys(mailstring)

        password = self.browser.find_element_by_name("password")
        password.send_keys(passwd)
        time.sleep(1)
        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        time.sleep(1)
        submit_button.click()
        time.sleep(1)
        self.url = ROOT + '/answer/get_question/quest'
<<<<<<< HEAD
        get_browser=self.browser.get(self.url)
        time.sleep(2)
        ansstring = "(//input[@name='ans'])[" + answer +"]"
=======
        get_browser = self.browser.get(self.url)
        time.sleep(1)
        ansstring = "(//input[@name='ans'])[" + answer + "]"
>>>>>>> master

        wait = WebDriverWait(self.browser, 12)
        element = wait.until(EC.element_to_be_clickable((By.XPATH, ansstring)))
        element.click()
        urgency = self.browser.find_element_by_id("userquestion_urgency")
        urgency.send_keys("9")
        importance = self.browser.find_element_by_id("userquestion_importance")
        importance.send_keys("10")
        self.browser.find_element_by_id("userquestion_changecat").click()

        # category.select_by_visible_text("Strategy")
        self.browser.find_element_by_id("userquestion_changescope").click()

        activescope = self.browser.find_element_by_id("userquestion_activescope")
        activescope.send_keys("2 Continental")

        # self.browser.find_element_by_id("userquestion_answerreason").clear()
        self.browser.find_element_by_id("userquestion_answerreason").send_keys("ph9 usera")

        time.sleep(2)

        category = self.browser.find_element_by_id("userquestion_category")
        category.send_keys("Strategy")

        continent = self.browser.find_element_by_id("userquestion_continent")
        continent.send_keys("Europe (EU)")


        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()
        time.sleep(1)

        body = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_tag_name('body'))

        # self.assertIn('This question is in progress', body.text)
        self.assertIn(result, body.text)

        if owner == 'yes':
            #print('url:' +  self.browser.current_url)
            functional_tests.votequest = self.browser.current_url
            #print functional_tests.votequest

        self.url = ROOT + '/default/user/logout'
        get_browser = self.browser.get(self.url)
        time.sleep(3)
