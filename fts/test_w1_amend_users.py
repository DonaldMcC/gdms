from functional_tests import FunctionalTest, ROOT, USERS
from ddt import ddt, data, unpack
from selenium.webdriver.support.ui import WebDriverWait
import time


@ddt
class TestRegisterPage (FunctionalTest):
    def setUp(self):
        self.url = ROOT + '/default/user/login'
        get_browser = self.browser.get(self.url)

    #data below was split in two as seems 4 or 5th one is unreliable and difficult to trace why
    @data((USERS['USER2'], USERS['PASSWORD2'], 'ui-multiselect-auth_user_exclude_categories-option-5'),
          (USERS['USER3'], USERS['PASSWORD3'], 'ui-multiselect-auth_user_exclude_categories-option-5'),
          (USERS['USER4'], USERS['PASSWORD4'], 'ui-multiselect-auth_user_exclude_categories-option-13'),
          (USERS['USER5'], USERS['PASSWORD5'], 'ui-multiselect-auth_user_exclude_categories-option-13'))
    @unpack
    def test_put_values_in_register_form(self, user, passwd, category):
        mailstring = user + '@user.com'
        email = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name("email"))
        email.send_keys(mailstring)

        password = self.browser.find_element_by_name("password")
        password.send_keys(passwd)

        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        time.sleep(1)
        submit_button.click()
        time.sleep(2)

        self.url = ROOT + '/default/user/profile'
        get_browser = self.browser.get(self.url)
        time.sleep(2)

        # select = Select(self.browser.find_element_by_id("auth_user_exclude_categories"))
        self.browser.find_element_by_xpath("(//button[@type='button'])[2]").click()
        time.sleep(1)
        self.browser.find_element_by_xpath("//li[2]/a/span[2]").click()
        time.sleep(1)
        self.browser.find_element_by_id(category).click()
        time.sleep(1)
        # select.select_by_visible_text(category)
        time.sleep(3)

        self.browser.find_element_by_xpath("//input[@value='Apply changes']").click()

        # TODO get this changed to changes applied after working
        resultstring = 'Welcome'
        time.sleep(1)

        body = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_tag_name('body'))
        self.assertIn(resultstring, body.text)

        self.url = ROOT + '/default/user/logout'
        get_browser = self.browser.get(self.url)
        time.sleep(2)
