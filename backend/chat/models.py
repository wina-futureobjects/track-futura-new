from django.db import models
from django.contrib.auth.models import User

class ChatThread(models.Model):
    """
    Model for storing chat threads/conversations
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_threads')
    title = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Chat thread {self.id} by {self.user.username}"
    
    class Meta:
        ordering = ['-updated_at']

class ChatMessage(models.Model):
    """
    Model for storing individual chat messages
    """
    SENDER_CHOICES = (
        ('user', 'User'),
        ('ai', 'AI'),
    )

    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_error = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} message in thread {self.thread.id}"
    
    class Meta:
        ordering = ['timestamp'] 