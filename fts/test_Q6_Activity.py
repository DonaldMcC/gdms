# These tests are all based on the tutorial at http://killer-web-development.com/

from functional_tests import FunctionalTest, ROOT

class TestHomePage (FunctionalTest):

    #def test_can_view_activity_page(self):
    #    self.browser.get(ROOT + '/review/newindex/activity')
    #    body = self.browser.find_element_by_tag_name('body')
    #    self.assertIn('Items Submitted', body.text)
    #    self.assertIn('Resolved Items', body.text)    
    #    self.assertIn('Challenged Items', body.text)
 
    def setUp(self):
        # open the browser
        self.url = ROOT + '/review/newindex/activity'
        get_browser=self.browser.get(self.url)

    def test_can_view_page(self):
        # Let's check if the website was loaded ok => response code == 200
        response_code = self.get_response_code(self.url)
        self.assertEqual(response_code, 200)
        self.assertIn('Items Submitted', body.text)
        self.assertIn('Resolved Items', body.text)    
        self.assertIn('Challenged Items', body.text)

    def test_has_right_title(self):        
        # Check title is net decision making
        title = self.browser.title
        self.assertEqual('Networked Decision Making', title)
