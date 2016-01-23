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

    # setup below for user7 being set twice seems stupid however for reasons that escape me the
    # setting of unspecified subdivision isn't working if done in a single step hence Manitoba
    # temporarily wheeled into play

    @data((USERS['USER7'], USERS['PASSWORD7'], 'North America (NA)', 'Canada (NA)', 'Manitoba'),
          (USERS['USER6'], USERS['PASSWORD6'], 'North America (NA)', 'Unspecified', 'Unspecified'),
          (USERS['USER8'], USERS['PASSWORD8'], 'North America (NA)', 'Canada (NA)', 'Alberta'),
          (USERS['USER9'], USERS['PASSWORD9'], 'North America (NA)', 'Canada (NA)', 'Saskatchewan'),
          (USERS['USER7'], USERS['PASSWORD7'], 'North America (NA)', 'Canada (NA)', 'Unspecified'))
    @unpack
    def test_put_values_in_register_form(self, user, passwd, continent, country, subdivision):
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

        self.url = ROOT + '/default/user/profile'
        get_browser=self.browser.get(self.url)
        time.sleep(1)

        select = Select(self.browser.find_element_by_id("auth_user_continent"))
        time.sleep(1)
        select.select_by_visible_text(continent)
        time.sleep(1)
        select = Select(self.browser.find_element_by_id("countryopt"))
        time.sleep(2)
        select.select_by_visible_text(country)
        time.sleep(3)
        select = Select(self.browser.find_element_by_id("subdivopt"))
        time.sleep(3)
        select.select_by_visible_text(subdivision)
        time.sleep(3)
        self.browser.find_element_by_xpath("//input[@value='Apply changes']").click()

        # TODO get this changed to changes applied after working
        resultstring = 'Welcome'
        time.sleep(2)

        body = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_tag_name('body'))
        self.assertIn(resultstring, body.text)
        #welcome_message = self.browser.find_element_by_css_selector(".flash")
        #self.assertEqual(resultstring, welcome_message.text)

        self.url = ROOT + '/default/user/logout'
        get_browser = self.browser.get(self.url)
        time.sleep(1)