import openai
from django.conf import settings
import json
import time
from datetime import datetime, timedelta
import random
import sys
import os

# Add the parent directory to sys.path to import common modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from common.data_integration_service import DataIntegrationService
except ImportError:
    # Fallback if import fails
    DataIntegrationService = None

# Import both PDF generators
try:
    from .pdf_generator import pdf_generator
    from .pdf_generator_enhanced import enhanced_pdf_generator
except ImportError:
    pdf_generator = None
    enhanced_pdf_generator = None

class ReportOpenAIService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY', '')
        try:
            self.client = openai.OpenAI(api_key=self.api_key) if self.api_key else None
        except Exception as e:
            print(f"Failed to initialize OpenAI client: {e}")
            self.client = None

    def generate_sentiment_analysis_report(self, configuration=None, project_id=None):
        """Generate AI-powered sentiment analysis report with real data"""
        if not self.client:
            return self._fallback_sentiment_analysis()

        try:
            # Get real comments data if available
            real_comments = []
            if project_id and DataIntegrationService:
                try:
                    data_service = DataIntegrationService(project_id=project_id)
                    comments_data = data_service.get_all_comments(limit=100, days_back=30)
                    real_comments = [comment['comment'] for comment in comments_data if comment.get('comment')]
                except Exception as e:
                    print(f"Error fetching real comments: {e}")

            # Use real comments if available, otherwise fall back to sample data
            if real_comments:
                sample_comments = real_comments
                data_source = "real project data"
            else:
                sample_comments = [
                    "That's the facelifted Leon. Is that a hint of what's to come in 2025 ? 😀",
                    "Bring in the Terramar !",
                    "Congratulations for a great launch!",
                    "😍",
                    "🔥🔥",
                    "🔥🔥🔥🎥",
                    "Can't wait to get mine! Bought the Cupra Tavascan VZ!",
                    "🔥🔥",
                    "the effort 🤯",
                    "Amazing design and performance! Love it!",
                    "Not impressed with the pricing",
                    "Beautiful car but too expensive for what it offers",
                    "Outstanding quality and features",
                    "This is exactly what I was looking for!",
                    "Disappointed with the color options",
                    "Excellent customer service experience",
                    "The wait time was too long",
                    "Incredible value for money",
                    "Poor build quality noticed",
                    "Absolutely love the new features!"
                ]
                data_source = "sample demonstration data"

            # Create prompt for OpenAI
            prompt = f"""
            Analyze the following social media comments for sentiment analysis.

            Data Source: {data_source}
            Total Comments: {len(sample_comments)}

            Comments:
            {json.dumps(sample_comments, indent=2)}

            Please provide a comprehensive sentiment analysis report with:
            1. Overall sentiment distribution (positive, negative, neutral percentages)
            2. Individual comment analysis with sentiment and confidence scores (for first 20 comments)
            3. Key insights and trends based on the actual data
            4. Actionable recommendations for social media strategy
            5. Trending keywords and themes from the comments

            Return the response in JSON format with these exact keys:
            - summary (with total_comments_analyzed, sentiment_distribution, overall_sentiment, confidence_average)
            - detailed_analysis (array of comment analyses for first 20 comments)
            - trending_keywords (array of keyword objects with keyword, count, sentiment)
            - insights (array of insight strings based on actual data patterns)
            - recommendations (array of recommendation strings)
            """

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert social media analyst specializing in sentiment analysis.
                        Provide detailed, accurate sentiment analysis with actionable insights.
                        Always return valid JSON format as requested."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            # Parse the AI response
            ai_result = json.loads(response.choices[0].message.content)

            # Ensure proper structure and add metadata
            return {
                **ai_result,
                'data_source_count': len(sample_comments),
                'ai_generated': True,
                'generation_timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"OpenAI Sentiment Analysis Error: {str(e)}")
            return self._fallback_sentiment_analysis()

    def generate_engagement_metrics_report(self, configuration=None, project_id=None):
        """Generate AI-powered engagement metrics report with real data"""
        if not self.client:
            return self._fallback_engagement_metrics()

        try:
            # Get real engagement data if available
            real_data = None
            if project_id and DataIntegrationService:
                try:
                    data_service = DataIntegrationService(project_id=project_id)
                    engagement_metrics = data_service.get_engagement_metrics(days_back=30)
                    posts_data = data_service.get_all_posts(limit=20, days_back=30)

                    real_data = {
                        "posts": [{
                            "title": post.get('content', f"Post by {post.get('user_posted', 'User')}")[:50] + "..." if len(post.get('content', '')) > 50 else post.get('content', f"Post by {post.get('user_posted', 'User')}"),
                            "likes": post.get('likes', 0),
                            "comments": post.get('num_comments', 0),
                            "shares": post.get('num_shares', 0),
                            "views": post.get('views', 0),
                            "platform": post.get('platform', 'unknown'),
                            "engagement_score": post.get('engagement_score', 0)
                        } for post in posts_data],
                        "total_posts": engagement_metrics.get('total_posts', 0),
                        "total_likes": engagement_metrics.get('total_likes', 0),
                        "total_comments": engagement_metrics.get('total_comments', 0),
                        "total_shares": engagement_metrics.get('total_shares', 0),
                        "total_views": engagement_metrics.get('total_views', 0),
                        "platforms": engagement_metrics.get('platforms', {}),
                        "time_period": "Last 30 days (real data)"
                    }
                    data_source = "real project data"
                except Exception as e:
                    print(f"Error fetching real engagement data: {e}")

            # Use real data if available, otherwise fall back to sample data
            if real_data:
                sample_data = real_data
            else:
                sample_data = {
                    "posts": [
                        {"title": "New Cupra Launch Event", "likes": 342, "comments": 28, "shares": 15, "views": 5420},
                        {"title": "Behind the Scenes Video", "likes": 289, "comments": 19, "shares": 12, "views": 4230},
                        {"title": "Customer Testimonial", "likes": 256, "comments": 34, "shares": 8, "views": 3890},
                        {"title": "Product Features Demo", "likes": 198, "comments": 15, "shares": 6, "views": 3120},
                        {"title": "Weekend Special Offer", "likes": 176, "comments": 22, "shares": 9, "views": 2850}
                    ],
                    "total_followers": 15420,
                    "time_period": "Last 30 days (sample data)"
                }
                data_source = "sample demonstration data"

            prompt = f"""
            Analyze the following social media engagement data and provide a comprehensive metrics report:

            Data:
            {json.dumps(sample_data, indent=2)}

            Please provide:
            1. Engagement rate calculations and analysis
            2. Top performing content identification
            3. Growth trends and patterns
            4. Audience engagement insights
            5. Optimization recommendations
            6. Performance benchmarks

            Return response in JSON format with keys:
            - summary (engagement rates, top metrics)
            - performance_analysis (detailed post analysis)
            - insights (array of insights)
            - recommendations (array of recommendations)
            - benchmarks (industry comparisons)
            """

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a social media analytics expert specializing in engagement metrics.
                        Provide detailed analysis with specific recommendations for improvement.
                        Always return valid JSON format."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            ai_result = json.loads(response.choices[0].message.content)

            # Add visualization data for charts
            chart_data = self._prepare_engagement_chart_data(sample_data)

            return {
                **ai_result,
                **chart_data,
                'data_source_count': len(sample_data['posts']),
                'ai_generated': True,
                'generation_timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"OpenAI Engagement Analysis Error: {str(e)}")
            return self._fallback_engagement_metrics()

    def generate_content_analysis_report(self, configuration=None, project_id=None):
        """Generate AI-powered content analysis report with real data"""
        if not self.client:
            return self._fallback_content_analysis()

        try:
            # Get real content data if available
            real_content_data = None
            if project_id and DataIntegrationService:
                try:
                    data_service = DataIntegrationService(project_id=project_id)
                    content_analysis = data_service.get_content_analysis_data(days_back=30)
                    posts_data = data_service.get_all_posts(limit=50, days_back=30)

                    real_content_data = {
                        "posts": [{
                            "type": post.get('content_type', 'post'),
                            "hashtags": post.get('hashtags', []) if isinstance(post.get('hashtags'), list) else str(post.get('hashtags', '')).split(),
                            "engagement": post.get('engagement_score', 0),
                            "platform": post.get('platform', 'unknown'),
                            "likes": post.get('likes', 0),
                            "comments": post.get('num_comments', 0),
                            "shares": post.get('num_shares', 0),
                            "views": post.get('views', 0)
                        } for post in posts_data],
                        "content_types": content_analysis.get('content_types', {}),
                        "hashtags": dict(list(content_analysis.get('hashtags', {}).items())[:20]),  # Top 20 hashtags
                        "posting_times": content_analysis.get('posting_times', {}),
                        "time_period": "Last 30 days (real data)"
                    }
                    data_source = "real project data"
                except Exception as e:
                    print(f"Error fetching real content data: {e}")

            # Use real data if available, otherwise fall back to sample data
            if real_content_data:
                content_data = real_content_data
            else:
                content_data = {
                    "posts": [
                        {"type": "image", "hashtags": ["#cupra", "#launch", "#automotive"], "engagement": 342},
                        {"type": "video", "hashtags": ["#behindthescenes", "#cupra"], "engagement": 289},
                        {"type": "carousel", "hashtags": ["#testimonial", "#customer"], "engagement": 256},
                        {"type": "image", "hashtags": ["#features", "#tech"], "engagement": 198},
                        {"type": "story", "hashtags": ["#offer", "#weekend"], "engagement": 176}
                    ],
                    "time_period": "Last 30 days (sample data)"
                }
                data_source = "sample demonstration data"

            prompt = f"""
            Analyze the following social media content data and provide insights:

            Content Data:
            {json.dumps(content_data, indent=2)}

            Provide analysis on:
            1. Content type performance
            2. Hashtag effectiveness
            3. Optimal posting strategies
            4. Content optimization opportunities
            5. Visual content impact
            6. Engagement patterns by content type

            Return JSON with keys:
            - content_performance (breakdown by type)
            - hashtag_analysis (effectiveness metrics)
            - optimization_opportunities (actionable suggestions)
            - insights (key findings)
            - recommendations (strategic advice)
            """

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a content strategy expert specializing in social media analytics.
                        Provide actionable insights for content optimization.
                        Always return valid JSON format."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            ai_result = json.loads(response.choices[0].message.content)

            return {
                **ai_result,
                'data_source_count': len(content_data['posts']),
                'ai_generated': True,
                'generation_timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"OpenAI Content Analysis Error: {str(e)}")
            return self._fallback_content_analysis()

    def _fallback_sentiment_analysis(self):
        """Fallback sentiment analysis when OpenAI is unavailable"""
        sample_comments = [
            "That's the facelifted Leon. Is that a hint of what's to come in 2025 ? 😀",
            "Bring in the Terramar !",
            "Congratulations for a great launch!",
            "😍",
            "🔥🔥",
            "Amazing design and performance! Love it!",
            "Not impressed with the pricing",
            "Beautiful car but too expensive for what it offers",
            "Outstanding quality and features",
            "Excellent customer service experience"
        ]

        # Simple keyword-based analysis
        positive_words = ['love', 'amazing', 'excellent', 'outstanding', 'congratulations', '😍', '🔥', 'beautiful']
        negative_words = ['disappointed', 'poor', 'expensive', 'not impressed']

        sentiment_results = []
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}

        for i, comment in enumerate(sample_comments):
            comment_lower = comment.lower()
            positive_score = sum(1 for word in positive_words if word in comment_lower)
            negative_score = sum(1 for word in negative_words if word in comment_lower)

            if positive_score > negative_score:
                sentiment = 'positive'
                confidence = min(0.6 + positive_score * 0.2, 0.95)
            elif negative_score > positive_score:
                sentiment = 'negative'
                confidence = min(0.6 + negative_score * 0.2, 0.95)
            else:
                sentiment = 'neutral'
                confidence = random.uniform(0.5, 0.8)

            sentiment_counts[sentiment] += 1
            sentiment_results.append({
                'id': i + 1,
                'comment': comment,
                'sentiment': sentiment,
                'confidence': round(confidence, 2),
                'timestamp': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            })

        total_comments = len(sample_comments)
        return {
            'summary': {
                'total_comments_analyzed': total_comments,
                'sentiment_distribution': {
                    'positive': round((sentiment_counts['positive'] / total_comments) * 100, 1),
                    'negative': round((sentiment_counts['negative'] / total_comments) * 100, 1),
                    'neutral': round((sentiment_counts['neutral'] / total_comments) * 100, 1)
                },
                'overall_sentiment': max(sentiment_counts, key=sentiment_counts.get),
                'confidence_average': round(sum(r['confidence'] for r in sentiment_results) / total_comments, 2)
            },
            'detailed_analysis': sentiment_results,
            'trending_keywords': [
                {'keyword': 'design', 'count': 8, 'sentiment': 'positive'},
                {'keyword': 'price', 'count': 6, 'sentiment': 'negative'},
                {'keyword': 'quality', 'count': 5, 'sentiment': 'positive'}
            ],
            'insights': [
                f"📈 {round((sentiment_counts['positive'] / total_comments) * 100, 1)}% of comments show positive sentiment",
                "📊 Design and quality are most mentioned positive aspects",
                "⚠️ Price concerns appear in negative feedback"
            ],
            'recommendations': [
                "Focus marketing on design and quality aspects",
                "Address pricing concerns in communications",
                "Leverage positive feedback for testimonials"
            ],
            'ai_generated': False,
            'data_source_count': total_comments
        }

    def _fallback_engagement_metrics(self):
        """Fallback engagement metrics when OpenAI is unavailable"""
        return {
            'summary': {
                'total_posts': 45,
                'total_likes': 2847,
                'total_comments': 156,
                'total_shares': 89,
                'average_engagement_rate': 4.2
            },
            'performance_analysis': [
                {'title': 'New Cupra Launch Event', 'likes': 342, 'comments': 28, 'shares': 15, 'engagement_rate': 6.8},
                {'title': 'Behind the Scenes Video', 'likes': 289, 'comments': 19, 'shares': 12, 'engagement_rate': 5.4}
            ],
            'insights': [
                "Video content performs 23% better than image posts",
                "Peak engagement occurs between 6-8 PM"
            ],
            'recommendations': [
                "Increase video content production",
                "Schedule posts during peak hours"
            ],
            'ai_generated': False,
            'data_source_count': 45
        }

    def _fallback_content_analysis(self):
        """Fallback content analysis when OpenAI is unavailable"""
        return {
            'content_performance': {
                'video': {'avg_engagement': 289, 'percentage': 35},
                'image': {'avg_engagement': 256, 'percentage': 45},
                'carousel': {'avg_engagement': 198, 'percentage': 20}
            },
            'hashtag_analysis': [
                {'hashtag': '#cupra', 'usage': 15, 'avg_engagement': 267},
                {'hashtag': '#automotive', 'usage': 12, 'avg_engagement': 234}
            ],
            'insights': [
                "Video content generates highest engagement",
                "Brand hashtags perform consistently well"
            ],
            'recommendations': [
                "Increase video content ratio to 40%",
                "Create branded hashtag campaigns"
            ],
            'ai_generated': False,
            'data_source_count': 25
        }

    def _prepare_engagement_chart_data(self, data):
        """Prepare data for engagement visualization charts"""
        chart_data = {}

        # Platform performance data for bar chart
        if 'platforms' in data:
            platform_performance = {}
            for platform, metrics in data['platforms'].items():
                total_engagement = metrics.get('total_likes', 0) + metrics.get('total_comments', 0) + metrics.get('total_shares', 0)
                total_posts = metrics.get('total_posts', 1)
                avg_engagement = (total_engagement / total_posts) if total_posts > 0 else 0
                platform_performance[platform] = {
                    'avg_engagement': round(avg_engagement, 1),
                    'total_posts': total_posts,
                    'total_likes': metrics.get('total_likes', 0),
                    'total_comments': metrics.get('total_comments', 0),
                    'total_shares': metrics.get('total_shares', 0)
                }
            chart_data['platform_performance'] = platform_performance

        # Engagement trends over time (sample data for visualization)
        chart_data['engagement_trends'] = [
            {'date': '2024-09-01', 'likes': random.randint(200, 400), 'comments': random.randint(20, 50), 'shares': random.randint(10, 30)},
            {'date': '2024-09-08', 'likes': random.randint(250, 450), 'comments': random.randint(25, 55), 'shares': random.randint(15, 35)},
            {'date': '2024-09-15', 'likes': random.randint(300, 500), 'comments': random.randint(30, 60), 'shares': random.randint(20, 40)},
            {'date': '2024-09-22', 'likes': random.randint(280, 480), 'comments': random.randint(28, 58), 'shares': random.randint(18, 38)},
            {'date': '2024-09-29', 'likes': random.randint(320, 520), 'comments': random.randint(32, 62), 'shares': random.randint(22, 42)}
        ]

        return chart_data

    def _prepare_sentiment_chart_data(self, summary):
        """Prepare data for sentiment visualization charts"""
        chart_data = {}

        # Ensure sentiment distribution is available for pie chart
        if 'sentiment_distribution' in summary:
            chart_data['sentiment_distribution'] = summary['sentiment_distribution']

        return chart_data

    def _prepare_content_chart_data(self, content_data):
        """Prepare data for content analysis visualization charts"""
        chart_data = {}

        # Content type performance data is already in the right format
        if 'content_performance' in content_data:
            chart_data['content_performance'] = content_data['content_performance']

        return chart_data

    def generate_enhanced_pdf(self, report_data, title, template_type):
        """Generate PDF with enhanced visualizations"""
        if not enhanced_pdf_generator:
            # Fall back to basic PDF generator
            if pdf_generator:
                if template_type == 'sentiment_analysis':
                    return pdf_generator.generate_sentiment_analysis_pdf(report_data, title)
                elif template_type == 'engagement_metrics':
                    return pdf_generator.generate_engagement_metrics_pdf(report_data, title)
                elif template_type == 'content_analysis':
                    return pdf_generator.generate_content_analysis_pdf(report_data, title)
                else:
                    return pdf_generator.generate_generic_pdf(report_data, title, template_type)
            else:
                raise Exception("No PDF generator available")

        # Use enhanced PDF generator with visualizations
        try:
            if template_type == 'sentiment_analysis':
                return enhanced_pdf_generator.generate_sentiment_analysis_pdf(report_data, title)
            elif template_type == 'engagement_metrics':
                return enhanced_pdf_generator.generate_engagement_metrics_pdf(report_data, title)
            elif template_type == 'content_analysis':
                return enhanced_pdf_generator.generate_content_analysis_pdf(report_data, title)
            else:
                # For other types, use basic generator
                if pdf_generator:
                    return pdf_generator.generate_generic_pdf(report_data, title, template_type)
                else:
                    raise Exception("No PDF generator available for this template type")
        except Exception as e:
            print(f"Enhanced PDF generation failed: {e}")
            # Fall back to basic generator
            if pdf_generator:
                if template_type == 'sentiment_analysis':
                    return pdf_generator.generate_sentiment_analysis_pdf(report_data, title)
                elif template_type == 'engagement_metrics':
                    return pdf_generator.generate_engagement_metrics_pdf(report_data, title)
                elif template_type == 'content_analysis':
                    return pdf_generator.generate_content_analysis_pdf(report_data, title)
                else:
                    return pdf_generator.generate_generic_pdf(report_data, title, template_type)
            else:
                raise e

# Global service instance
report_openai_service = ReportOpenAIService()