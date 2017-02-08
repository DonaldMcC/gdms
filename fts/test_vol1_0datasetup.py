# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first
# so think this should change to ddt and do the following
# Add the questions which is a link and a message
# Visit the page and confirm event setup that way
# View the eventmap and redraw
# Test that question visible on the page


from functional_tests import FunctionalTest, ROOT, USERS
from ddt import ddt, data, unpack
import time
from selenium.webdriver.support.ui import WebDriverWait


@ddt
class AnswerQuestion (FunctionalTest):

    def setUp(self):       
        self.url = ROOT + '/default/user/login'
        get_browser = self.browser.get(self.url)

        mailstring = USERS['USER1'] + '@user.com'
        email = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name("email"))
        email.send_keys(mailstring)

        password = self.browser.find_element_by_name("password")
        password.send_keys(USERS['PASSWORD1'])

        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()
        time.sleep(1)

        self.url = ROOT + '/admin'
        get_browser = self.browser.get(self.url)

    @data((r'/eventquests/addevtquests', 'Strategy Event Quests Added'),
          (r'/eventquests/addndsquests', 'NDS questions have been added'),
          (r'/eventquests/addhealthquests', 'Health questions have been added'),
          (r'/eventquests/addothquests', 'Other questions have been added'))
    @unpack
    def test_addquests(self, url, result):
        self.url = ROOT + url
        get_browser = self.browser.get(self.url)

        body = self.browser.find_element_by_tag_name('body')
        self.assertIn(result, body.text)
