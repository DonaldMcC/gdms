# These tests are all based on the tutorial at http://killer-web-development.com/
# this test will add various questions that should be assigned to a continent, country and subdivision
# these should all be unrelated so will go  Africa, Switzerland and Alberta
# various users should also update their settings as follows
#
# Testuser1 - stays as unspecified
# Testuser2 - specifies Africa and unspecified country and subdivision
# Testuser3 - specifies Africa and South Africa and unspecified subdivision
# Testuser4 - specifies Europe and unspecified country
# Testuser5 - specifies Europe and Switzerland and unspecified Subdivision
# Testuser6 - specifies North America and Unspeccified country
# Testuser7 - specifies North America, Canada and unspecified subdivision
# Testuser8 - specifies North America, Canada and Alberta
# Testuser9 - specifies North America, Canada and Saskatchewan
# This currently not working properly with chromedriver use firefox for this phase



from functional_tests import FunctionalTest, ROOT, USERS
import time
from ddt import ddt, data, unpack
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


@ddt
class AddBasicQuestion (FunctionalTest):

    def setUp(self):
        self.url = ROOT + '/default/user/login'        
        get_browser=self.browser.get(self.url)
        
    #This is for a std question but with pass being most common answer
    @data(('Strategy category question', 'Ans1', 'Ans2', 'Strategy'))
    @unpack
    def test_question(self, question, ans1, ans2, category):
        mailstring = USERS['USER2'] + '@user.com'

        email = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name("email"))
        email.send_keys(mailstring)

        password = self.browser.find_element_by_name("password")
        password.send_keys(USERS['PASSWORD2'])
        time.sleep(1)
        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        time.sleep(1)
        submit_button.click()
        time.sleep(1)

        self.url = ROOT + '/submit/new_question'
        get_browser=self.browser.get(self.url)
        time.sleep(1)

        questiontext = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_name('questiontext')) 
        questiontext.send_keys(question)

        select = Select(self.browser.find_element_by_id("question_category"))
        time.sleep(1)
        select.select_by_visible_text(category)


        ans1 = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_id("question_answers"))
        ans1.send_keys('yes')
        ans1.send_keys(Keys.RETURN)

        ans2 = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_xpath("(//input[@id='question_answers'])[2]"))
        ans2.send_keys('no')
        time.sleep(1)
        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        time.sleep(1)
        submit_button.click()
        time.sleep(1)

        welcome_message = self.browser.find_element_by_css_selector(".flash")
        self.assertIn('Details Submitted', welcome_message.text)
        time.sleep(1)

        self.url = ROOT + '/default/user/logout'
        get_browser=self.browser.get(self.url)
        time.sleep(1)