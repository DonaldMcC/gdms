# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first


from functional_tests import FunctionalTest, ROOT, USERS
import time
from selenium.webdriver.support.ui import WebDriverWait


class AddBasicQuestion (FunctionalTest):

    def setUp(self):
        self.url = ROOT + '/default/user/login'        
        get_browser = self.browser.get(self.url)

        mailstring = USERS['USER2'] + '@user.com'
        email = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name("email"))
        email.send_keys(mailstring)

        password = self.browser.find_element_by_name("password")    
        password.send_keys(USERS['PASSWORD2'])    
  
        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        time.sleep(1)
        submit_button.click()  
        time.sleep(1)
        
        # TODO add in proper url
        self.url = ROOT + '/viewquest/comments/1'
        time.sleep(1)
        get_browser = self.browser.get(self.url)
        time.sleep(1)

    def test_page_displays(self):
        body = self.browser.find_element_by_tag_name('body')
        time.sleep(1)
        self.assertIn('Add a comment', body.text)
        self.assertIn('Reasons', body.text)
        
        commentstring = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_id("plugin_comments_post_body"))
        commentstring.send_keys('This comment was inserted as part of testing phase 3')
        time.sleep(1)
        submit_button = self.browser.find_element_by_xpath("//input[@value='Submit']")
        time.sleep(1)
        submit_button.click()
        time.sleep(2)
        
        body = self.browser.find_element_by_tag_name('body')
        time.sleep(1)
        self.assertIn('phase 3', body.text)

        self.url = ROOT + '/default/user/logout'
        get_browser = self.browser.get(self.url)
