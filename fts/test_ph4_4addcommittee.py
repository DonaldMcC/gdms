# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first


from functional_tests import FunctionalTest, ROOT, USERS
import time
from selenium.webdriver.support.ui import WebDriverWait


class AddEvent (FunctionalTest):

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
        
        self.url = ROOT + '/admin/access_group'
        get_browser = self.browser.get(self.url)
        time.sleep(1)

    def test_has_right_heading(self):
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Access Group Maintenance', body.text)

    def test4(self):
        toclick = WebDriverWait(self, 12).until(lambda self: self.browser.find_element_by_css_selector("span.buttontext.button"))
        toclick.click()
        time.sleep(2)

        self.browser.find_element_by_id("access_group_group_name").clear()
        self.browser.find_element_by_id("access_group_group_name").send_keys("Committee")
        self.browser.find_element_by_id("access_group_group_desc").clear()
        self.browser.find_element_by_id("access_group_group_desc").send_keys("This is an admin appointed committee group")
        self.browser.find_element_by_id("access_group_group_type").send_keys("admin")
        self.browser.find_element_by_css_selector("input.btn.btn-primary").click()
        time.sleep(2)
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('committee', body.text)

    def test_adduser2fromgrid(self):
        self.url = ROOT + '/admin/group_members'
        get_browser = self.browser.get(self.url)
        time.sleep(1)

        toclick = WebDriverWait(self, 12).until(lambda self: self.browser.find_element_by_css_selector("span.buttontext.button"))
        toclick.click()
        time.sleep(5)

        self.browser.find_element_by_id("group_members_access_group").send_keys("committee")
        self.browser.find_element_by_id("group_members_auth_userid").send_keys("Testuser2")
        self.browser.find_element_by_css_selector("input.btn.btn-primary").click()
        time.sleep(2)
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('user2', body.text)

    def test_adduser3fromgrid(self):
        self.url = ROOT + '/admin/group_members'
        get_browser = self.browser.get(self.url)
        time.sleep(1)

        toclick = WebDriverWait(self, 12).until(lambda self: self.browser.find_element_by_css_selector("span.buttontext.button"))
        toclick.click()
        time.sleep(5)

        self.browser.find_element_by_id("group_members_access_group").send_keys("committee")
        self.browser.find_element_by_id("group_members_auth_userid").send_keys("Testuser3")
        self.browser.find_element_by_css_selector("input.btn.btn-primary").click()
        time.sleep(2)
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('user3', body.text)

    def test_adduser4fromgrid(self):
        self.url = ROOT + '/admin/group_members'
        get_browser = self.browser.get(self.url)
        time.sleep(1)

        toclick = WebDriverWait(self, 12).until(lambda self: self.browser.find_element_by_css_selector("span.buttontext.button"))
        toclick.click()
        time.sleep(5)

        self.browser.find_element_by_id("group_members_access_group").send_keys("committee")
        self.browser.find_element_by_id("group_members_auth_userid").send_keys("Testuser4")
        self.browser.find_element_by_css_selector("input.btn.btn-primary").click()
        time.sleep(2)
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('user4', body.text)
