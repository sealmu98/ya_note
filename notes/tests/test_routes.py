# notes/tests/test_routes.py
from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username='testuser1')
        cls.user2 = User.objects.create(username='testuser2')
        cls.note = Note.objects.create(title='Test Note', author=cls.user1)

    def login_user(self, user):
        self.client.force_login(user)

    def test_anonymous_user_can_access_home_page(self):
        response = self.client.get(reverse('notes:home'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authenticated_user_can_access_pages(self):
        self.login_user(self.user1)
        pages = [
            ('notes:list', HTTPStatus.OK),
            ('notes:add', HTTPStatus.OK),
            ('notes:success', HTTPStatus.OK),
        ]
        for page, status_code in pages:
            response = self.client.get(reverse(page))
            self.assertEqual(response.status_code, status_code)

    def test_only_author_can_access_note_pages(self):
        self.login_user(self.user2)
        pages = [
            ('notes:detail', self.note.slug, HTTPStatus.NOT_FOUND),
            ('notes:edit', self.note.slug, HTTPStatus.NOT_FOUND),
            ('notes:delete', self.note.slug, HTTPStatus.NOT_FOUND),
        ]
        for page, slug, status_code in pages:
            response = self.client.get(reverse(page, args=(slug,)))
            self.assertEqual(response.status_code, status_code)

    def test_anonymous_user_redirected_to_login_page(self):
        response = self.client.get(reverse('notes:list'))
        self.assertRedirects(response, reverse(
            'users:login') + '?next=' + reverse('notes:list'))
