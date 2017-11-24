from unittest import TestCase
from BizTransfer import app


class TestLogin(TestCase):
    def test_login(self):
        rv = login('omarelmohri@ipconnex.com', 'H0ught0n')
        self.assertIn(b'Successful', rv.data)


def login(username, password):
    assert isinstance(app, object)
    #  return app. post('/login/', data=dict(username=username, password=password), follow_redictects=True)