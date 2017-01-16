# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first


from functional_tests import FunctionalTest, ROOT, USERS
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.alert import Alert


class AnswerQuestion (FunctionalTest):

    def setUp(self):
        self.url = ROOT + '/default/user/login'        
        get_browser = self.browser.get(self.url)

        mailstring = USERS['USER1']+'@user.com'
        email = self.browser.find_element_by_name("email")

        email = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name("email"))
        email.send_keys(mailstring)

        # username = self.browser.find_element_by_name("username")
        # username = WebDriverWait(self, 10).until(lambda self : self.browser.find_element_by_name("username"))
        # username.send_keys(USERS['USER1'])
        password = self.browser.find_element_by_name("password")    
        password.send_keys(USERS['PASSWORD1'])    

        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()    
        time.sleep(1)        

        self.url = ROOT + '/admin'        
        get_browser = self.browser.get(self.url)


    def test_datasetup(self):
        self.url = ROOT + '/admin/datasetup'        
        get_browser=self.browser.get(self.url)
        time.sleep(1)

        self.browser.execute_script('alert("hi")')
        time.sleep(2)
        alert = self.browser.switch_to_alert()
        alert.accept()

        body = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_tag_name('body'))
        self.assertIn('Standard data has been added', body.text)

    def test_addcategories(self):
        self.url = ROOT + '/admin/addstdcategories'        
        get_browser=self.browser.get(self.url)
        time.sleep(1)

        body = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_tag_name('body'))
        self.assertIn('Standard categories have been added', body.text)

    def test_addresolvemethods(self):
        self.url = ROOT + '/admin/addresolvemethods'
        get_browser = self.browser.get(self.url)
        time.sleep(1)

        body = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_tag_name('body'))
        self.assertIn('Standard resolution methods have been added', body.text)

    def test_addmessages(self):
        self.url = ROOT + '/admin/stdmessages'        
        get_browser = self.browser.get(self.url)
        time.sleep(1)

        body = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_tag_name('body'))

        self.assertIn('Standard messages have been added', body.text)
