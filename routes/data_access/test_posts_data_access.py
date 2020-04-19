from unittest import TestCase
from routes.data_access.posts_data_access import select_post_including_content, select_recent_posts_from_author


class Test(TestCase):
    def test_select_post_including_content(self):
        post = select_post_including_content(3)
        self.assertTrue(post)

    def test_select_recent_posts_from_author(self):
        posts = select_recent_posts_from_author(3)
        self.assertTrue(posts)