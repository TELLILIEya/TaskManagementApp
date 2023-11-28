import unittest
from TaskManagement import app, db, Task

class TestTaskrService(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:kanunviolon@localhost/soa_app'
        self.app = app.test_client()

        with app.app_context():
            db.create_all()



    def add_task(self):
        data = {"title": "Nouvelle tâche", "description": "Description de la tâche","deadline":"11/12/2023","completed":False,"user_id":1}
        response = self.app.post('/api/tasks', json=data)
        self.assertEqual(response.status_code, 201)

    
if __name__ == '__main__':
    unittest.main()
