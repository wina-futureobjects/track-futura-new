import openai
from django.conf import settings
import json
import asyncio
import sys
import os

# Add the parent directory to sys.path to import common modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from common.data_integration_service import DataIntegrationService
except ImportError:
    # Fallback if import fails
    DataIntegrationService = None

class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY', '')
        try:
            self.client = openai.OpenAI(api_key=self.api_key) if self.api_key else None
        except Exception as e:
            print(f"Failed to initialize OpenAI client: {e}")
            self.client = None

    def generate_response(self, user_message, conversation_history=None, project_id=None):
        """Generate AI response using OpenAI GPT with real data"""
        if not self.client:
            return "I'm sorry, the AI service is currently unavailable. Please try again later."

        try:
            # Get real data from the project if available
            data_context = ""
            if project_id and DataIntegrationService:
                try:
                    data_service = DataIntegrationService(project_id=project_id)

                    # Get recent posts and comments for context
                    recent_posts = data_service.get_all_posts(limit=20, days_back=7)
                    recent_comments = data_service.get_all_comments(limit=30, days_back=7)
                    engagement_metrics = data_service.get_engagement_metrics(days_back=7)

                    data_context = f"""

                    CURRENT PROJECT DATA CONTEXT:
                    Recent Posts ({len(recent_posts)} posts from last 7 days):
                    {json.dumps(recent_posts[:5], default=str) if recent_posts else "No recent posts found"}

                    Recent Comments ({len(recent_comments)} comments from last 7 days):
                    {json.dumps(recent_comments[:10], default=str) if recent_comments else "No recent comments found"}

                    Engagement Overview:
                    - Total Posts: {engagement_metrics.get('total_posts', 0)}
                    - Total Likes: {engagement_metrics.get('total_likes', 0)}
                    - Total Comments: {engagement_metrics.get('total_comments', 0)}
                    - Total Shares: {engagement_metrics.get('total_shares', 0)}
                    - Total Views: {engagement_metrics.get('total_views', 0)}

                    Platform Breakdown:
                    {json.dumps(engagement_metrics.get('platforms', {}), default=str)}
                    """
                except Exception as e:
                    data_context = f"\nNote: Unable to fetch current project data: {str(e)}"

            messages = [
                {
                    "role": "system",
                    "content": f"""You are Track Futura AI Assistant, an expert in social media analytics and data analysis.
                    You help users analyze their social media performance, engagement metrics, and content strategy.

                    When responding about data analysis:
                    - Use the actual project data provided in the context when available
                    - Provide clear, actionable insights based on real data
                    - Use specific metrics and numbers from the actual data
                    - Suggest next steps for improvement based on current performance
                    - Focus on social media platforms: Instagram, Facebook, LinkedIn, TikTok
                    - Reference specific posts, comments, and metrics from the data when relevant

                    {data_context}

                    If you need to show charts or data visualizations, use this format:
                    ```chart
                    {{
                      "type": "line|bar|pie|radar",
                      "title": "Chart Title",
                      "data": {{
                        "labels": ["Label1", "Label2", "Label3"],
                        "datasets": [
                          {{
                            "label": "Dataset Name",
                            "data": [value1, value2, value3],
                            "backgroundColor": "color",
                            "borderColor": "color"
                          }}
                        ]
                      }}
                    }}
                    ```

                    Always prioritize insights from the actual project data when available. Keep responses concise but informative."""
                }
            ]

            # Add conversation history if provided
            if conversation_history:
                # Convert queryset to list and get last 5 messages
                history_list = list(conversation_history)
                recent_messages = history_list[-5:] if len(history_list) > 5 else history_list
                for msg in recent_messages:
                    role = "user" if msg.sender == "user" else "assistant"
                    messages.append({"role": role, "content": msg.content})

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1500,
                temperature=0.7,
                stream=False
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"OpenAI API Error: {str(e)}")
            return f"I apologize, but I'm experiencing technical difficulties. Please try again in a moment. Error: {str(e)}"

openai_service = OpenAIService()