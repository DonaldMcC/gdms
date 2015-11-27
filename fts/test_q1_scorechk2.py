from functional_tests import FunctionalTest, ROOT, USERS
from ddt import ddt, data, unpack
from selenium.webdriver.support.ui import WebDriverWait
import time

@ddt
class TestScores (FunctionalTest):
    def setUp(self):
        self.url = ROOT + '/default/user/login'
        get_browser = self.browser.get(self.url)

    @data((USERS['USER2'], USERS['PASSWORD2'], 80, 3, 10), (USERS['USER3'], USERS['PASSWORD3'], 80, 3, 10),
          (USERS['USER4'], USERS['PASSWORD4'], 92, 3, 10), (USERS['USER5'], USERS['PASSWORD5'], 80, 0, 5),
          (USERS['USER6'], USERS['PASSWORD6'], 70, 0, 3), (USERS['USER7'], USERS['PASSWORD7'], 30, 0, 2))
    @unpack
    def test_put_values_in_regester_form(self, user, passwd, score, rating, questions):
        mailstring = user + '@user.com'
        email = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name("email"))
        email.send_keys(mailstring)

        password = self.browser.find_element_by_name("password")
        #password.send_keys(USERS['PASSWORD2'])
        password.send_keys(passwd)

        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()
        time.sleep(1)

        scorestring = 'Score: ' + str(score)
        ratingstring = 'Rating: ' + str(rating)
        questionstring = 'Questions: ' + str(questions)

        time.sleep(1)
        body = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_tag_name('body'))
        self.assertIn(scorestring, body.text)
        self.assertIn(ratingstring, body.text)
        self.assertIn(questionstring, body.text)

        self.url = ROOT + '/default/user/logout'
        get_browser = self.browser.get(self.url)