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
    from common.sentiment_analysis_service import sentiment_service
except ImportError:
    # Fallback if import fails
    DataIntegrationService = None
    sentiment_service = None

class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY', '')
        try:
            self.client = openai.OpenAI(api_key=self.api_key) if self.api_key else None
        except Exception as e:
            print(f"Failed to initialize OpenAI client: {e}")
            self.client = None

    def generate_response(self, user_message, conversation_history=None, project_id=None):
        """Generate AI response using OpenAI GPT with real data and sentiment analysis"""
        if not self.client:
            return "I'm sorry, the AI service is currently unavailable. Please try again later."

        try:
            # Get real data from the project if available
            data_context = ""
            sentiment_context = ""
            
            if project_id and DataIntegrationService:
                try:
                    print(f"[OPENAI] Fetching data for project_id: {project_id}")
                    data_service = DataIntegrationService(project_id=project_id)

                    # Get recent posts separated by company vs competitor (use 30 days to ensure we get data)
                    company_posts = data_service.get_company_posts(limit=50, days_back=30)
                    competitor_posts = data_service.get_competitor_posts(limit=50, days_back=30)
                    all_posts = data_service.get_all_posts(limit=50, days_back=30)

                    print(f"[OPENAI] Found {len(company_posts)} company posts, {len(competitor_posts)} competitor posts")

                    recent_comments = data_service.get_all_comments(limit=50, days_back=30)

                    # Get engagement metrics for company and competitors separately
                    company_metrics = data_service.get_engagement_metrics(days_back=30, source_type='company')
                    competitor_metrics = data_service.get_engagement_metrics(days_back=30, source_type='competitor')
                    overall_metrics = data_service.get_engagement_metrics(days_back=30)

                    # Perform sentiment analysis on recent comments
                    if sentiment_service and recent_comments:
                        sentiment_analysis = sentiment_service.analyze_comment_sentiment(recent_comments)
                        
                        sentiment_context = f"""

                        SENTIMENT ANALYSIS INSIGHTS:
                        Overall Sentiment: {sentiment_analysis.get('overall_sentiment', 'neutral').title()}
                        Sentiment Breakdown: {json.dumps(sentiment_analysis.get('sentiment_breakdown', {}), default=str)}
                        Sentiment Percentages: {json.dumps(sentiment_analysis.get('sentiment_percentages', {}), default=str)}
                        Platform Breakdown: {json.dumps(sentiment_analysis.get('platform_breakdown', {}), default=str)}
                        
                        Key Insights:
                        {chr(10).join(sentiment_analysis.get('insights', []))}
                        
                        Total Comments Analyzed: {sentiment_analysis.get('total_analyzed', 0)}
                        High Confidence Results: {sentiment_analysis.get('high_confidence_count', 0)}
                        """

                        # Also analyze content sentiment
                        if all_posts:
                            content_sentiment = sentiment_service.analyze_content_sentiment(all_posts, include_comments=False)
                            sentiment_context += f"""
                            
                            CONTENT SENTIMENT ANALYSIS:
                            Post Sentiment Results: {json.dumps(content_sentiment.get('post_sentiment_results', []), default=str)}
                            Content Insights: {chr(10).join(content_sentiment.get('overall_insights', []))}
                            Recommendations: {chr(10).join(content_sentiment.get('recommendations', []))}
                            """

                    data_context = f"""

                    CURRENT PROJECT DATA CONTEXT (Last 30 Days):

                    === COMPANY DATA ===
                    Company Posts: {len(company_posts)} posts
                    {json.dumps(company_posts[:3], default=str) if company_posts else "No company posts found"}

                    Company Engagement Metrics:
                    - Total Posts: {company_metrics.get('total_posts', 0)}
                    - Total Likes: {company_metrics.get('total_likes', 0)}
                    - Total Comments: {company_metrics.get('total_comments', 0)}
                    - Total Shares: {company_metrics.get('total_shares', 0)}
                    - Total Views: {company_metrics.get('total_views', 0)}
                    - Avg Engagement Rate: {company_metrics.get('engagement_rate', 0):.2f}%
                    - Platform Breakdown: {json.dumps(company_metrics.get('platforms', {}), default=str)}

                    === COMPETITOR DATA ===
                    Competitor Posts: {len(competitor_posts)} posts
                    {json.dumps(competitor_posts[:3], default=str) if competitor_posts else "No competitor posts found"}

                    Competitor Engagement Metrics:
                    - Total Posts: {competitor_metrics.get('total_posts', 0)}
                    - Total Likes: {competitor_metrics.get('total_likes', 0)}
                    - Total Comments: {competitor_metrics.get('total_comments', 0)}
                    - Total Shares: {competitor_metrics.get('total_shares', 0)}
                    - Total Views: {competitor_metrics.get('total_views', 0)}
                    - Avg Engagement Rate: {competitor_metrics.get('engagement_rate', 0):.2f}%
                    - Platform Breakdown: {json.dumps(competitor_metrics.get('platforms', {}), default=str)}

                    === OVERALL COMPARISON ===
                    Total Posts: {overall_metrics.get('total_posts', 0)} (Company: {len(company_posts)}, Competitors: {len(competitor_posts)})
                    Overall Engagement Rate: {overall_metrics.get('engagement_rate', 0):.2f}%

                    Recent Comments/Content ({len(recent_comments)} items):
                    {json.dumps(recent_comments[:5], default=str) if recent_comments else "No recent content found"}

                    {sentiment_context}
                    """
                except Exception as e:
                    data_context = f"\nNote: Unable to fetch current project data: {str(e)}"
                    sentiment_context = f"\nNote: Unable to perform sentiment analysis: {str(e)}"

            messages = [
                {
                    "role": "system",
                    "content": f"""You are Track Futura AI Assistant, an expert in social media analytics, data analysis, and sentiment analysis.
                    You help users analyze their social media performance, engagement metrics, content strategy, and audience sentiment.

                    CORE CAPABILITIES:
                    1. Social Media Analytics: Analyze engagement, reach, and performance across platforms
                    2. Competitive Analysis: Compare company performance vs competitors
                    3. Sentiment Analysis: Interpret audience emotions and reactions from comments and content
                    4. Content Strategy: Provide recommendations based on data and sentiment insights
                    5. Trend Analysis: Identify patterns in engagement and sentiment over time
                    6. Platform Optimization: Platform-specific insights for Instagram, Facebook, LinkedIn, TikTok

                    DATA ORGANIZATION:
                    - Company Data: Posts and metrics from your company's social media accounts (marked as source_type: 'company')
                    - Competitor Data: Posts and metrics from competitor accounts (marked as source_type: 'competitor')
                    - Always differentiate between company and competitor performance when analyzing
                    - Use comparative analysis to provide actionable insights

                    SENTIMENT ANALYSIS EXPERTISE:
                    - Analyze comment sentiment to understand audience reception
                    - Identify emotional indicators and key phrases in audience feedback
                    - Provide context insights about what drives positive/negative sentiment
                    - Recommend response strategies for different sentiment types
                    - Track sentiment trends across platforms and time periods
                    - Connect sentiment patterns with content performance

                    When responding about data analysis:
                    - Use the actual project data and sentiment analysis provided in the context
                    - Provide clear, actionable insights based on real data and sentiment patterns
                    - Use specific metrics, sentiment scores, and numbers from the actual data
                    - Highlight sentiment trends and their implications for content strategy
                    - Suggest next steps for improvement based on current performance and audience sentiment
                    - Reference specific posts, comments, sentiment patterns, and metrics when relevant
                    - Connect sentiment insights with engagement metrics for comprehensive analysis

                    SENTIMENT INSIGHTS INTEGRATION:
                    - When discussing engagement, always consider sentiment quality alongside quantity
                    - Identify content that drives positive sentiment vs. high engagement
                    - Recommend content adjustments based on sentiment patterns
                    - Alert users to concerning negative sentiment trends
                    - Celebrate positive sentiment achievements and explain what's working

                    {data_context}

                    If you need to show charts or data visualizations, use this format:
                    ```chart
                    {{
                      "type": "line|bar|pie|radar|doughnut",
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

                    For sentiment visualizations, use colors:
                    - Positive sentiment: green (#4CAF50)
                    - Neutral sentiment: gray (#9E9E9E)  
                    - Negative sentiment: red (#F44336)

                    Always prioritize insights from the actual project data and sentiment analysis when available. 
                    Combine quantitative metrics with qualitative sentiment insights for comprehensive recommendations.
                    Keep responses concise but informative, focusing on actionable insights."""
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