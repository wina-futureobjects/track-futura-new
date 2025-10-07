"""
Sentiment Analysis Service using OpenAI
Analyzes comments and content sentiment for AI chatbot knowledge
"""

import openai
import os
import json
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SentimentAnalysisService:
    """
    Service to analyze sentiment of social media content using OpenAI
    Provides sentiment insights for AI chatbot
    """

    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY', '')
        try:
            self.client = openai.OpenAI(api_key=self.api_key) if self.api_key else None
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client for sentiment analysis: {e}")
            self.client = None

    def analyze_comment_sentiment(self, comments, batch_size=20):
        """
        Analyze sentiment of multiple comments using OpenAI
        Returns sentiment scores and insights
        """
        if not self.client or not comments:
            return {
                'overall_sentiment': 'neutral',
                'sentiment_breakdown': {'positive': 0, 'neutral': 0, 'negative': 0},
                'insights': [],
                'error': 'OpenAI service unavailable or no comments provided'
            }

        try:
            # Process comments in batches
            all_results = []
            
            for i in range(0, len(comments), batch_size):
                batch = comments[i:i + batch_size]
                batch_results = self._analyze_batch_sentiment(batch)
                all_results.extend(batch_results)

            # Aggregate results
            return self._aggregate_sentiment_results(all_results, comments)

        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {
                'overall_sentiment': 'neutral',
                'sentiment_breakdown': {'positive': 0, 'neutral': 0, 'negative': 0},
                'insights': [f"Error analyzing sentiment: {str(e)}"],
                'error': str(e)
            }

    def _analyze_batch_sentiment(self, comments_batch):
        """Analyze sentiment for a batch of comments"""
        
        # Prepare comments text for analysis
        comments_text = []
        for comment in comments_batch:
            comment_content = comment.get('comment', '')
            platform = comment.get('platform', 'unknown')
            user = comment.get('comment_user', 'anonymous')
            
            comments_text.append({
                'text': comment_content,
                'platform': platform,
                'user': user,
                'id': comment.get('comment_id', '')
            })

        # Create prompt for OpenAI
        prompt = self._create_sentiment_prompt(comments_text)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert sentiment analyst specializing in social media content.
                        Analyze the sentiment of comments and provide detailed insights.
                        
                        For each comment, determine:
                        1. Sentiment: positive, negative, or neutral
                        2. Confidence score (0-1)
                        3. Key emotional indicators
                        4. Context and implications
                        
                        Respond with valid JSON only."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.3
            )

            # Parse the response
            result_text = response.choices[0].message.content
            try:
                return json.loads(result_text)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return self._fallback_sentiment_analysis(comments_batch)

        except Exception as e:
            logger.error(f"OpenAI API error in sentiment analysis: {e}")
            return self._fallback_sentiment_analysis(comments_batch)

    def _create_sentiment_prompt(self, comments_data):
        """Create a prompt for sentiment analysis"""
        
        comments_json = json.dumps(comments_data, indent=2)
        
        return f"""
        Analyze the sentiment of these social media comments and return a JSON response:

        Comments to analyze:
        {comments_json}

        Please return a JSON array where each object corresponds to a comment and includes:
        {{
            "comment_id": "id of the comment",
            "sentiment": "positive|negative|neutral",
            "confidence": 0.95,
            "emotion_indicators": ["happy", "excited", "satisfied"],
            "key_phrases": ["love this", "amazing content"],
            "context_insights": "Brief analysis of what makes this sentiment",
            "platform": "platform name",
            "response_recommendation": "How to respond to this type of comment"
        }}

        Focus on:
        - Overall emotional tone
        - Customer satisfaction indicators
        - Brand perception signals
        - Engagement quality
        - Actionable insights for social media strategy

        Return only valid JSON array, no additional text.
        """

    def _fallback_sentiment_analysis(self, comments_batch):
        """Fallback sentiment analysis using simple keyword matching"""
        
        positive_keywords = [
            'love', 'amazing', 'great', 'awesome', 'fantastic', 'excellent',
            'wonderful', 'perfect', 'brilliant', 'outstanding', 'incredible',
            'beautiful', 'stunning', 'impressive', 'remarkable', 'superb'
        ]
        
        negative_keywords = [
            'hate', 'terrible', 'awful', 'horrible', 'disgusting', 'worst',
            'disappointing', 'frustrating', 'annoying', 'pathetic', 'useless',
            'garbage', 'trash', 'stupid', 'ridiculous', 'waste'
        ]

        results = []
        
        for comment in comments_batch:
            comment_text = comment.get('comment', '').lower()
            
            positive_count = sum(1 for word in positive_keywords if word in comment_text)
            negative_count = sum(1 for word in negative_keywords if word in comment_text)
            
            if positive_count > negative_count:
                sentiment = 'positive'
                confidence = min(0.7 + (positive_count * 0.1), 0.95)
            elif negative_count > positive_count:
                sentiment = 'negative'
                confidence = min(0.7 + (negative_count * 0.1), 0.95)
            else:
                sentiment = 'neutral'
                confidence = 0.6

            results.append({
                'comment_id': comment.get('comment_id', ''),
                'sentiment': sentiment,
                'confidence': confidence,
                'emotion_indicators': [],
                'key_phrases': [],
                'context_insights': f'Fallback analysis - {sentiment} sentiment detected',
                'platform': comment.get('platform', 'unknown'),
                'response_recommendation': f'Standard {sentiment} response approach'
            })

        return results

    def _aggregate_sentiment_results(self, sentiment_results, original_comments):
        """Aggregate individual sentiment results into overall insights"""
        
        if not sentiment_results:
            return {
                'overall_sentiment': 'neutral',
                'sentiment_breakdown': {'positive': 0, 'neutral': 0, 'negative': 0},
                'insights': ['No sentiment data available'],
                'detailed_results': []
            }

        # Count sentiments
        sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        high_confidence_sentiments = []
        platform_sentiments = {}
        insights = []

        for result in sentiment_results:
            if isinstance(result, list):
                # Handle batch results
                for item in result:
                    sentiment = item.get('sentiment', 'neutral')
                    confidence = item.get('confidence', 0)
                    platform = item.get('platform', 'unknown')
                    
                    sentiment_counts[sentiment] += 1
                    
                    if confidence > 0.8:
                        high_confidence_sentiments.append(item)
                    
                    if platform not in platform_sentiments:
                        platform_sentiments[platform] = {'positive': 0, 'neutral': 0, 'negative': 0}
                    platform_sentiments[platform][sentiment] += 1
            else:
                # Handle single results
                sentiment = result.get('sentiment', 'neutral')
                confidence = result.get('confidence', 0)
                platform = result.get('platform', 'unknown')
                
                sentiment_counts[sentiment] += 1
                
                if confidence > 0.8:
                    high_confidence_sentiments.append(result)
                
                if platform not in platform_sentiments:
                    platform_sentiments[platform] = {'positive': 0, 'neutral': 0, 'negative': 0}
                platform_sentiments[platform][sentiment] += 1

        # Determine overall sentiment
        total_comments = sum(sentiment_counts.values())
        if total_comments == 0:
            overall_sentiment = 'neutral'
        else:
            max_sentiment = max(sentiment_counts, key=sentiment_counts.get)
            overall_sentiment = max_sentiment

        # Calculate percentages
        sentiment_percentages = {}
        for sentiment, count in sentiment_counts.items():
            sentiment_percentages[sentiment] = (count / total_comments * 100) if total_comments > 0 else 0

        # Generate comprehensive insights
        # Overall sentiment analysis
        if sentiment_percentages['positive'] > 70:
            insights.append(f"🎉 Exceptional audience reception with {sentiment_percentages['positive']:.1f}% positive sentiment. Your content strongly resonates with your audience.")
            insights.append(f"💡 Strategy: Maintain current content approach and identify successful patterns for replication.")
        elif sentiment_percentages['positive'] > 50:
            insights.append(f"✅ Strong positive response ({sentiment_percentages['positive']:.1f}%). Audience shows favorable engagement with your content.")
            insights.append(f"📈 Opportunity: Analyze top-performing content to increase positive sentiment further.")
        elif sentiment_percentages['positive'] > 30:
            insights.append(f"👍 Moderate positive sentiment ({sentiment_percentages['positive']:.1f}%). Room for improvement in audience satisfaction.")
            insights.append(f"🎯 Action: Review neutral and negative feedback to identify content gaps.")
        else:
            insights.append(f"⚠️ Limited positive sentiment ({sentiment_percentages['positive']:.1f}%). Content strategy needs immediate attention.")
            insights.append(f"🔄 Recommendation: Conduct audience research to better understand preferences and pain points.")

        # Negative sentiment analysis
        if sentiment_percentages['negative'] > 30:
            insights.append(f"🚨 Critical: High negative sentiment ({sentiment_percentages['negative']:.1f}%) requires immediate action. Review recent content and address audience concerns.")
            insights.append(f"💬 Crisis response: Engage with negative comments, acknowledge issues, and provide solutions or explanations.")
        elif sentiment_percentages['negative'] > 20:
            insights.append(f"⚠️ Significant negative feedback ({sentiment_percentages['negative']:.1f}%). Identify recurring themes in negative comments for targeted improvements.")
        elif sentiment_percentages['negative'] > 10:
            insights.append(f"📊 Moderate negative sentiment ({sentiment_percentages['negative']:.1f}%) is within normal range. Monitor trends and respond to constructive criticism.")
        elif sentiment_percentages['negative'] > 5:
            insights.append(f"✓ Low negative sentiment ({sentiment_percentages['negative']:.1f}%) indicates healthy audience relationship. Continue current engagement practices.")
        else:
            insights.append(f"🌟 Minimal negative sentiment ({sentiment_percentages['negative']:.1f}%) - excellent community management!")

        # Neutral sentiment analysis
        if sentiment_percentages['neutral'] > 60:
            insights.append(f"📊 Large neutral audience ({sentiment_percentages['neutral']:.1f}%) represents significant untapped engagement potential.")
            insights.append(f"💡 Strategy: Create more emotionally compelling content, ask questions, and use calls-to-action to convert neutral sentiment to positive.")
            insights.append(f"🎯 Focus: Add storytelling, personal experiences, or controversial (but appropriate) topics to spark stronger reactions.")
        elif sentiment_percentages['neutral'] > 40:
            insights.append(f"📈 Substantial neutral sentiment ({sentiment_percentages['neutral']:.1f}%). These users are observing but not emotionally invested.")
            insights.append(f"🔍 Recommendation: Increase content variety, interactive elements (polls, questions), and direct audience engagement.")

        # Engagement quality analysis
        engagement_ratio = (sentiment_percentages['positive'] + sentiment_percentages['negative']) / 100
        if engagement_ratio < 0.4:
            insights.append(f"💭 Low emotional engagement ({engagement_ratio*100:.1f}% strong reactions). Content may be too informational or lacking personal connection.")
        elif engagement_ratio > 0.7:
            insights.append(f"🔥 High emotional engagement ({engagement_ratio*100:.1f}% strong reactions). Content successfully triggers audience emotions and drives conversation.")

        # Platform-specific deep analysis
        for platform, counts in platform_sentiments.items():
            platform_total = sum(counts.values())
            if platform_total > 5:  # Only analyze platforms with sufficient data
                platform_positive_pct = (counts['positive'] / platform_total * 100) if platform_total > 0 else 0
                platform_negative_pct = (counts['negative'] / platform_total * 100) if platform_total > 0 else 0
                platform_neutral_pct = (counts['neutral'] / platform_total * 100) if platform_total > 0 else 0

                insights.append(f"📱 {platform.title()}: {platform_positive_pct:.1f}% positive, {platform_neutral_pct:.1f}% neutral, {platform_negative_pct:.1f}% negative ({platform_total} comments)")

                # Platform-specific recommendations
                if platform_positive_pct > sentiment_percentages['positive']:
                    insights.append(f"   ✨ {platform.title()} outperforms overall average - replicate successful tactics on other platforms")
                elif platform_negative_pct > sentiment_percentages['negative'] + 10:
                    insights.append(f"   ⚠️ {platform.title()} shows elevated negative sentiment - review platform-specific content strategy")

                # Platform audience insights
                if platform_neutral_pct > 70:
                    insights.append(f"   💡 {platform.title()} audience is highly neutral - consider more engaging content formats (video, interactive posts)")

        # High confidence emotional insights
        if len(high_confidence_sentiments) > 3:
            strong_emotions = [item.get('emotion_indicators', []) for item in high_confidence_sentiments]
            flat_emotions = [emotion for sublist in strong_emotions for emotion in sublist if emotion]
            if flat_emotions:
                unique_emotions = list(set(flat_emotions[:8]))
                insights.append(f"💭 Dominant emotional themes: {', '.join(unique_emotions)}")
                insights.append(f"🎯 Content strategy: Lean into these emotions in future content to maximize engagement")

        # Volume insights
        if total_comments > 100:
            insights.append(f"📊 High engagement volume ({total_comments} comments analyzed) indicates strong community interest and active participation.")
        elif total_comments > 50:
            insights.append(f"📈 Moderate engagement volume ({total_comments} comments). Consider strategies to increase participation rates.")
        elif total_comments < 20:
            insights.append(f"📉 Low engagement volume ({total_comments} comments). Focus on growing audience reach and encouraging comments through questions and CTAs.")

        return {
            'overall_sentiment': overall_sentiment,
            'sentiment_breakdown': sentiment_counts,
            'sentiment_percentages': sentiment_percentages,
            'platform_breakdown': platform_sentiments,
            'insights': insights,
            'detailed_results': sentiment_results,
            'total_analyzed': total_comments,
            'high_confidence_count': len(high_confidence_sentiments)
        }

    def analyze_content_sentiment(self, posts, include_comments=True):
        """
        Analyze sentiment of posts and their comments
        """
        try:
            from .data_integration_service import DataIntegrationService
            
            if not posts:
                return {
                    'post_sentiment': 'neutral',
                    'comment_sentiment': 'neutral',
                    'overall_insights': ['No content to analyze'],
                    'recommendations': []
                }

            # Analyze post content sentiment
            post_contents = [post.get('content', '') for post in posts if post.get('content')]
            post_sentiment_results = []
            
            if post_contents:
                # Create simplified post analysis
                for i, content in enumerate(post_contents):
                    if content.strip():
                        post_sentiment_results.append({
                            'content': content[:200],  # First 200 chars
                            'sentiment': self._simple_sentiment_analysis(content),
                            'platform': posts[i].get('platform', 'unknown')
                        })

            # Analyze comments if requested
            comment_sentiment_results = {}
            if include_comments:
                data_service = DataIntegrationService()
                recent_comments = data_service.get_all_comments(limit=100, days_back=7)
                if recent_comments:
                    comment_sentiment_results = self.analyze_comment_sentiment(recent_comments)

            return {
                'post_sentiment_results': post_sentiment_results,
                'comment_sentiment_results': comment_sentiment_results,
                'overall_insights': self._generate_content_insights(post_sentiment_results, comment_sentiment_results),
                'recommendations': self._generate_recommendations(post_sentiment_results, comment_sentiment_results)
            }

        except Exception as e:
            logger.error(f"Error in content sentiment analysis: {e}")
            return {
                'post_sentiment': 'neutral',
                'comment_sentiment': 'neutral',
                'overall_insights': [f'Error analyzing content: {str(e)}'],
                'recommendations': ['Review content analysis setup']
            }

    def _simple_sentiment_analysis(self, text):
        """Simple sentiment analysis for fallback"""
        positive_words = ['good', 'great', 'amazing', 'love', 'excellent', 'awesome', 'happy', 'wonderful']
        negative_words = ['bad', 'terrible', 'hate', 'awful', 'horrible', 'disappointing', 'frustrated', 'angry']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'

    def _generate_content_insights(self, post_results, comment_results):
        """Generate insights from post and comment sentiment analysis"""
        insights = []
        
        if post_results:
            post_sentiments = [result.get('sentiment', 'neutral') for result in post_results]
            positive_posts = post_sentiments.count('positive')
            total_posts = len(post_sentiments)
            
            if total_posts > 0:
                positive_ratio = positive_posts / total_posts
                if positive_ratio > 0.7:
                    insights.append(f"📝 Strong positive content strategy: {positive_ratio:.1%} of posts have positive sentiment")
                elif positive_ratio < 0.3:
                    insights.append(f"📝 Content sentiment needs improvement: Only {positive_ratio:.1%} positive posts")

        if comment_results and isinstance(comment_results, dict):
            overall_comment_sentiment = comment_results.get('overall_sentiment', 'neutral')
            sentiment_breakdown = comment_results.get('sentiment_breakdown', {})
            
            if overall_comment_sentiment == 'positive':
                insights.append("💬 Audience response is overwhelmingly positive")
            elif overall_comment_sentiment == 'negative':
                insights.append("💬 Audience feedback indicates concerns that need addressing")
            
            insights.extend(comment_results.get('insights', []))

        if not insights:
            insights.append("📊 Limited sentiment data available for comprehensive analysis")

        return insights

    def _generate_recommendations(self, post_results, comment_results):
        """Generate actionable recommendations based on sentiment analysis"""
        recommendations = []

        if comment_results and isinstance(comment_results, dict):
            sentiment_percentages = comment_results.get('sentiment_percentages', {})
            positive_pct = sentiment_percentages.get('positive', 0)
            neutral_pct = sentiment_percentages.get('neutral', 0)
            negative_pct = sentiment_percentages.get('negative', 0)
            total_analyzed = comment_results.get('total_analyzed', 0)

            # Immediate priority recommendations
            if negative_pct > 30:
                recommendations.append("🚨 URGENT: Implement crisis communication protocol - address negative sentiment immediately")
                recommendations.append("🔍 Conduct sentiment root cause analysis - identify specific issues triggering negative responses")
                recommendations.append("💬 Set up community outreach program - personally respond to top negative comments within 24 hours")
                recommendations.append("📋 Create FAQ document addressing most common complaints mentioned in comments")

            # High negative feedback (20-30%)
            elif negative_pct > 20:
                recommendations.append("⚠️ Priority: Review and revise content strategy to reduce negative sentiment")
                recommendations.append("🎯 Analyze negative comment patterns - categorize by theme (product, service, communication, etc.)")
                recommendations.append("🔄 Develop response templates for common negative scenarios to ensure consistent, professional engagement")
                recommendations.append("📊 Set up weekly sentiment tracking to monitor improvement trends")

            # Moderate negative (10-20%)
            elif negative_pct > 10:
                recommendations.append("📊 Monitor negative sentiment trends - implement bi-weekly reviews to catch escalating issues")
                recommendations.append("💡 Create content addressing common concerns before they become complaints")
                recommendations.append("🤝 Engage proactively with neutral audience to prevent sentiment from turning negative")

            # Low negative (<10%) - maintain status
            else:
                recommendations.append("✅ Maintain current community management practices - negative sentiment is well-controlled")
                recommendations.append("🎯 Continue analyzing occasional negative feedback for continuous improvement insights")

            # Neutral audience engagement strategies
            if neutral_pct > 60:
                recommendations.append("📈 HIGH OPPORTUNITY: Convert neutral audience to positive with these tactics:")
                recommendations.append("   • Use storytelling and emotional narratives to create deeper connections")
                recommendations.append("   • Implement interactive content (polls, quizzes, Q&As) to drive active participation")
                recommendations.append("   • Share behind-the-scenes content and personal experiences to humanize your brand")
                recommendations.append("   • Create controversial (but brand-safe) content to spark stronger emotional responses")
                recommendations.append("   • Develop user-generated content campaigns to increase emotional investment")
            elif neutral_pct > 40:
                recommendations.append("🎯 Boost emotional engagement with neutral audience:")
                recommendations.append("   • Add clear calls-to-action asking for opinions and reactions")
                recommendations.append("   • Increase video content and visual storytelling (higher emotional impact)")
                recommendations.append("   • Host live sessions, AMAs, or real-time events to create urgency and FOMO")

            # Positive sentiment amplification
            if positive_pct > 60:
                recommendations.append("🌟 Leverage your positive momentum:")
                recommendations.append("   • Identify and document successful content patterns for replication")
                recommendations.append("   • Create case studies from positive feedback to attract new audience")
                recommendations.append("   • Develop brand ambassador program with most engaged positive commenters")
                recommendations.append("   • Request testimonials and user reviews from satisfied audience members")
            elif positive_pct > 40:
                recommendations.append("📈 Amplify positive sentiment:")
                recommendations.append("   • Analyze top 10 positive comments to identify what resonates most")
                recommendations.append("   • Create more content in the style/topic of highest positive-sentiment posts")
                recommendations.append("   • Encourage positive commenters to share their experiences (testimonials)")
            elif positive_pct < 30:
                recommendations.append("🔄 Rebuild positive sentiment:")
                recommendations.append("   • Conduct audience research to understand preferences and values")
                recommendations.append("   • Study competitors with higher positive sentiment for strategic insights")
                recommendations.append("   • Test new content formats, tones, and topics with A/B experiments")
                recommendations.append("   • Consider bringing in guest contributors or influencers to refresh perspective")

            # Volume-based recommendations
            if total_analyzed < 20:
                recommendations.append("📣 Increase engagement volume:")
                recommendations.append("   • End posts with specific questions that invite responses")
                recommendations.append("   • Run contests, giveaways, or challenges to boost participation")
                recommendations.append("   • Optimize posting times for maximum audience availability")
                recommendations.append("   • Cross-promote content across all social platforms to expand reach")
            elif total_analyzed > 100:
                recommendations.append("💪 You have strong engagement - optimize it:")
                recommendations.append("   • Segment your audience based on sentiment for targeted follow-up content")
                recommendations.append("   • Identify your most vocal advocates for partnership opportunities")
                recommendations.append("   • Use high engagement as social proof in marketing materials")

            # Platform-specific recommendations
            platform_breakdown = comment_results.get('platform_breakdown', {})
            if len(platform_breakdown) > 1:
                platform_performances = []
                for platform, counts in platform_breakdown.items():
                    platform_total = sum(counts.values())
                    if platform_total > 5:
                        platform_pos_pct = (counts['positive'] / platform_total * 100) if platform_total > 0 else 0
                        platform_performances.append((platform, platform_pos_pct, platform_total))

                if platform_performances:
                    # Sort by positive percentage
                    platform_performances.sort(key=lambda x: x[1], reverse=True)
                    best_platform = platform_performances[0]
                    worst_platform = platform_performances[-1]

                    if best_platform[1] - worst_platform[1] > 20:  # Significant difference
                        recommendations.append(f"🔄 Platform optimization: {best_platform[0].title()} outperforms {worst_platform[0].title()} by {best_platform[1] - worst_platform[1]:.1f}%")
                        recommendations.append(f"   • Replicate {best_platform[0].title()} content style and engagement tactics on {worst_platform[0].title()}")
                        recommendations.append(f"   • Analyze audience demographics - you may have different audiences on different platforms")
                        recommendations.append(f"   • Consider platform-specific content strategies rather than cross-posting")

        # Post-specific recommendations
        if post_results:
            negative_posts = [r for r in post_results if r.get('sentiment') == 'negative']
            positive_posts = [r for r in post_results if r.get('sentiment') == 'positive']

            if len(negative_posts) > len(post_results) * 0.3:
                recommendations.append("📝 Content audit: Your own posts show negative sentiment - revise messaging:")
                recommendations.append("   • Shift from problem-focused to solution-focused language")
                recommendations.append("   • Add more aspirational, inspirational, and empowering messaging")
                recommendations.append("   • Review tone - ensure it's appropriate for your brand personality")

            if len(positive_posts) > len(post_results) * 0.7:
                recommendations.append("✨ Your content has strong positive tone - maintain this approach")

        # Always include these foundational recommendations
        recommendations.append("📊 Establish sentiment tracking dashboard - monitor weekly trends and set improvement targets")
        recommendations.append("🎯 Create content calendar based on sentiment insights - plan topics that historically generate positive responses")
        recommendations.append("💬 Build engagement playbook - document what works and standardize successful practices across team")

        return recommendations

# Create a global instance
sentiment_service = SentimentAnalysisService()