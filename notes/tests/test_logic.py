# notes/tests/test_logic.py
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Test User')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.note_data = {'title': 'Test Note', 'text': 'This is a test note'}

    def create_note(self, client, data):
        response = client.post(reverse('notes:add'), data=data)
        self.assertRedirects(response, reverse('notes:success'))
        return Note.objects.get()

    def test_anonymous_user_cant_create_note(self):
        self.client.post(reverse('notes:add'), data=self.note_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        note = self.create_note(self.auth_client, self.note_data)
        self.assertEqual(note.title, 'Test Note')

    def test_cant_create_two_notes_with_same_slug(self):
        self.create_note(self.auth_client, self.note_data)
        response = self.auth_client.post(
            reverse('notes:add'), data=self.note_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=('test-note - такой slug уже существует, '
                    'придумайте уникальное значение!'))

    def test_slug_is_generated_automatically(self):
        self.note_data['slug'] = ''
        note = self.create_note(self.auth_client, self.note_data)
        self.assertIsNotNone(note.slug)


class TestNoteEditDelete(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Test User')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.note = Note.objects.create(
            title='Test Note', text='This is a test note', author=cls.user)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def edit_note(self, client, url, data):
        response = client.post(url, data=data)
        self.assertRedirects(response, reverse('notes:success'))
        return Note.objects.get()

    def delete_note(self, client, url):
        response = client.delete(url)
        self.assertRedirects(response, reverse('notes:success'))
        return Note.objects.count()

    def test_user_can_edit_own_note(self):
        note = self.edit_note(self.auth_client, self.edit_url, {
                              'title': 'Updated Note',
                              'text': 'This is an updated note'
                              }
                              )
        self.assertEqual(note.title, 'Updated Note')

    def test_user_cant_edit_foreign_note(self):
        foreign_user = User.objects.create(username='Foreign User')
        foreign_note = Note.objects.create(
            title='Foreign Note',
            text='This is a foreign note',
            author=foreign_user)
        edit_url = reverse('notes:edit', args=(foreign_note.slug,))
        response = self.auth_client.post(
            edit_url,
            data={
                'title': 'Updated Foreign Note',
                'text': 'This is an updated foreign note'}
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        foreign_note.refresh_from_db()
        self.assertEqual(foreign_note.title, 'Foreign Note')

    def test_user_can_delete_own_note(self):
        notes_count = self.delete_note(self.auth_client, self.delete_url)
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_foreign_note(self):
        foreign_user = User.objects.create(username='Foreign User')
        foreign_note = Note.objects.create(
            title='Foreign Note',
            text='This is a foreign note',
            author=foreign_user
        )
        delete_url = reverse('notes:delete', args=(foreign_note.slug,))
        response = self.auth_client.delete(delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)
