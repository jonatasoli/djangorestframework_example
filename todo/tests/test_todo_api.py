from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Todo

from todo.serializers import TodoSerializer


TODO_URL = reverse('todo:todo-list')


class PublicTodoApiTests(TestCase):
    """Test the publically available todos API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access this endpoint"""
        res = self.client.get(TODO_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTodoAPITests(TestCase):
    """Test todos can be retrieved by authorized user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@jonatasoliveira.me',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_todo_list(self):
        """Test retrieving a list of todos"""
        Todo.objects.create(user=self.user,
                            task='first',
                            description='Todo 1')
        Todo.objects.create(user=self.user,
                            task='second',
                            description='Todo 2')

        res = self.client.get(TODO_URL)

        todos = Todo.objects.all().order_by('id')
        serializer = TodoSerializer(todos, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_todos_limited_to_user(self):
        """Test that only todos for authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            'other@jonatasoliveira.me',
            'testpass'
        )
        Todo.objects.create(user=user2,
                            task='New',
                            description='New todo')

        todo = Todo.objects.create(user=self.user,
                                   task='User Task',
                                   description='User Task Description')

        res = self.client.get(TODO_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['task'], todo.task)

    def test_create_todo_successful(self):
        """Test creating a new Todos"""
        payload = {'task': 'Todo Successful', 'description': 'Description Successful'}
        self.client.post(TODO_URL, payload)

        exists = Todo.objects.filter(
            user=self.user,
            task=payload['task']
        ).exists()
        self.assertTrue(exists)

    def test_create_todo_invalid(self):
        """Test creating invalid ingredient fails"""
        payload = {'task:': '', 'description': ''}
        res = self.client.post(TODO_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
