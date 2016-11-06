# These tests are all based on the tutorial at http://killer-web-development.com/

from functional_tests import FunctionalTest, ROOT

class TestHomePage (FunctionalTest):

    def setUp(self):
        # open the browser
        self.url = ROOT + '/'
        get_browser=self.browser.get(self.url)

    def test_can_view_home_page(self):
        self.browser.get(ROOT + '/')
        
        response_code = self.get_response_code(self.url)
        self.assertEqual(response_code, 200)
        
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('you consider important to human progress', body.text)

    def test_has_right_title(self):        
        # Check title is net decision making
        title = self.browser.title
        self.assertEqual('GDMS', title)


class TestAboutPage(FunctionalTest):

    def setUp(self):
        self.url = ROOT + '/about'
        get_browser=self.browser.get(self.url)

    def test_can_view_about_page(self):
        # Let's check if the website was loaded ok
        response_code = self.get_response_code(self.url)
        self.assertEqual(response_code, 200)

    def test_has_right_title(self):
        title = self.browser.title
        self.assertEqual('GDMS', title)

    def test_has_right_heading(self):        
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('About', body.text)
