# test.py


import os
import unittest

from views import app, db
from config import basedir
from models import User

TEST_DB = 'test.db'


class ALLTests(unittest.TestCase):

    ############################
    #### setup and teardown ####
    ############################

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()

    # executed after each test
    def tearDown(self):
        db.drop_all()

    # helper functions
    def login(self, name, password):
        return self.app.post('/', data=dict(name=name, password=password),
                      follow_redirects=True)

    def register(self, name, email, password, confirm):
        return self.app.post('register/', data=dict(name=name,
                                                    email=email,
                                                    password=password,
                                                    confirm=confirm),
                             follow_redirects=True)

    def logout(self):
        return self.app.get('logout/', follow_redirects=True)

    def create_user(self, name, email, password):
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

    def create_admin_user(self):
        new_user = User(name='Superman',
                        email='admin@realpython.com',
                        password='allpowerful',
                        role='admin')
        db.session.add(new_user)
        db.session.commit()

    def create_task(self):
        return self.app.post('add/', data=dict(name='Go to the bank',
                                        due_date='02/05/2014',
                                        priority=1,
                                        posted_date='02/04/2014',
                                        status='1'),
                      follow_redirects=True)

    # each test should start with 'test'
    def test_user_setup(self):
        new_user = User('rwest', 'robert.david.west@gmail.com',
                        'testpassword')
        db.session.add(new_user)
        db.session.commit()
        test = db.session.query(User).all()
        for t in test:
            t.name
        assert t.name == "rwest"

    def test_form_is_present_on_login_page(self):
        response = self.app.get('/')
        self.assertEquals(response.status_code, 200)
        self.assertIn('Please sign in to access your task list', response.data)

    def test_users_cannot_login_unless_registered(self):
        response = self.login('foo','bar')
        self.assertIn('Invalid username or password.', response.data)

    def test_users_can_login(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        response = self.login('Michael', 'python')
        self.assertIn('You are logged in. Go crazy.', response.data)

    def test_invalid_form_data(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        response = self.login('alert("alert box!");', 'foo')
        self.assertIn('Invalid username or password.', response.data)

    def test_form_is_present_on_register_page(self):
        response = self.app.get('register/')
        self.assertEquals(response.status_code, 200)
        self.assertIn('Please register to start a task list', response.data)

    def test_user_registration(self):
        self.app.get('register/', follow_redirects=True)
        response = self.register('Michael', 'michael@realpython.com',
                                 'python', 'python')
        self.assertIn('Thanks for registering. Please login.', response.data)

    def test_duplicate_user_registration_throws_error(self):
        self.app.get('register/', follow_redirects=True)
        self.register('Michael', 'michael@realpython.com', 'python',
                      'python')

        self.app.get('register/', follow_redirects=True)
        response = self.register('Michael', 'michael@realpython.com',
                                 'python', 'python')
        self.assertIn('Oh no! That username and/or email already exist.',
                      response.data)

    def test_user_registration_field_errors(self):
        response = self.register('Michael', 'michael@realpython.com',
                                 'python', '')
        self.assertIn('This field is required', response.data)

    def test_logged_in_users_can_logout(self):
        self.register('johnsmith', 'jonhn@cats.com', 'onkonkonk', 'onkonkonk')
        self.login('johnsmith', 'onkonkonk')
        response = self.logout()
        self.assertIn('You are logged out. Bye. :(', response.data)

    def test_not_logged_in_users_cannot_logout(self):
        response = self.logout()
        self.assertNotIn('You are logged out. Bye. :(', response.data)

    def test_logged_in_users_can_access_tasks_page(self):
        self.register('johnsmith', 'jonhn@cats.com', 'onkonkonk', 'onkonkonk')
        self.login('johnsmith', 'onkonkonk')
        response = self.app.get('tasks/')
        self.assertEquals(response.status_code, 200)
        self.assertIn('Add a new task', response.data)

    def not_logged_in_users_cannot_access_tasks_page(self):
        response = self.app.get('tasks/', follow_redirects=True)
        self.assertIn('You need to login first', response.data)

    def test_users_can_add_task(self):
        self.create_user('davesmith', 'some@email.com', 'badpassword')
        self.login('davesmith', 'badpassword')
        self.app.get('tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn('New entry was successfully posted. Thanks.',
                      response.data)

    def test_users_cannot_add_tasks_when_error(self):
        self.create_user('davesmith', 'some@email.com', 'badpassword')
        self.login('davesmith', 'badpassword')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.post('add/', data=dict(name='Go to the bank',
                                                   due_date='',
                                                   priority='1',
                                                   posted_date='02/05/2015',
                                                   status='1'),
                                  follow_redirects=True)
        self.assertIn('This field is required', response.data)

    def test_users_can_mark_tasks_as_complete(self):
        self.create_user('davesmith', 'some@email.com', 'badpassword')
        self.login('davesmith', 'badpassword')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get('complete/1/', follow_redirects=True)
        self.assertIn('The task was marked as complete. Nice', response.data)

    def test_users_can_delete_tasks(self):
        self.create_user('davesmith', 'some@email.com', 'badpassword')
        self.login('davesmith', 'badpassword')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get('delete/1/', follow_redirects=True)
        self.assertIn('The task was deleted. Why not add a new one?', response.data)

    def test_users_cannot_complete_tasks_that_were_not_created_by_them(self):
        self.create_user('davesmith', 'some@email.com', 'badpassword')
        self.login('davesmith', 'badpassword')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user('notdave', 'notdaves@emai.com', 'defnothispwordinnit')
        self.login('notdave', 'defnothispwordinnit')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get('complete/1/', follow_redirects=True)
        self.assertIn('You can only update tasks that belong to you.',
                      response.data)

    def test_users_cannot_delete_tasks_that_are_not_created_by_them(self):
        self.create_user('davesmith', 'some@email.com', 'badpassword')
        self.login('davesmith', 'badpassword')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user('notdave', 'notdaves@emai.com', 'defnothispwordinnit')
        self.login('notdave', 'defnothispwordinnit')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get('delete/1/', follow_redirects=True)
        self.assertIn('You can only delete tasks that belong to you.',
                      response.data)

    def test_default_user_role(self):

        db.session.add(User('Johnny', 'john@doe.com', 'johnny'))
        db.session.commit()

        users = db.session.query(User).all()
        print users
        for user in users:
            self.assertEquals(user.role, 'user')

    def test_admin_users_can_complete_tasks_that_are_not_created_by_them(self):
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'allpowerful')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get("complete/1/", follow_redirects=True)
        self.assertNotIn(
            'You can only update tasks that belong to you.',
            response.data
        )

    def test_admin_users_can_delete_tasks_that_are_not_created_by_them(self):
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'allpowerful')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get("delete/1/", follow_redirects=True)
        self.assertNotIn('You can only delete tasks that belong to you',
                         response.data)

if __name__ == '__main__':
    unittest.main()
