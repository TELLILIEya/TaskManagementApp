import unittest
from TaskManagement import app, db, User

class TestUserService(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:kanunviolon@localhost/soa_app'
        self.app = app.test_client()

        with app.app_context():
            db.create_all()



    def test_registration(self):
        data = {'username': 'testuser2', 'email': 'testuser2@example.com', 'password': 'testpassword'}
        response = self.app.post('/api/users/register', json=data)
        self.assertEqual(response.status_code, 201)

    def test_login_successful(self):
        # Assume you've registered a user with test data in the previous test
        data = {'email': 'testuser@example.com', 'password': 'testpassword'}
        response = self.app.post('/api/users/login', json=data)
        self.assertEqual(response.status_code, 200)

    def test_login_failed(self):
        data = {'email': 'nonexistent@example.com', 'password': 'wrongpassword'}
        response = self.app.post('/api/users/login', json=data)
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()
