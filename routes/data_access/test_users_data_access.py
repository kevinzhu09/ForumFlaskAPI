from unittest import TestCase
from routes.data_access.users_data_access import login_social_user


class Test(TestCase):
    def test_login_social_user(self):
        user_id = login_social_user('55334', 'k@gmail.com', 'Google', 'drao')
        self.assertEqual(user_id, 2)
