import unittest
import json
import logintc


class TestLoginTCClient(unittest.TestCase):

    def set_response(self, method, url, headers, body):
        full_url = ''.join(['https://cloud.logintc.com/api', url])
        self.responses[(method, full_url)] = (headers, body)

    def verify_request(self, method, url, body=None):
        full_url = ''.join(['https://cloud.logintc.com/api', url])
        if body is not None:
            return self.requests[(method, full_url)] == body
        else:
            return (method, full_url) in self.requests

    def setUp(self):
        def _mock_request(url, method, headers, body=None):
            if body is not None and body != '':
                self.requests[(method, url)] = json.loads(body)
            else:
                self.requests[(method, url)] = None
            return self.responses[(method, url)]

        self.api_key = 'tZwXzwvdvwFp9oNvRK3ilAs5WZXEwkZ6X0IyexpqjtsDb7POd9x' \
                       'JNw5JaqJsRJRM'
        self.domain_id = 'fa3df768810f0bcb2bfbf0413bfe072e720deb2e'
        self.session_id = '45244fcfe80fbbb0c40f3325487c23053591f575'

        self.user_id = '649fde0d701f636d90ed979bf032b557e48a87cc'
        self.user_username = 'jdoe'
        self.user_email = 'jdoe@cyphercor.com'
        self.user_name = 'John Doe'

        self.domain_name = 'Cisco ASA'
        self.domain_type = 'RADIUS'
        self.domain_key_type = 'PIN'

        self.organization_name = 'Chrome Stage'

        self.token_code = '89hto1p45'

        self.client = logintc.LoginTC(self.api_key)
        self.client.http.request = _mock_request

        self.responses = {}
        self.requests = {}

    def tearDown(self):
        self.responses = {}
        self.requests = {}

    def test_get_session_500_status_raises_exception(self):
        self.set_response('GET',
                          '/domains/%s/sessions/%s' %
                          (self.domain_id, self.session_id),
                          {'status': '500'}, '')

        self.assertRaises(logintc.InternalAPIException,
                          self.client.get_session, self.domain_id,
                          self.session_id)

    def test_get_session(self):
        self.set_response('GET',
                          '/domains/%s/sessions/%s' %
                          (self.domain_id, self.session_id),
                          {'status': '200'},
                          json.dumps({'state': 'pending'}))

        res = self.client.get_session(self.domain_id, self.session_id)

        self.assertEqual({'state': 'pending'}, res)

    def test_create_session_raises_exception(self):
        self.set_response('POST',
                          '/domains/%s/sessions' % self.domain_id,
                          {'status': '404'},
                          json.dumps({'errors': [
                              {'code': 'api.error.notfound.token',
                               'message': 'No token loaded for user.'}]}))

        self.assertRaises(logintc.NoTokenException,
                          self.client.create_session,
                          self.domain_id, 'username')

    def test_create_session(self):
        self.set_response('POST',
                          '/domains/%s/sessions' % self.domain_id,
                          {'status': '200'},
                          json.dumps({'id': self.session_id,
                                     'state': 'pending'}))

        res = self.client.create_session(self.domain_id, username='test')

        self.assertEqual({'id': self.session_id, 'state': 'pending'}, res)

    def test_delete_session(self):
        path = '/domains/%s/sessions/%s' % (self.domain_id, self.session_id)
        self.set_response('DELETE',
                          path,
                          {'status': '200'},
                          '')

        self.client.delete_session(self.domain_id, self.session_id)

        self.assertTrue(self.verify_request('DELETE', path))

    def test_create_user(self):
        self.set_response('POST',
                          '/users',
                          {'status': '200'},
                          json.dumps({'id': self.user_id,
                                      'username': self.user_username,
                                      'email': self.user_email,
                                      'name': self.user_name,
                                      'domains': []
                                      }))

        res = self.client.create_user(self.user_username, self.user_email,
                                      self.user_name,)

        self.assertEqual({'id': self.user_id,
                          'username': self.user_username,
                          'email': self.user_email,
                          'name': self.user_name,
                          'domains': []}, res)

    def test_get_user(self):
        self.set_response('GET',
                          '/users/%s' % self.user_id,
                          {'status': '200'},
                          json.dumps({'id': self.user_id,
                                      'username': self.user_username,
                                      'email': self.user_email,
                                      'name': self.user_name,
                                      'domains': []
                                      }))

        res = self.client.get_user(self.user_id)

        self.assertEqual({'id': self.user_id,
                          'username': self.user_username,
                          'email': self.user_email,
                          'name': self.user_name,
                          'domains': []}, res)

    def test_update_user(self):
        path = '/users/%s' % self.user_id
        self.set_response('PUT',
                          path,
                          {'status': '200'},
                          json.dumps({'id': self.user_id,
                                      'username': self.user_username,
                                      'email': 'new@cyphercor.com',
                                      'name': 'New Name',
                                      'domains': []
                                      }))

        res = self.client.update_user(self.user_id, name='New Name',
                                      email='new@cyphercor.com')

        self.assertEqual({'id': self.user_id,
                          'username': self.user_username,
                          'email': 'new@cyphercor.com',
                          'name': 'New Name',
                          'domains': []}, res)

        self.assertTrue(self.verify_request('PUT', path, {'name': 'New Name',
                                            'email': 'new@cyphercor.com'}))

    def test_delete_user(self):
        path = '/users/%s' % self.user_id
        self.set_response('DELETE',
                          path,
                          {'status': '200'},
                          '')

        self.client.delete_user(self.user_id)

        self.assertTrue(self.verify_request('DELETE', path))

    def test_add_domain_user(self):
        path = '/domains/%s/users/%s' % (self.domain_id, self.user_id)
        self.set_response('PUT',
                          path,
                          {'status': '200'},
                          '')

        self.client.add_domain_user(self.domain_id, self.user_id)

        self.assertTrue(self.verify_request('PUT', path))

    def test_set_domain_users(self):
        users = [{'username': "user1",
                  'email': "user1@cyphercor.com",
                  'name': "user one"},
                 {'username': "user2",
                  'email': "user2@cyphercor.com",
                  'name': "user two"}]
        path = '/domains/%s/users' % self.domain_id

        self.set_response('PUT',
                          path,
                          {'status': '200'},
                          '')

        self.client.set_domain_users(self.domain_id, users)

        self.assertTrue(self.verify_request('PUT', path, users))

    def test_remove_domain_user(self):
        path = '/domains/%s/users/%s' % (self.domain_id, self.user_id)
        self.set_response('DELETE',
                          path,
                          {'status': '200'},
                          '')

        self.client.remove_domain_user(self.domain_id, self.user_id)

        self.assertTrue(self.verify_request('DELETE', path))

    def test_create_user_token(self):
        self.set_response('PUT',
                          '/domains/%s/users/%s/token' %
                          (self.domain_id, self.user_id),
                          {'status': '200'},
                          json.dumps({'state': 'pending',
                                      'code': self.token_code}))

        res = self.client.create_user_token(self.domain_id, self.user_id)

        self.assertEqual({'state': 'pending', 'code': self.token_code}, res)

    def test_get_user_token(self):
        self.set_response('GET',
                          '/domains/%s/users/%s/token' %
                          (self.domain_id, self.user_id),
                          {'status': '200'},
                          json.dumps({'state': 'active'}))

        res = self.client.get_user_token(self.domain_id, self.user_id)

        self.assertEqual({'state': 'active'}, res)

    def test_delete_user_token(self):
        path = '/domains/%s/users/%s/token' % (self.domain_id, self.user_id)
        self.set_response('DELETE',
                          path,
                          {'status': '200'},
                          '')

        self.client.delete_user_token(self.domain_id, self.user_id)

        self.assertTrue(self.verify_request('DELETE', path))

    def test_get_ping(self):
        self.set_response('GET',
                          '/ping',
                          {'status': '200'},
                          json.dumps({'status': 'OK'}))

        res = self.client.get_ping()

        self.assertEqual({'status': 'OK'}, res)

    def test_get_organization(self):
        self.set_response('GET',
                          '/organization',
                          {'status': '200'},
                          json.dumps({'name': self.organization_name}))

        res = self.client.get_organization()

        self.assertEqual({'name': self.organization_name}, res)

    def test_get_domain(self):
        self.set_response('GET',
                          '/domains/%s' % self.domain_id,
                          {'status': '200'},
                          json.dumps({'id': self.domain_id,
                                      'name': self.domain_name,
                                      'type': self.domain_type,
                                      'keyType': self.domain_key_type
                                      }))

        res = self.client.get_domain(self.domain_id)

        self.assertEqual({'id': self.domain_id,
                          'name': self.domain_name,
                          'type': self.domain_type,
                          'keyType': self.domain_key_type}, res)

    def test_get_domain_user(self):
        self.set_response('GET',
                          '/domains/%s/users/%s' % (self.domain_id, self.user_id),
                          {'status': '200'},
                          json.dumps({'id': self.user_id,
                                      'username': self.user_username,
                                      'email': self.user_email,
                                      'name': self.user_name,
                                      'domains': ['%s' % self.domain_id]
                                      }))

        res = self.client.get_domain_user(self.domain_id, self.user_id)

        self.assertEqual({'id': self.user_id,
                          'username': self.user_username,
                          'email': self.user_email,
                          'name': self.user_name,
                          'domains': ['%s' % self.domain_id]
                          }, res)

    def test_get_domain_users(self):
        self.set_response('GET',
                          '/domains/%s/users' % self.domain_id,
                          {'status': '200'},
                          json.dumps([{'id': self.user_id,
                                       'username': self.user_username,
                                       'email': self.user_email,
                                       'name': self.user_name,
                                       'domains': ['%s' % self.domain_id]
                                       }, {'id': self.user_id,
                                           'username': self.user_username,
                                           'email': self.user_email,
                                           'name': self.user_name,
                                           'domains': ['%s' % self.domain_id]
                                           }]))

        res = self.client.get_domain_users(self.domain_id)

        self.assertEqual([{'id': self.user_id,
                           'username': self.user_username,
                           'email': self.user_email,
                           'name': self.user_name,
                           'domains': ['%s' % self.domain_id]
                           }, {'id': self.user_id,
                               'username': self.user_username,
                               'email': self.user_email,
                               'name': self.user_name,
                               'domains': ['%s' % self.domain_id]
                               }], res)

    def test_get_domain_image(self):
        self.set_response('GET',
                          '/domains/%s/image' % self.domain_id,
                          {'status': '200'}, 'Hello World!')

        res = self.client.get_domain_image(self.domain_id)

        self.assertEqual('Hello World!', res)

if __name__ == '__main__':
    unittest.main()
