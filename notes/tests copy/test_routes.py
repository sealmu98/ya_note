# notes/tests/test_routes.py
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


class TestRoutes(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = User.objects.create(username='Автор')
        self.not_author = User.objects.create(username='Не автор')
        self.note = Note.objects.create(
            title='Заголовок', text='Текст заметки', slug='note-slug', author=self.author)

    def test_pages_availability_for_anonymous_user(self):
        pages = ['notes:home', 'users:login', 'users:logout', 'users:signup']
        for page in pages:
            url = reverse(page)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_pages_availability_for_auth_user(self):
        self.client.force_login(self.not_author)
        pages = ['notes:list', 'notes:add', 'notes:success']
        for page in pages:
            url = reverse(page)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_pages_availability_for_different_users(self):
        pages = ['notes:detail', 'notes:edit', 'notes:delete']
        for page in pages:
            url = reverse(page, args=[self.note.slug])
            self.client.force_login(self.not_author)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)
            self.client.force_login(self.author)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_redirects(self):
        pages = [
            ('notes:detail', [self.note.slug]),
            ('notes:edit', [self.note.slug]),
            ('notes:delete', [self.note.slug]),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        ]
        login_url = reverse('users:login')
        for page, args in pages:
            url = reverse(page, args=args)
            expected_url = f'{login_url}?next={url}'
            response = self.client.get(url)
            self.assertRedirects(response, expected_url)
