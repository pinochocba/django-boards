from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase


class LoginRequiredPasswordChangeTests(TestCase):
	def test_redirection(self):
		url = reverse('password_change')
		login_url = reverse('login')
		response = self.client.get(url)
		self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=url))


class SuccessfulPasswordChangeTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='john', email='john@doe.com', password='old_password')
		self.url = reverse('password_change')

		data = {
			'old_password': 'old_password',
			'new_password1': 'new_password',
			'new_password2': 'new_password',
		}
		self.client.login(username='john', password='old_password')
		self.response = self.client.post(self.url, data)


	def test_redirection(self):
		'''
		A valid form submission should redirect the user
		'''
		self.assertRedirects(self.response, reverse('password_change_done'))


	def test_password_changed(self):
		'''
		refresh the user instance from database to get the new password
		hash updated by the change password view
		'''
		self.user.refresh_from_db()
		self.assertTrue(self.user.check_password('new_password'))


	def test_user_authentication(self):
		'''
		Create a new request to an arbitrary page.
		The resulting response should now have an 'user' to its context, after
		a success sign up.
		'''
		response = self.client.get(reverse('home'))
		user = response.context.get('user')
		self.assertTrue(user.is_authenticated())


class InvalidPasswordChangeTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='john', email='john@doe.com', password='old_password')
		self.url = reverse('password_change')
		self.client.login(username='john', password='old_password')
		self.response = self.client.post(self.url, {})


	def test_status_code(self):
		'''
		A invalid form submission should return to the same page
		'''
		self.assertEquals(self.response.status_code, 200)


	def test_forms_errors(self):
		form = self.response.context.get('form')
		self.assertTrue(form.errors)


	def test_didnt_change_password(self):
		'''
		refresh the user instance from the database to make
		sure we have the latest data.
		'''
		self.user.refresh_from_db()
		self.assertTrue(self.user.check_password('old_password'))