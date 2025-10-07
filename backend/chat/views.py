from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import ChatThread, ChatMessage
from .serializers import ChatThreadSerializer, ChatMessageSerializer
from .openai_service import openai_service

class ChatThreadViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing chat threads
    """
    serializer_class = ChatThreadSerializer
    permission_classes = []  # Temporarily disable auth for testing

    def get_queryset(self):
        # For testing without auth, get all active threads
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            return ChatThread.objects.filter(user=self.request.user, is_active=True)
        return ChatThread.objects.filter(is_active=True)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        # For testing without auth, set user to None
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save(user=None)

    @action(detail=True, methods=['POST'])
    def add_message(self, request, pk=None):
        """
        Add a new message to the thread and generate AI response
        """
        thread = self.get_object()
        serializer = ChatMessageSerializer(data=request.data)

        if serializer.is_valid():
            # Save user message
            user_message = serializer.save(thread=thread)

            # If it's a user message, generate AI response
            if request.data.get('sender') == 'user':
                try:
                    # Get conversation history
                    conversation_history = ChatMessage.objects.filter(thread=thread).order_by('timestamp')

                    # Get project_id from request if available
                    project_id = None
                    print(f"[CHAT] Request data: {request.data}")
                    print(f"[CHAT] Query params: {request.query_params}")
                    # Try to get project_id from request data or query params
                    project_id = request.data.get('project_id') or request.query_params.get('project_id')
                    if project_id:
                        try:
                            project_id = int(project_id)
                            print(f"[CHAT] ✅ Using project_id: {project_id}")
                        except (ValueError, TypeError):
                            project_id = None
                            print(f"[CHAT] ❌ Invalid project_id format: {project_id}")
                    else:
                        print(f"[CHAT] ⚠️ No project_id found in request!")

                    # Generate AI response with real data
                    ai_response = openai_service.generate_response(
                        user_message.content,
                        conversation_history,
                        project_id=project_id
                    )

                    # Save AI response
                    ai_message = ChatMessage.objects.create(
                        thread=thread,
                        content=ai_response,
                        sender='ai'
                    )

                    # Update thread's updated_at timestamp
                    thread.save()

                    # Return both messages
                    return Response({
                        'user_message': ChatMessageSerializer(user_message).data,
                        'ai_message': ChatMessageSerializer(ai_message).data
                    }, status=status.HTTP_201_CREATED)

                except Exception as e:
                    # If AI fails, still return user message with error details
                    print(f"❌ AI response failed: {str(e)}")
                    import traceback
                    traceback.print_exc()

                    # Create an error message for the user
                    error_message = ChatMessage.objects.create(
                        thread=thread,
                        content=f"I encountered an error processing your request. Error: {str(e)}",
                        sender='ai'
                    )

                    return Response({
                        'user_message': ChatMessageSerializer(user_message).data,
                        'ai_message': ChatMessageSerializer(error_message).data
                    }, status=status.HTTP_201_CREATED)

            # Update thread's updated_at timestamp
            thread.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'])
    def archive(self, request, pk=None):
        """
        Archive (soft delete) a thread
        """
        thread = self.get_object()
        thread.is_active = False
        thread.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['POST'])
    def clear_all_history(self, request):
        """
        Clear all chat history (archive all threads)
        """
        if hasattr(request, 'user') and request.user.is_authenticated:
            threads = ChatThread.objects.filter(user=request.user, is_active=True)
        else:
            threads = ChatThread.objects.filter(is_active=True)
        
        threads.update(is_active=False)
        return Response({'message': 'All chat history cleared'}, status=status.HTTP_200_OK)

class ChatMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing chat messages
    """
    serializer_class = ChatMessageSerializer
    permission_classes = []  # Temporarily disable auth for testing

    def get_queryset(self):
        thread_id = self.request.query_params.get('thread_id')
        if thread_id:
            # For testing without auth, don't filter by user
            if hasattr(self.request, 'user') and self.request.user.is_authenticated:
                thread = get_object_or_404(ChatThread, id=thread_id, user=self.request.user)
            else:
                thread = get_object_or_404(ChatThread, id=thread_id)
            return ChatMessage.objects.filter(thread=thread)
        return ChatMessage.objects.none() 