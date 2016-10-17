from functional_tests import FunctionalTest, ROOT, USERS
from ddt import ddt, data, unpack
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.support.ui import Select


# Testuser1 - stays as unspecified
# Testuser2 - specifies Africa and unspecified country and subdivision
# Testuser3 - specifies Africa and South Africa and unspecified subdivision
# Testuser4 - specifies Europe and unspecifoed country
# Testuser5 - specifies Europe and Switzerland and unspecified Subdivision
# Testuser6 - specifies North America and Unspeccified country
# Testuser7 - specifies North America, Canada and unspecified subdivision
# Testuser8 - specifies North America, Canada and Alberta
# Testuser9 - specifies North America, Canada and Saskatchewan

@ddt
class TestRegisterPage (FunctionalTest):
    def setUp(self):
        self.url = ROOT + '/default/user/login'
        get_browser=self.browser.get(self.url)


    #data below was split in two as seems 4 or 5th one is unreliable and difficult to trace why
    @data((USERS['USER2'], USERS['PASSWORD2'], 'Unspecified', 'Unspecified', 'Unspecified'),
          (USERS['USER3'], USERS['PASSWORD3'], 'Unspecified', 'Unspecified', 'Unspecified'),
          (USERS['USER4'], USERS['PASSWORD4'], 'Unspecified', 'Unspecified', 'Unspecified'),
          (USERS['USER5'], USERS['PASSWORD5'], 'Unspecified', 'Unspecified', 'Unspecified'))
    @unpack
    def test_put_values_in_register_form(self, user, passwd, continent, country, subdivision):
        mailstring = user + '@user.com'
        email = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name("email"))
        email.send_keys(mailstring)

        password = self.browser.find_element_by_name("password")
        password.send_keys(passwd)

        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        time.sleep(1)
        submit_button.click()
        time.sleep(1)

        self.url = ROOT + '/default/user/profile'
        get_browser=self.browser.get(self.url)
        time.sleep(2)

        select = Select(self.browser.find_element_by_id("auth_user_continent"))
        time.sleep(1)
        select.select_by_visible_text(continent)

        select = Select(self.browser.find_element_by_id("countryopt"))
        time.sleep(1)
        select.select_by_visible_text(country)
        time.sleep(1)
        select = Select(self.browser.find_element_by_id("subdivopt"))
        select.select_by_visible_text(subdivision)
        time.sleep(1)

        self.browser.find_element_by_xpath("//input[@value='Apply changes']").click()

        # TODO get this changed to changes applied after working
        resultstring = 'Welcome'
        time.sleep(1)


        body = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_tag_name('body'))
        self.assertIn(resultstring, body.text)
        #welcome_message = self.browser.find_element_by_css_selector(".w2p_flash")
        #self.assertEqual(resultstring, welcome_message.text)

        self.url = ROOT + '/default/user/logout'
        get_browser = self.browser.get(self.url)
        time.sleep(1)