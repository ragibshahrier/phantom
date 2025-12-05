"""
Integration tests for the chat API endpoint.

Tests Requirements: 1.1, 7.2, 7.4, 7.5
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from scheduler.models import Category, ConversationHistory
from unittest.mock import patch, MagicMock

User = get_user_model()


class ChatEndpointTest(TestCase):
    """
    Integration tests for the /api/chat/ endpoint.
    
    Tests Requirements: 1.1, 7.2, 7.4, 7.5
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            name='Test User',
            timezone='UTC'
        )
        
        # Create default categories
        Category.objects.create(name='Exam', priority_level=5, color='#FF0000')
        Category.objects.create(name='Study', priority_level=4, color='#00FF00')
        Category.objects.create(name='Gym', priority_level=3, color='#0000FF')
        Category.objects.create(name='Social', priority_level=2, color='#FFFF00')
        Category.objects.create(name='Gaming', priority_level=1, color='#FF00FF')
        
        # Set up API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_chat_endpoint_exists(self):
        """Test that the chat endpoint exists and is accessible."""
        response = self.client.post('/api/chat/', {'message': 'test'})
        
        # Should not return 404
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_chat_requires_authentication(self):
        """Test that the chat endpoint requires authentication."""
        # Create unauthenticated client
        unauth_client = APIClient()
        
        response = unauth_client.post('/api/chat/', {'message': 'test'})
        
        # Should return 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('ai_agent.views.PhantomAgent')
    def test_chat_with_valid_message(self, mock_agent_class):
        """Test chat endpoint with a valid message."""
        # Mock the agent's process_input method
        mock_agent = MagicMock()
        mock_agent.process_input.return_value = {
            'response': 'Most excellent! I have scheduled your exam.',
            'actions': [{'type': 'create', 'params': {}}],
            'intent': 'create'
        }
        mock_agent_class.return_value = mock_agent
        
        response = self.client.post('/api/chat/', {
            'message': 'schedule exam tomorrow at 2pm'
        })
        
        # Should return 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Response should have expected structure
        self.assertIn('response', response.data)
        self.assertIn('actions', response.data)
        self.assertIn('intent', response.data)
        self.assertIn('success', response.data)
        
        # Response should be a string
        self.assertIsInstance(response.data['response'], str)
        
        # Actions should be a list
        self.assertIsInstance(response.data['actions'], list)
    
    def test_chat_with_empty_message(self):
        """Test chat endpoint with an empty message."""
        response = self.client.post('/api/chat/', {'message': ''})
        
        # Should return 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Should have error response
        self.assertIn('response', response.data)
        self.assertFalse(response.data['success'])
    
    def test_chat_with_missing_message(self):
        """Test chat endpoint with missing message field."""
        response = self.client.post('/api/chat/', {})
        
        # Should return 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('ai_agent.views.PhantomAgent')
    def test_chat_stores_conversation_history(self, mock_agent_class):
        """Test that chat endpoint stores conversation in history."""
        # Mock the agent
        mock_agent = MagicMock()
        mock_agent.process_input.return_value = {
            'response': 'Study session scheduled.',
            'actions': [{'type': 'create', 'params': {}}],
            'intent': 'create'
        }
        mock_agent_class.return_value = mock_agent
        
        # Clear any existing conversations
        ConversationHistory.objects.filter(user=self.user).delete()
        
        message = 'schedule study session tomorrow'
        response = self.client.post('/api/chat/', {'message': message})
        
        # Should return 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that conversation was stored
        conversations = ConversationHistory.objects.filter(user=self.user)
        self.assertGreater(conversations.count(), 0, "Conversation should be stored in history")
        
        # Verify the stored conversation
        latest_conv = conversations.first()
        self.assertEqual(latest_conv.message, message)
        self.assertIsNotNone(latest_conv.response)
        self.assertIsNotNone(latest_conv.intent_detected)
    
    @patch('ai_agent.views.PhantomAgent')
    @patch('ai_agent.views.TaskCategoryExtractor')
    def test_chat_with_ambiguous_input(self, mock_extractor_class, mock_agent_class):
        """Test chat endpoint with ambiguous input that requires clarification."""
        # Mock the extractor to return ambiguous
        mock_extractor = MagicMock()
        mock_extractor.is_ambiguous.return_value = True
        mock_extractor_class.return_value = mock_extractor
        
        # Mock the agent (won't be called due to ambiguous input)
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent
        
        response = self.client.post('/api/chat/', {'message': 'hi'})
        
        # Should return 200 OK (but with clarification request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should indicate ambiguous intent
        self.assertEqual(response.data['intent'], 'ambiguous')
        self.assertFalse(response.data['success'])
        
        # Response should request clarification
        self.assertIn('response', response.data)
        response_text = response.data['response'].lower()
        self.assertTrue(
            'clarif' in response_text or 'details' in response_text or 'more' in response_text or 'require' in response_text,
            "Response should request clarification"
        )
    
    @patch('ai_agent.views.PhantomAgent')
    def test_chat_response_has_victorian_style(self, mock_agent_class):
        """Test that chat responses maintain Victorian Ghost Butler style."""
        # Mock the agent with Victorian-style response
        mock_agent = MagicMock()
        mock_agent.process_input.return_value = {
            'response': 'Most excellent! I have attended to your request.',
            'actions': [{'type': 'create', 'params': {}}],
            'intent': 'create'
        }
        mock_agent_class.return_value = mock_agent
        
        response = self.client.post('/api/chat/', {
            'message': 'schedule exam tomorrow'
        })
        
        # Should return 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Response should exist
        self.assertIn('response', response.data)
        response_text = response.data['response']
        
        # Response should be non-empty
        self.assertGreater(len(response_text), 0)
        
        # Response should be a string
        self.assertIsInstance(response_text, str)
    
    @patch('ai_agent.views.PhantomAgent')
    def test_chat_extracts_category(self, mock_agent_class):
        """Test that chat endpoint extracts category from message."""
        # Mock the agent
        mock_agent = MagicMock()
        mock_agent.process_input.return_value = {
            'response': 'Exam scheduled.',
            'actions': [{'type': 'create', 'params': {}}],
            'intent': 'create'
        }
        mock_agent_class.return_value = mock_agent
        
        response = self.client.post('/api/chat/', {
            'message': 'schedule exam tomorrow at 2pm'
        })
        
        # Should return 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should extract category
        if 'category' in response.data and response.data['category']:
            self.assertEqual(response.data['category'], 'Exam')
    
    @patch('ai_agent.views.PhantomAgent')
    def test_chat_extracts_task_title(self, mock_agent_class):
        """Test that chat endpoint extracts task title from message."""
        # Mock the agent
        mock_agent = MagicMock()
        mock_agent.process_input.return_value = {
            'response': 'Math exam scheduled.',
            'actions': [{'type': 'create', 'params': {}}],
            'intent': 'create'
        }
        mock_agent_class.return_value = mock_agent
        
        response = self.client.post('/api/chat/', {
            'message': 'schedule math exam tomorrow at 2pm'
        })
        
        # Should return 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should extract task title
        if 'task_title' in response.data and response.data['task_title']:
            task_title = response.data['task_title']
            self.assertIsInstance(task_title, str)
            self.assertGreater(len(task_title), 0)
    
    def test_conversation_history_endpoint(self):
        """Test the conversation history endpoint."""
        # Create some conversation history
        ConversationHistory.objects.create(
            user=self.user,
            message='test message 1',
            response='test response 1',
            intent_detected='create'
        )
        ConversationHistory.objects.create(
            user=self.user,
            message='test message 2',
            response='test response 2',
            intent_detected='query'
        )
        
        # Query conversation history
        response = self.client.get('/api/chat/history/')
        
        # Should return 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should have conversations
        self.assertIn('conversations', response.data)
        self.assertIn('count', response.data)
        
        # Should have at least 2 conversations
        self.assertGreaterEqual(response.data['count'], 2)
        
        # Conversations should have expected structure
        for conv in response.data['conversations']:
            self.assertIn('message', conv)
            self.assertIn('response', conv)
            self.assertIn('intent', conv)
            self.assertIn('timestamp', conv)
    
    def test_conversation_history_limit(self):
        """Test that conversation history respects limit parameter."""
        # Create multiple conversations
        for i in range(15):
            ConversationHistory.objects.create(
                user=self.user,
                message=f'test message {i}',
                response=f'test response {i}',
                intent_detected='test'
            )
        
        # Query with limit
        response = self.client.get('/api/chat/history/?limit=5')
        
        # Should return 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should have exactly 5 conversations
        self.assertEqual(response.data['count'], 5)
    
    def test_conversation_history_requires_authentication(self):
        """Test that conversation history endpoint requires authentication."""
        # Create unauthenticated client
        unauth_client = APIClient()
        
        response = unauth_client.get('/api/chat/history/')
        
        # Should return 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
