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
        get_browser=self.browser.get(self.url)

    @data((USERS['USER2'], USERS['PASSWORD2'], 'Answer recorded'), (USERS['USER3'], USERS['PASSWORD3'], 'Answer recorded'),
          (USERS['USER4'], USERS['PASSWORD4'], 'Answer recorded'))
    @unpack
    def test_answer_action(self, user, passwd, result):
        #username = self.browser.find_element_by_name("username")
        username = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_name("username"))
        username.send_keys(user)

        password = self.browser.find_element_by_name("password")
        password.send_keys(passwd)


        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()
        time.sleep(1)

        self.url = ROOT + '/review/newindex/action/InProg/priority/0'
        get_browser=self.browser.get(self.url)

        #self.browser.find_element_by_xpath("(//input[@name='ans'])[2]").click()
        toclick = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_xpath("//input[@value='Approve']"))
        toclick.click()

        # would like to know which action was quick approved - maybe log that via the ajaz call
        time.sleep(2)

        body = self.browser.find_element_by_tag_name('body')
        self.assertIn(result, body.text)
