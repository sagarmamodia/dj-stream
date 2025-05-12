from django.test import TestCase, SimpleTestCase
from django.urls import reverse
import json
from unittest.mock import patch
from .models import User, OAuthToken, JwtRefreshToken, AuthTypes

class GetAuthUrlViewTest(TestCase):
    
    def test_get_auth_url(self):
        response = self.client.get(reverse('auth-url'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json() 
        self.assertIn("auth_url", data)
        self.assertTrue(isinstance(data['auth_url'], str))

class OauthCallBackTest(TestCase):
   
    @patch('auth_app.views.jwt_auth.generate_jwt_token')
    @patch('auth_app.views.requests.get')
    @patch('auth_app.views.requests.post')
    def test_user_does_not_exist(self, mock_request_post, mock_request_get,  mock_generate_jwt_token):
        mock_request_post.return_value.json.return_value = {
                'access_token': 'access_token',
                'refresh_token': 'refresh_token',
        }

        mock_request_get.return_value.json.return_value = {
                'name': 'name',
                'email': 'email@email.com'
        }
        mock_generate_jwt_token.return_value = ('jwt_token', 'jwt_refresh_token')


        session = self.client.session
        session['oauth_state'] = 'state'
        session.save()

        response = self.client.get(reverse('google-oauth-callback'), {'state': 'state', 'code': 'code'})
        
        #test if data has been stored in database
        user = User.objects.filter(email='email@email.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.name, 'name')
        self.assertEqual(user.email, 'email@email.com')
        self.assertIsNone(user.password)

        oauth_token = OAuthToken.objects.filter(user=user).first()
        self.assertIsNotNone(oauth_token)
        self.assertEqual(oauth_token.user.id, user.id)
        self.assertEqual(oauth_token.access_token, 'access_token')
        self.assertEqual(oauth_token.refresh_token, 'refresh_token')

        jwt_refresh_token_object = JwtRefreshToken.objects.filter(user=user).first()
        self.assertIsNotNone(jwt_refresh_token_object)
        self.assertEqual(jwt_refresh_token_object.user.id, user.id)
        self.assertEqual(jwt_refresh_token_object.refresh_token, 'jwt_refresh_token')

        #test if response is correct or not
        response_data = response.json()
        self.assertIsNotNone(response_data)
        self.assertTrue('access_token' in response_data.keys())
        self.assertTrue('refresh_token' in response_data.keys())
        self.assertTrue('user_info' in response_data.keys())
        self.assertEqual(response_data['access_token'], 'jwt_access_token')
        self.assertEqual(response_data['refresh_token'], 'jwt_refresh_token')
        self.assertEqual(response_data['user_info']['name'], 'name')
        self.assertEqual(response_data['user_info']['email'], 'email@email.com')

    @patch('auth_app.views.jwt_auth.generate_jwt_token')
    @patch('auth_app.views.requests.get')
    @patch('auth_app.views.requests.post')
    def test_user_does_not_exist(self, mock_request_post, mock_request_get,  mock_generate_jwt_token):
        mock_request_post.return_value.json.return_value = {
                'access_token': 'access_token',
                'refresh_token': 'refresh_token',
        }

        mock_request_get.return_value.json.return_value = {
                'name': 'name',
                'email': 'email@email.com'
        }
        mock_generate_jwt_token.return_value = ('jwt_access_token', 'jwt_refresh_token')
        User.objects.create(auth_type=AuthTypes.OAUTH.value, name='name2', email='email@email.com')

        session = self.client.session
        session['oauth_state'] = 'state'
        session.save()

        response = self.client.get(reverse('google-oauth-callback'), {'state': 'state', 'code': 'code'})
        
        #test if the data has been stored in database
        user = User.objects.filter(email='email@email.com').first()
        self.assertEqual(User.objects.filter(email='email@email.com').count(), 1)
        self.assertIsNotNone(user)
        self.assertEqual(user.name, 'name2')
        self.assertEqual(user.email, 'email@email.com')
        self.assertIsNone(user.password)

        oauth_token = OAuthToken.objects.filter(user=user).first()
        self.assertIsNotNone(oauth_token)
        self.assertEqual(oauth_token.user.id, user.id)
        self.assertEqual(oauth_token.access_token, 'access_token')
        self.assertEqual(oauth_token.refresh_token, 'refresh_token')

        jwt_refresh_token_object = JwtRefreshToken.objects.filter(user=user).first()
        self.assertIsNotNone(jwt_refresh_token_object)
        self.assertEqual(jwt_refresh_token_object.user.id, user.id)
        self.assertEqual(jwt_refresh_token_object.refresh_token, 'jwt_refresh_token')

        #test if response is correct or not
        response_data = response.json()
        self.assertIsNotNone(response_data)
        self.assertTrue('access_token' in response_data.keys())
        self.assertTrue('refresh_token' in response_data.keys())
        self.assertTrue('user_info' in response_data.keys())
        self.assertEqual(response_data['access_token'], 'jwt_access_token')
        self.assertEqual(response_data['refresh_token'], 'jwt_refresh_token')
        self.assertEqual(response_data['user_info']['name'], 'name2')
        self.assertEqual(response_data['user_info']['email'], 'email@email.com')







