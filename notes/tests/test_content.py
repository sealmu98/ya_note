# notes/tests/test_content.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestNotesListPage(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='user1')
        self.user2 = User.objects.create(username='user2')
        self.note1 = Note.objects.create(
            title='Note 1', text='Text 1', author=self.user1)
        self.note2 = Note.objects.create(
            title='Note 2', text='Text 2', author=self.user1)
        self.note3 = Note.objects.create(
            title='Note 3', text='Text 3', author=self.user2)
        self.client.force_login(self.user1)

    def test_notes_on_page(self):
        response = self.client.get(reverse('notes:list'))
        self.assertIsNotNone(response.context)
        self.assertIn('object_list', response.context)
        self.assertQuerysetEqual(response.context[
            'object_list'].order_by('pk'), [
            self.note1, self.note2], ordered=False)
        self.assertNotIn(self.note3, response.context['object_list'])


class TestNoteCreatePage(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='user')
        self.client.force_login(self.user)

    def test_form_on_page(self):
        response = self.client.get(reverse('notes:add'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)


class TestNoteUpdatePage(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='user')
        self.note = Note.objects.create(
            title='Note', text='Text', author=self.user)
        self.client.force_login(self.user)

    def test_form_on_page(self):
        response = self.client.get(
            reverse('notes:edit', args=[self.note.slug]))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
