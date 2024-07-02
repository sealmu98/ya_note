# notes/tests/test_content.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = User.objects.create(username='Автор')
        self.not_author = User.objects.create(username='Не автор')
        self.note = Note.objects.create(
            title='Заголовок', text='Текст заметки', slug='note-slug', author=self.author)

    def test_notes_list_for_different_users(self):
        clients = [(self.author, True), (self.not_author, False)]
        for client, note_in_list in clients:
            self.client.force_login(client)
            url = reverse('notes:list')
            response = self.client.get(url)
            object_list = response.context['object_list']
            self.assertEqual((self.note in object_list), note_in_list)

    def test_pages_contains_form(self):
        pages = [
            ('notes:add', None),
            ('notes:edit', [self.note.slug]),
        ]
        for page, args in pages:
            url = reverse(page, args=args)
            self.client.force_login(self.author)
            response = self.client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)
