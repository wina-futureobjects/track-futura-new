from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import HttpResponse
from django.utils import timezone
import json
import random
import time
from datetime import datetime, timedelta
import csv
import logging
from django.core.serializers.json import DjangoJSONEncoder

logger = logging.getLogger(__name__)
from .models import ReportTemplate, GeneratedReport
from rest_framework import serializers
from .openai_service import report_openai_service
from .pdf_generator import pdf_generator
from rest_framework.permissions import IsAuthenticated

# Serializers
class ReportTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportTemplate
        fields = '__all__'

class GeneratedReportSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    template_type = serializers.CharField(source='template.template_type', read_only=True)
    
    class Meta:
        model = GeneratedReport
        fields = '__all__'

# ViewSets
class ReportTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for browsing available report templates
    """
    queryset = ReportTemplate.objects.filter(is_active=True)
    serializer_class = ReportTemplateSerializer
    
    def list(self, request):
        """
        List all available report templates in marketplace format
        """
        templates = self.get_queryset()
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)

class GeneratedReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing generated reports
    """
    queryset = GeneratedReport.objects.all()
    serializer_class = GeneratedReportSerializer
    
    def get_queryset(self):
        # Filter by user if authentication is implemented
        return GeneratedReport.objects.all().order_by('-created_at')
    
    @action(detail=False, methods=['POST'])
    def generate_report(self, request):
        """
        Generate a report based on selected template and configuration
        """
        try:
            template_id = request.data.get('template_id')
            title = request.data.get('title', '')
            configuration = request.data.get('configuration', {})
            
            if not template_id:
                return Response(
                    {'error': 'Template ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                template = ReportTemplate.objects.get(id=template_id)
            except ReportTemplate.DoesNotExist:
                return Response(
                    {'error': 'Template not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Create the report record
            report = GeneratedReport.objects.create(
                title=title or f"{template.name} Report",
                template=template,
                configuration=configuration,
                status='processing'
            )
            
            # Process the report based on template type using OpenAI
            try:
                # Try to get project_id from request
                project_id = None
                if hasattr(request, 'user') and request.user.is_authenticated:
                    project_id = request.query_params.get('project_id') or request.data.get('project_id')
                    if project_id:
                        try:
                            project_id = int(project_id)
                        except (ValueError, TypeError):
                            project_id = None

                # Import enhanced report service
                from reports.enhanced_report_service import enhanced_report_service

                # Use enhanced service for all report types
                if template.template_type == 'sentiment_analysis':
                    report.results = enhanced_report_service.generate_sentiment_analysis(report, project_id)
                elif template.template_type == 'competitive_analysis':
                    report.results = enhanced_report_service.generate_competitive_analysis(report, project_id)
                elif template.template_type == 'engagement_metrics':
                    report.results = enhanced_report_service.generate_engagement_metrics(report, project_id)
                elif template.template_type == 'content_analysis':
                    report.results = enhanced_report_service.generate_content_analysis(report, project_id)
                elif template.template_type == 'trend_analysis':
                    report.results = enhanced_report_service.generate_trend_analysis(report, project_id)
                elif template.template_type == 'user_behavior':
                    report.results = enhanced_report_service.generate_user_behavior(report, project_id)
                else:
                    # Default processing for other types
                    self._process_default_template(report)

                report.status = 'completed'
                report.completed_at = timezone.now()
                report.data_source_count = report.results.get('data_source_count', 0)
                
            except Exception as e:
                report.status = 'failed'
                report.error_message = str(e)
            
            report.save()

            # Convert results to JSON string to handle datetime serialization
            report.results = json.loads(json.dumps(report.results, cls=DjangoJSONEncoder))
            report.save()

            serializer = GeneratedReportSerializer(report)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Error generating report: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _process_sentiment_analysis(self, report):
        """
        Process sentiment analysis using sample comment data
        """
        start_time = time.time()
        
        # Sample comments data for demo (simulating database queries)
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
        
        # Simulate sentiment analysis processing
        time.sleep(1)  # Simulate processing time
        
        positive_words = ['love', 'amazing', 'excellent', 'outstanding', 'incredible', 'congratulations', '😍', '🔥', 'beautiful']
        negative_words = ['disappointed', 'poor', 'expensive', 'not impressed', 'too long']
        
        sentiment_results = []
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for i, comment in enumerate(sample_comments):
            comment_lower = comment.lower()
            
            # Simple sentiment analysis logic
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
        
        # Calculate metrics
        total_comments = len(sample_comments)
        sentiment_distribution = {
            'positive': round((sentiment_counts['positive'] / total_comments) * 100, 1),
            'negative': round((sentiment_counts['negative'] / total_comments) * 100, 1),
            'neutral': round((sentiment_counts['neutral'] / total_comments) * 100, 1)
        }
        
        # Trending keywords (mock data)
        trending_keywords = [
            {'keyword': 'design', 'count': 8, 'sentiment': 'positive'},
            {'keyword': 'price', 'count': 6, 'sentiment': 'negative'},
            {'keyword': 'quality', 'count': 5, 'sentiment': 'positive'},
            {'keyword': 'features', 'count': 4, 'sentiment': 'positive'},
            {'keyword': 'service', 'count': 3, 'sentiment': 'positive'},
        ]
        
        processing_time = time.time() - start_time
        
        # Store results
        report.results = {
            'summary': {
                'total_comments_analyzed': total_comments,
                'sentiment_distribution': sentiment_distribution,
                'overall_sentiment': max(sentiment_counts, key=sentiment_counts.get),
                'confidence_average': round(sum(r['confidence'] for r in sentiment_results) / total_comments, 2)
            },
            'detailed_analysis': sentiment_results,
            'trending_keywords': trending_keywords,
            'insights': [
                f"📈 {sentiment_distribution['positive']}% of comments show positive sentiment",
                f"📊 Most mentioned topic: design and quality",
                f"⚠️ Price concerns mentioned in {sentiment_distribution['negative']}% of negative comments",
                f"🎯 High engagement with emoji usage indicates strong emotional response"
            ],
            'recommendations': [
                "Focus marketing on design and quality aspects",
                "Address pricing concerns in future communications",
                "Leverage positive feedback for testimonials",
                "Monitor trending keywords for content strategy"
            ]
        }
        
        report.data_source_count = total_comments
        report.processing_time = processing_time
    
    def _process_engagement_metrics(self, report):
        """
        Process engagement metrics using sample data
        """
        start_time = time.time()
        time.sleep(0.8)  # Simulate processing
        
        # Sample engagement data
        engagement_data = {
            'total_posts': 45,
            'total_likes': 2847,
            'total_comments': 156,
            'total_shares': 89,
            'average_engagement_rate': 4.2,
            'top_performing_posts': [
                {'title': 'New Cupra Launch Event', 'likes': 342, 'comments': 28, 'shares': 15},
                {'title': 'Behind the Scenes Video', 'likes': 289, 'comments': 19, 'shares': 12},
                {'title': 'Customer Testimonial', 'likes': 256, 'comments': 34, 'shares': 8}
            ]
        }
        
        processing_time = time.time() - start_time
        
        report.results = engagement_data
        report.data_source_count = engagement_data['total_posts']
        report.processing_time = processing_time
    
    def _process_default_template(self, report):
        """
        Default processing for other template types
        """
        start_time = time.time()
        time.sleep(0.5)  # Simulate processing
        
        processing_time = time.time() - start_time
        
        report.results = {
            'message': f'Report generated successfully for {report.template.name}',
            'placeholder_data': True,
            'note': 'This is a placeholder result for demo purposes'
        }
        report.data_source_count = 100  # Mock data count
        report.processing_time = processing_time
    
    @action(detail=True, methods=['GET'])
    def download_csv(self, request, pk=None):
        """
        Download report results as CSV
        """
        try:
            report = self.get_object()
            
            if report.status != 'completed':
                return Response(
                    {'error': 'Report is not completed yet'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create CSV response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{report.title.replace(" ", "_")}_{report.id}.csv"'
            
            writer = csv.writer(response)
            
            if report.template.template_type == 'sentiment_analysis':
                # Write sentiment analysis CSV
                writer.writerow(['Comment ID', 'Comment Text', 'Sentiment', 'Confidence', 'Timestamp'])
                
                for item in report.results.get('detailed_analysis', []):
                    writer.writerow([
                        item['id'],
                        item['comment'],
                        item['sentiment'],
                        item['confidence'],
                        item['timestamp']
                    ])
            else:
                # Generic CSV export
                writer.writerow(['Key', 'Value'])
                for key, value in report.results.items():
                    writer.writerow([key, str(value)])
            
            return response

        except Exception as e:
            return Response(
                {'error': f'Error downloading CSV: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['GET'])
    def download_pdf(self, request, pk=None):
        """
        Download report results as PDF
        """
        try:
            report = self.get_object()

            if report.status != 'completed':
                return Response(
                    {'error': 'Report is not completed yet'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generate PDF with enhanced visualizations
            try:
                pdf_buffer = report_openai_service.generate_enhanced_pdf(
                    report.results, report.title, report.template.template_type
                )
            except Exception as e:
                # Fallback to basic PDF generator if enhanced fails
                print(f"Enhanced PDF generation failed, using fallback: {e}")
                if report.template.template_type == 'sentiment_analysis':
                    pdf_buffer = pdf_generator.generate_sentiment_analysis_pdf(
                        report.results, report.title
                    )
                elif report.template.template_type == 'engagement_metrics':
                    pdf_buffer = pdf_generator.generate_engagement_metrics_pdf(
                        report.results, report.title
                    )
                elif report.template.template_type == 'content_analysis':
                    pdf_buffer = pdf_generator.generate_content_analysis_pdf(
                        report.results, report.title
                    )
                else:
                    pdf_buffer = pdf_generator.generate_generic_pdf(
                        report.results, report.title, report.template.template_type
                    )

            # Create PDF response
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{report.title.replace(" ", "_")}_{report.id}.pdf"'

            return response

        except Exception as e:
            return Response(
                {'error': f'Error generating PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _process_engagement_metrics_with_real_data(self, report, project_id=None):
        """Process engagement metrics using real Instagram data"""
        start_time = time.time()

        try:
            from common.data_integration_service import DataIntegrationService

            data_service = DataIntegrationService(project_id=project_id)
            metrics = data_service.get_engagement_metrics(days_back=30)

            if not metrics:
                return self._get_fallback_engagement_data()

            processing_time = time.time() - start_time

            # Enhance with insights
            insights = []
            recommendations = []

            if metrics.get('engagement_rate', 0) > 5:
                insights.append(f"🎯 Excellent engagement rate of {metrics['engagement_rate']}% - above industry average")
                recommendations.append("Maintain current content strategy - it's working well")
            elif metrics.get('engagement_rate', 0) > 2:
                insights.append(f"📊 Good engagement rate of {metrics['engagement_rate']}%")
                recommendations.append("Consider A/B testing different content types to boost engagement")
            else:
                insights.append(f"⚠️ Low engagement rate of {metrics['engagement_rate']}% - needs improvement")
                recommendations.append("Focus on interactive content like polls, questions, and behind-the-scenes content")

            if metrics.get('total_views', 0) > 0:
                view_to_engagement = ((metrics['total_likes'] + metrics['total_comments']) / metrics['total_views']) * 100
                insights.append(f"👁️ View-to-engagement conversion: {view_to_engagement:.2f}%")

            top_posts = metrics.get('top_performing_posts', [])
            if top_posts:
                best_post = top_posts[0]
                insights.append(f"🏆 Top performing post has {best_post.get('likes', 0)} likes and {best_post.get('comments', 0)} comments")
                recommendations.append(f"Analyze what made the top post successful: @{best_post.get('user', 'unknown')} content style")

            # Get posts for visualization data
            posts = data_service.get_all_posts(limit=50, days_back=30)

            # Generate visualization data
            visualization_data = {
                'engagement_trend': self._generate_engagement_trend_data(posts),
                'platform_performance': self._generate_platform_performance_data(metrics),
                'content_performance_breakdown': self._generate_content_performance_breakdown(posts),
                'top_posts_chart': [
                    {
                        'title': post.get('content', '')[:50] + '...' if len(post.get('content', '')) > 50 else post.get('content', ''),
                        'likes': post.get('likes', 0),
                        'comments': post.get('comments', 0),
                        'engagement': post.get('likes', 0) + post.get('comments', 0),
                        'content_type': post.get('content_type', 'post')
                    } for post in top_posts[:5]
                ]
            }

            metrics.update({
                'insights': insights,
                'recommendations': recommendations,
                'processing_time': processing_time,
                'visualization_data': visualization_data,
                'report_generated_at': timezone.now().isoformat()
            })

            return metrics

        except Exception as e:
            logger.error(f"Error processing engagement metrics: {e}")
            return self._get_fallback_engagement_data()

    def _process_content_analysis_with_real_data(self, report, project_id=None):
        """Process content analysis using real Instagram data"""
        start_time = time.time()

        try:
            from common.real_data_service import RealDataService

            # Get data source selections from configuration
            config = report.configuration or {}
            batch_job_ids = config.get('batch_job_ids', [])
            folder_ids = config.get('folder_ids', [])

            data_service = RealDataService(
                project_id=project_id,
                batch_job_ids=batch_job_ids,
                folder_ids=folder_ids
            )
            analysis = data_service.get_real_content_analysis()

            if not analysis:
                return self._get_fallback_content_data()

            processing_time = time.time() - start_time

            # Generate insights
            insights = []
            recommendations = []

            content_types = analysis.get('content_type_breakdown', {})
            if content_types:
                # Find best performing content type
                best_type = max(content_types.items(), key=lambda x: x[1].get('total_likes', 0))
                insights.append(f"🎬 {best_type[0].title()} content performs best with {best_type[1]['total_likes']} total likes")
                recommendations.append(f"Increase {best_type[0]} content production by 30%")

            top_hashtags = analysis.get('top_hashtags', [])
            if top_hashtags:
                best_hashtag = top_hashtags[0]
                insights.append(f"#️⃣ #{best_hashtag['hashtag']} is your top hashtag with {best_hashtag['avg_likes']} avg likes")
                recommendations.append(f"Use #{best_hashtag['hashtag']} more frequently in future posts")

            total_hashtags = analysis.get('total_unique_hashtags', 0)
            if total_hashtags > 50:
                insights.append(f"📈 Using {total_hashtags} unique hashtags shows good diversity")
            elif total_hashtags < 10:
                recommendations.append("Expand hashtag variety to reach wider audiences")

            top_users = analysis.get('top_performing_users', [])
            if top_users:
                top_user = top_users[0]
                insights.append(f"👑 Top creator @{top_user['user']} has {top_user['total_likes']} total likes across {top_user['posts']} posts")
                recommendations.append(f"Analyze @{top_user['user']}'s content strategy for insights")

            analysis.update({
                'insights': insights,
                'recommendations': recommendations,
                'processing_time': processing_time,
                'report_generated_at': timezone.now().isoformat()
            })

            return analysis

        except Exception as e:
            logger.error(f"Error processing content analysis: {e}")
            return self._get_fallback_content_data()

    def _process_trend_analysis_with_real_data(self, report, project_id=None):
        """Process trend analysis using real Instagram data"""
        start_time = time.time()

        try:
            from common.real_data_service import RealDataService

            # Get data source selections from configuration
            config = report.configuration or {}
            batch_job_ids = config.get('batch_job_ids', [])
            folder_ids = config.get('folder_ids', [])

            data_service = RealDataService(
                project_id=project_id,
                batch_job_ids=batch_job_ids,
                folder_ids=folder_ids
            )
            posts = data_service.get_scraped_posts(limit=1000)

            if not posts:
                return self._get_fallback_trend_data()

            # Analyze hashtag trends
            hashtag_trends = {}
            daily_stats = {}

            for post in posts:
                # Parse date_posted if it's a string
                if isinstance(post['date_posted'], str):
                    from dateutil import parser
                    date_obj = parser.parse(post['date_posted'])
                else:
                    date_obj = post['date_posted']
                date_key = date_obj.strftime('%Y-%m-%d')
                if date_key not in daily_stats:
                    daily_stats[date_key] = {'posts': 0, 'engagement': 0}

                daily_stats[date_key]['posts'] += 1
                daily_stats[date_key]['engagement'] += post.get('likes', 0) + post.get('comments', 0)

                for hashtag in post.get('hashtags', []):
                    if hashtag not in hashtag_trends:
                        hashtag_trends[hashtag] = {'usage_count': 0, 'total_engagement': 0, 'avg_engagement': 0}

                    hashtag_trends[hashtag]['usage_count'] += 1
                    hashtag_trends[hashtag]['total_engagement'] += post.get('likes', 0) + post.get('comments', 0)

            # Calculate averages and trends
            for hashtag in hashtag_trends:
                hashtag_trends[hashtag]['avg_engagement'] = round(
                    hashtag_trends[hashtag]['total_engagement'] / hashtag_trends[hashtag]['usage_count'], 2
                )

            # Get trending hashtags
            trending_hashtags = sorted(
                hashtag_trends.items(),
                key=lambda x: x[1]['avg_engagement'],
                reverse=True
            )[:10]

            # Calculate growth metrics
            sorted_dates = sorted(daily_stats.keys())
            growth_metrics = {}

            if len(sorted_dates) >= 7:
                first_week = sorted_dates[:7]
                last_week = sorted_dates[-7:]

                first_week_engagement = sum(daily_stats[date]['engagement'] for date in first_week) / 7
                last_week_engagement = sum(daily_stats[date]['engagement'] for date in last_week) / 7

                growth_rate = ((last_week_engagement - first_week_engagement) / first_week_engagement * 100) if first_week_engagement > 0 else 0

                growth_metrics = {
                    'engagement_growth_rate': round(growth_rate, 2),
                    'first_week_avg': round(first_week_engagement, 2),
                    'last_week_avg': round(last_week_engagement, 2)
                }

            processing_time = time.time() - start_time

            # Generate insights
            insights = []
            recommendations = []

            if growth_metrics.get('engagement_growth_rate', 0) > 10:
                insights.append(f"📈 Strong engagement growth of {growth_metrics['engagement_growth_rate']}% over the past week")
                recommendations.append("Continue current strategy - momentum is building")
            elif growth_metrics.get('engagement_growth_rate', 0) < -10:
                insights.append(f"📉 Engagement declined by {abs(growth_metrics['engagement_growth_rate'])}% - needs attention")
                recommendations.append("Review recent content changes and revert to proven strategies")

            if trending_hashtags:
                top_trend = trending_hashtags[0]
                insights.append(f"🔥 #{top_trend[0]} is trending with {top_trend[1]['avg_engagement']} avg engagement")
                recommendations.append(f"Leverage #{top_trend[0]} in upcoming content")

            result = {
                'trending_hashtags': [{'hashtag': k, **v} for k, v in trending_hashtags],
                'daily_engagement_stats': daily_stats,
                'growth_metrics': growth_metrics,
                'total_hashtags_analyzed': len(hashtag_trends),
                'insights': insights,
                'recommendations': recommendations,
                'processing_time': processing_time,
                'data_source_count': len(posts),
                'report_generated_at': timezone.now().isoformat()
            }

            return result

        except Exception as e:
            logger.error(f"Error processing trend analysis: {e}")
            return self._get_fallback_trend_data()

    def _process_user_behavior_with_real_data(self, report, project_id=None):
        """Process user behavior analysis using real Instagram data"""
        start_time = time.time()

        try:
            from common.real_data_service import RealDataService

            # Get data source selections from configuration
            config = report.configuration or {}
            batch_job_ids = config.get('batch_job_ids', [])
            folder_ids = config.get('folder_ids', [])

            data_service = RealDataService(
                project_id=project_id,
                batch_job_ids=batch_job_ids,
                folder_ids=folder_ids
            )
            posts = data_service.get_scraped_posts(limit=1000)

            if not posts:
                return self._get_fallback_user_behavior_data()

            # Analyze user patterns
            user_stats = {}
            hourly_activity = {}
            daily_activity = {}

            for post in posts:
                user = post.get('user', 'unknown')
                if user not in user_stats:
                    user_stats[user] = {
                        'posts': 0, 'total_likes': 0, 'total_comments': 0,
                        'avg_likes': 0, 'engagement_rate': 0, 'followers': 0,
                        'is_verified': False
                    }

                user_stats[user]['posts'] += 1
                user_stats[user]['total_likes'] += post.get('likes', 0)
                user_stats[user]['total_comments'] += post.get('comments', 0)
                user_stats[user]['followers'] = max(user_stats[user]['followers'], post.get('followers', 0))
                user_stats[user]['is_verified'] = post.get('is_verified', False)

                # Activity timing analysis
                post_time = post['date_posted']
                hour = post_time.hour
                day = post_time.strftime('%A')

                if hour not in hourly_activity:
                    hourly_activity[hour] = {'posts': 0, 'engagement': 0}
                if day not in daily_activity:
                    daily_activity[day] = {'posts': 0, 'engagement': 0}

                engagement = post.get('likes', 0) + post.get('comments', 0)
                hourly_activity[hour]['posts'] += 1
                hourly_activity[hour]['engagement'] += engagement
                daily_activity[day]['posts'] += 1
                daily_activity[day]['engagement'] += engagement

            # Calculate user averages
            for user in user_stats:
                if user_stats[user]['posts'] > 0:
                    user_stats[user]['avg_likes'] = round(user_stats[user]['total_likes'] / user_stats[user]['posts'], 2)
                    total_engagement = user_stats[user]['total_likes'] + user_stats[user]['total_comments']
                    user_stats[user]['engagement_rate'] = round(total_engagement / user_stats[user]['posts'], 2)

            # Find peak activity times
            peak_hour = max(hourly_activity.items(), key=lambda x: x[1]['engagement'])[0] if hourly_activity else 12
            peak_day = max(daily_activity.items(), key=lambda x: x[1]['engagement'])[0] if daily_activity else 'Monday'

            # Top performers
            top_users = sorted(user_stats.items(), key=lambda x: x[1]['total_likes'], reverse=True)[:10]

            processing_time = time.time() - start_time

            # Generate insights
            insights = []
            recommendations = []

            verified_users = sum(1 for user, stats in user_stats.items() if stats['is_verified'])
            total_users = len(user_stats)

            if verified_users > 0:
                insights.append(f"✅ {verified_users} verified users out of {total_users} total users")
                recommendations.append("Engage more with verified accounts for increased visibility")

            insights.append(f"⏰ Peak engagement hour: {peak_hour}:00")
            insights.append(f"📅 Peak engagement day: {peak_day}")
            recommendations.append(f"Schedule important posts around {peak_hour}:00 on {peak_day}s")

            if top_users:
                top_performer = top_users[0]
                insights.append(f"🏆 Top performer @{top_performer[0]} averages {top_performer[1]['avg_likes']} likes per post")
                recommendations.append(f"Study @{top_performer[0]}'s posting patterns and content style")

            result = {
                'user_performance_stats': [{'user': k, **v} for k, v in top_users],
                'peak_activity_times': {
                    'hour': peak_hour,
                    'day': peak_day,
                    'hourly_breakdown': hourly_activity,
                    'daily_breakdown': daily_activity
                },
                'user_demographics': {
                    'total_users': total_users,
                    'verified_users': verified_users,
                    'verification_rate': round((verified_users / total_users * 100), 2) if total_users > 0 else 0
                },
                'insights': insights,
                'recommendations': recommendations,
                'processing_time': processing_time,
                'data_source_count': len(posts),
                'report_generated_at': timezone.now().isoformat()
            }

            return result

        except Exception as e:
            logger.error(f"Error processing user behavior analysis: {e}")
            return self._get_fallback_user_behavior_data()

    def _get_fallback_engagement_data(self):
        """Fallback engagement data when real data is unavailable"""
        return {
            'total_posts': 45,
            'total_likes': 2847,
            'total_comments': 156,
            'total_views': 45000,
            'avg_likes_per_post': 63.27,
            'avg_comments_per_post': 3.47,
            'avg_views_per_post': 1000.0,
            'engagement_rate': 6.67,
            'platform_breakdown': {'instagram': {'posts': 45, 'likes': 2847, 'comments': 156, 'views': 45000}},
            'insights': ['Using sample data - connect real data for accurate insights'],
            'recommendations': ['Set up data integration to get real-time insights'],
            'data_source_count': 45
        }

    def _get_fallback_content_data(self):
        """Fallback content data when real data is unavailable"""
        return {
            'content_type_breakdown': {
                'Video': {'count': 15, 'total_likes': 1200, 'total_comments': 80},
                'Image': {'count': 25, 'total_likes': 1400, 'total_comments': 60},
                'Sidecar': {'count': 5, 'total_likes': 247, 'total_comments': 16}
            },
            'top_hashtags': [
                {'hashtag': 'nike', 'posts': 10, 'total_likes': 500, 'avg_likes': 50.0},
                {'hashtag': 'sport', 'posts': 8, 'total_likes': 320, 'avg_likes': 40.0}
            ],
            'insights': ['Using sample data - connect real data for accurate insights'],
            'recommendations': ['Set up data integration to get real-time insights'],
            'data_source_count': 45
        }

    def _get_fallback_trend_data(self):
        """Fallback trend data when real data is unavailable"""
        return {
            'trending_hashtags': [
                {'hashtag': 'trending', 'usage_count': 5, 'avg_engagement': 75.0},
                {'hashtag': 'viral', 'usage_count': 3, 'avg_engagement': 60.0}
            ],
            'growth_metrics': {'engagement_growth_rate': 5.2},
            'insights': ['Using sample data - connect real data for accurate insights'],
            'recommendations': ['Set up data integration to get real-time insights'],
            'data_source_count': 45
        }

    def _get_fallback_user_behavior_data(self):
        """Fallback user behavior data when real data is unavailable"""
        return {
            'user_performance_stats': [
                {'user': 'sample_user', 'posts': 10, 'avg_likes': 50.0, 'total_likes': 500}
            ],
            'peak_activity_times': {'hour': 18, 'day': 'Monday'},
            'user_demographics': {'total_users': 25, 'verified_users': 3},
            'insights': ['Using sample data - connect real data for accurate insights'],
            'recommendations': ['Set up data integration to get real-time insights'],
            'data_source_count': 45
        }

    def _process_competitive_analysis_with_real_data(self, report, project_id=None):
        """Process competitive analysis using real Instagram data with OpenAI enhancement"""
        start_time = time.time()

        try:
            from common.real_data_service import RealDataService

            # Get data source selections from configuration
            config = report.configuration or {}
            batch_job_ids = config.get('batch_job_ids', [])
            folder_ids = config.get('folder_ids', [])

            data_service = RealDataService(
                project_id=project_id,
                batch_job_ids=batch_job_ids,
                folder_ids=folder_ids
            )

            # Get comprehensive data for competitive analysis
            posts = data_service.get_scraped_posts(limit=100)
            engagement_metrics = data_service.get_real_engagement_metrics()
            content_analysis = data_service.get_real_content_analysis()

            # Prepare data for OpenAI analysis
            analysis_data = {
                'posts_sample': posts[:10],  # Send sample for analysis
                'engagement_metrics': engagement_metrics,
                'content_analysis': content_analysis,
                'total_posts': len(posts),
                'date_range': '30 days'
            }

            # Use OpenAI for competitive analysis
            try:
                openai_analysis = report_openai_service.generate_competitive_analysis(analysis_data)
            except Exception as e:
                logger.warning(f"OpenAI analysis failed, using fallback: {e}")
                openai_analysis = {}

            processing_time = time.time() - start_time

            # Build comprehensive competitive analysis results
            results = {
                'brand_performance': {
                    'overall_engagement_rate': engagement_metrics.get('engagement_rate', 0),
                    'total_reach': engagement_metrics.get('total_views', 0),
                    'content_volume': engagement_metrics.get('total_posts', 0),
                    'avg_likes_per_post': engagement_metrics.get('avg_likes_per_post', 0),
                    'follower_growth_indicator': 'positive' if engagement_metrics.get('engagement_rate', 0) > 5 else 'neutral'
                },
                'content_strategy_analysis': {
                    'top_performing_content_types': content_analysis.get('content_type_breakdown', {}),
                    'hashtag_effectiveness': content_analysis.get('top_hashtags', [])[:5],
                    'posting_frequency': f"{engagement_metrics.get('total_posts', 0)} posts in 30 days"
                },
                'market_positioning': {
                    'engagement_benchmarks': {
                        'above_average': engagement_metrics.get('engagement_rate', 0) > 3,
                        'industry_comparison': 'Above average' if engagement_metrics.get('engagement_rate', 0) > 3 else 'Below average',
                        'content_quality_score': min(engagement_metrics.get('engagement_rate', 0) * 10, 100)
                    }
                },
                'competitive_advantages': self._extract_competitive_advantages(engagement_metrics, content_analysis),
                'areas_for_improvement': self._identify_improvement_areas(engagement_metrics, content_analysis),
                'visualization_data': {
                    'engagement_trend': self._generate_engagement_trend_data(posts),
                    'content_performance_chart': self._generate_content_performance_chart(content_analysis),
                    'competitor_comparison': self._generate_competitor_comparison_data(engagement_metrics)
                },
                'ai_insights': openai_analysis.get('insights', []),
                'strategic_recommendations': openai_analysis.get('recommendations', []),
                'market_opportunities': openai_analysis.get('opportunities', []),
                'processing_time': processing_time,
                'data_source_count': len(posts),
                'report_generated_at': timezone.now().isoformat()
            }

            return results

        except Exception as e:
            logger.error(f"Error in competitive analysis: {e}")
            return self._get_fallback_competitive_analysis_data()

    def _extract_competitive_advantages(self, engagement_metrics, content_analysis):
        """Extract competitive advantages from the data"""
        advantages = []

        if engagement_metrics.get('engagement_rate', 0) > 5:
            advantages.append("High engagement rate indicates strong audience connection")

        if engagement_metrics.get('total_views', 0) > 1000000:
            advantages.append("Strong reach and visibility in the market")

        top_hashtags = content_analysis.get('top_hashtags', [])
        if top_hashtags:
            advantages.append(f"Effective hashtag strategy with #{top_hashtags[0].get('hashtag', 'N/A')} performing well")

        return advantages or ["Building foundational metrics for competitive analysis"]

    def _identify_improvement_areas(self, engagement_metrics, content_analysis):
        """Identify areas for improvement"""
        improvements = []

        if engagement_metrics.get('engagement_rate', 0) < 3:
            improvements.append("Improve engagement rate through more interactive content")

        hashtag_count = content_analysis.get('total_unique_hashtags', 0)
        if hashtag_count < 5:
            improvements.append("Diversify hashtag strategy to reach broader audiences")

        content_types = content_analysis.get('content_type_breakdown', {})
        if len(content_types) < 2:
            improvements.append("Expand content type variety to maintain audience interest")

        return improvements or ["Continue current strategy and monitor performance"]

    def _generate_engagement_trend_data(self, posts):
        """Generate data for engagement trend visualization"""
        trend_data = []
        for i, post in enumerate(posts[:10]):
            trend_data.append({
                'day': i + 1,
                'engagement': post.get('likes', 0) + post.get('comments', 0),
                'likes': post.get('likes', 0),
                'comments': post.get('comments', 0)
            })
        return trend_data

    def _generate_content_performance_chart(self, content_analysis):
        """Generate data for content performance chart"""
        content_types = content_analysis.get('content_type_breakdown', {})
        chart_data = []

        for content_type, stats in content_types.items():
            chart_data.append({
                'type': content_type,
                'posts': stats.get('count', 0),
                'total_likes': stats.get('total_likes', 0),
                'avg_engagement': stats.get('total_likes', 0) / max(stats.get('count', 1), 1)
            })

        return chart_data

    def _generate_competitor_comparison_data(self, engagement_metrics):
        """Generate competitor comparison visualization data"""
        our_performance = engagement_metrics.get('engagement_rate', 0)

        return {
            'our_brand': {
                'engagement_rate': our_performance,
                'content_volume': engagement_metrics.get('total_posts', 0),
                'reach': engagement_metrics.get('total_views', 0)
            },
            'industry_average': {
                'engagement_rate': 3.5,  # Industry benchmark
                'content_volume': 20,
                'reach': 500000
            },
            'performance_score': min((our_performance / 3.5) * 100, 150) if our_performance > 0 else 50
        }

    def _get_fallback_competitive_analysis_data(self):
        """Fallback competitive analysis data when real data is unavailable"""
        return {
            'brand_performance': {
                'overall_engagement_rate': 4.2,
                'total_reach': 125000,
                'content_volume': 15,
                'avg_likes_per_post': 500,
                'follower_growth_indicator': 'positive'
            },
            'content_strategy_analysis': {
                'top_performing_content_types': {'Video': {'count': 8}, 'Image': {'count': 7}},
                'hashtag_effectiveness': [{'hashtag': 'sample', 'avg_likes': 100}],
                'posting_frequency': '15 posts in 30 days'
            },
            'competitive_advantages': ['Sample competitive advantage'],
            'areas_for_improvement': ['Sample improvement area'],
            'ai_insights': ['Connect real data for AI-powered insights'],
            'strategic_recommendations': ['Set up data integration for detailed analysis'],
            'data_source_count': 0
        }

    def _generate_platform_performance_data(self, metrics):
        """Generate platform performance visualization data"""
        platform_breakdown = metrics.get('platform_breakdown', {})
        performance_data = []

        for platform, stats in platform_breakdown.items():
            performance_data.append({
                'platform': platform.title(),
                'posts': stats.get('posts', 0),
                'likes': stats.get('likes', 0),
                'comments': stats.get('comments', 0),
                'views': stats.get('views', 0),
                'engagement_rate': ((stats.get('likes', 0) + stats.get('comments', 0)) / max(stats.get('views', 1), 1)) * 100
            })

        return performance_data

    def _generate_content_performance_breakdown(self, posts):
        """Generate content performance breakdown for charts"""
        content_performance = {}

        for post in posts:
            content_type = post.get('content_type', 'post')
            if content_type not in content_performance:
                content_performance[content_type] = {
                    'type': content_type,
                    'count': 0,
                    'total_likes': 0,
                    'total_comments': 0,
                    'avg_engagement': 0
                }

            content_performance[content_type]['count'] += 1
            content_performance[content_type]['total_likes'] += post.get('likes', 0)
            content_performance[content_type]['total_comments'] += post.get('comments', 0)

        # Calculate averages
        for content_type in content_performance.values():
            if content_type['count'] > 0:
                content_type['avg_engagement'] = (content_type['total_likes'] + content_type['total_comments']) / content_type['count']

        return list(content_performance.values())

    def _process_engagement_metrics_ONLY_REAL_DATA(self, report, project_id=None):
        """Process engagement metrics using ONLY real Apify scraped data - NO FALLBACKS"""
        start_time = time.time()

        try:
            from common.real_data_service import RealDataService

            # Get data source selections from configuration
            config = report.configuration or {}
            batch_job_ids = config.get('batch_job_ids', [])
            folder_ids = config.get('folder_ids', [])

            # Create service instance with selected data sources
            data_service = RealDataService(
                project_id=project_id,
                batch_job_ids=batch_job_ids,
                folder_ids=folder_ids
            )

            # Get ONLY real scraped data - NO FALLBACKS EVER
            metrics = data_service.get_real_engagement_metrics()
            visualization_data = data_service.get_real_visualization_data()

            if not metrics or metrics.get('total_posts', 0) == 0:
                # If no real data available, return clear error message
                return {
                    'error': 'NO REAL SCRAPED DATA AVAILABLE - Please run Apify scraper first',
                    'total_posts': 0,
                    'total_likes': 0,
                    'total_comments': 0,
                    'total_views': 0,
                    'data_source_count': 0,
                    'message': 'This report requires actual scraped data from Apify'
                }

            processing_time = time.time() - start_time

            # Generate insights based on REAL data only
            insights = []
            recommendations = []

            engagement_rate = metrics.get('engagement_rate', 0)
            total_likes = metrics.get('total_likes', 0)
            total_comments = metrics.get('total_comments', 0)
            total_views = metrics.get('total_views', 0)

            # Real insights based on actual scraped numbers
            if engagement_rate > 5:
                insights.append(f"🎯 Excellent engagement rate of {engagement_rate}% - above industry average")
                insights.append(f"💪 Strong performance with {total_likes:,} total likes and {total_comments:,} comments")
                recommendations.append("Maintain current content strategy - it's working exceptionally well")
            elif engagement_rate > 2:
                insights.append(f"📊 Good engagement rate of {engagement_rate}%")
                insights.append(f"📈 {total_likes:,} likes and {total_comments:,} comments show solid audience response")
                recommendations.append("Consider A/B testing different content types to boost engagement further")
            else:
                insights.append(f"⚠️ Low engagement rate of {engagement_rate}% - needs improvement")
                insights.append(f"📉 Only {total_likes:,} likes and {total_comments:,} comments from {total_views:,} views")
                recommendations.append("Focus on interactive content like polls, questions, and behind-the-scenes content")

            # Real view-to-engagement conversion
            if total_views > 0:
                view_to_engagement = ((total_likes + total_comments) / total_views) * 100
                insights.append(f"👁️ View-to-engagement conversion: {view_to_engagement:.2f}%")

            # Real top post analysis
            top_posts = metrics.get('top_performing_posts', [])
            if top_posts:
                best_post = top_posts[0]
                insights.append(f"🏆 Top performing post: '{best_post['content'][:100]}...' with {best_post['likes']:,} likes")
                recommendations.append(f"Analyze what made '{best_post['content'][:50]}...' successful - content type: {best_post['content_type']}")

            # Add real visualization data with actual content
            real_top_posts_chart = []
            for post in top_posts[:5]:
                real_top_posts_chart.append({
                    'title': post['content'][:50] + '...' if len(post['content']) > 50 else post['content'],
                    'likes': post['likes'],
                    'comments': post['comments'],
                    'views': post['views'],
                    'engagement': post['likes'] + post['comments'],
                    'content_type': post['content_type'],
                    'user': post['user'],
                    'url': post['url']
                })

            metrics['visualization_data'] = {
                **visualization_data,
                'top_posts_chart': real_top_posts_chart,
                'platform_performance': [{
                    'platform': 'Instagram (Real Data)',
                    'posts': metrics['total_posts'],
                    'likes': metrics['total_likes'],
                    'comments': metrics['total_comments'],
                    'views': metrics['total_views'],
                    'engagement_rate': engagement_rate
                }]
            }

            metrics['insights'] = insights
            metrics['recommendations'] = recommendations
            metrics['processing_time'] = processing_time
            metrics['report_generated_at'] = timezone.now().isoformat()
            metrics['data_source'] = 'REAL_APIFY_SCRAPED_DATA_ONLY'

            return metrics

        except Exception as e:
            logger.error(f"CRITICAL ERROR - Cannot process real data: {e}")
            return {
                'error': f'CRITICAL ERROR processing real scraped data: {str(e)}',
                'total_posts': 0,
                'data_source_count': 0,
                'message': 'Check Apify integration and scraped data availability'
            }


# Template-Specific API Views
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

class EngagementMetricsReportView(APIView):
    """Dedicated endpoint for Engagement Metrics reports with unique visualization"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, report_id):
        report = get_object_or_404(GeneratedReport, id=report_id, template__template_type='engagement_metrics')
        
        # Return report with engagement-specific structure
        return Response({
            'id': report.id,
            'title': report.title,
            'template_type': 'engagement_metrics',
            'status': report.status,
            'results': report.results,
            'created_at': report.created_at,
            'completed_at': report.completed_at
        })


class SentimentAnalysisReportView(APIView):
    """Dedicated endpoint for Sentiment Analysis reports with pie chart visualization"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, report_id):
        report = get_object_or_404(GeneratedReport, id=report_id, template__template_type='sentiment_analysis')
        
        return Response({
            'id': report.id,
            'title': report.title,
            'template_type': 'sentiment_analysis',
            'status': report.status,
            'results': report.results,
            'created_at': report.created_at,
            'completed_at': report.completed_at
        })


class ContentAnalysisReportView(APIView):
    """Dedicated endpoint for Content Analysis reports with hashtag visualization"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, report_id):
        report = get_object_or_404(GeneratedReport, id=report_id, template__template_type='content_analysis')
        
        return Response({
            'id': report.id,
            'title': report.title,
            'template_type': 'content_analysis',
            'status': report.status,
            'results': report.results,
            'created_at': report.created_at,
            'completed_at': report.completed_at
        })


class TrendAnalysisReportView(APIView):
    """Dedicated endpoint for Trend Analysis reports with trend line visualization"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, report_id):
        report = get_object_or_404(GeneratedReport, id=report_id, template__template_type='trend_analysis')
        
        return Response({
            'id': report.id,
            'title': report.title,
            'template_type': 'trend_analysis',
            'status': report.status,
            'results': report.results,
            'created_at': report.created_at,
            'completed_at': report.completed_at
        })


class CompetitiveAnalysisReportView(APIView):
    """Dedicated endpoint for Competitive Analysis reports with comparison visualization"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, report_id):
        report = get_object_or_404(GeneratedReport, id=report_id, template__template_type='competitive_analysis')
        
        return Response({
            'id': report.id,
            'title': report.title,
            'template_type': 'competitive_analysis',
            'status': report.status,
            'results': report.results,
            'created_at': report.created_at,
            'completed_at': report.completed_at
        })


class UserBehaviorReportView(APIView):
    """Dedicated endpoint for User Behavior reports with user engagement visualization"""
    permission_classes = [IsAuthenticated]

    def get(self, request, report_id):
        report = get_object_or_404(GeneratedReport, id=report_id, template__template_type='user_behavior')

        return Response({
            'id': report.id,
            'title': report.title,
            'template_type': 'user_behavior',
            'status': report.status,
            'results': report.results,
            'created_at': report.created_at,
            'completed_at': report.completed_at
        })


class EnhancedPDFAnalysisView(APIView):
    """Generate enhanced PDF analysis with deep insights using LLM"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            report_id = request.data.get('report_id')
            report_type = request.data.get('report_type')
            results = request.data.get('results', {})

            if not report_id or not report_type:
                return Response(
                    {'error': 'report_id and report_type are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generate enhanced analysis using OpenAI
            enhanced_analysis = self._generate_enhanced_analysis(
                report_id, report_type, results
            )

            return Response(enhanced_analysis, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error generating enhanced PDF analysis: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _generate_enhanced_analysis(self, report_id, report_type, results):
        """Generate comprehensive enhanced analysis using OpenAI"""

        # Prepare the prompt for OpenAI
        metrics_summary = self._extract_metrics_summary(results)

        # Prepare detailed data for the prompt
        metrics_summary = self._extract_detailed_metrics(results)
        visualizations_info = self._extract_visualization_info(results)
        top_performers = self._extract_top_performers(results)

        # Create specialized prompt based on report type
        is_sentiment_report = 'sentiment' in report_type.lower() or 'sentiment_counts' in results

        if is_sentiment_report:
            prompt = f"""
You are a senior sentiment analysis expert at FutureObjects creating an executive PDF report for a client.

REPORT TYPE: {report_type.replace('_', ' ').title()}

ACTUAL SENTIMENT DATA:
{metrics_summary}

SAMPLE COMMENTS FROM REAL USERS:
{top_performers}

VISUALIZATION DATA AVAILABLE:
{visualizations_info}

Your task is to provide deep sentiment analysis insights that a C-level executive would find valuable for reputation management and customer experience improvement.

Generate a comprehensive sentiment analysis in JSON format with these exact sections:

1. executive_summary: Write 3-4 professional paragraphs (minimum 400 words) that:
   - Start with the overall sentiment landscape and its brand reputation impact
   - Analyze the positive/neutral/negative distribution and what it means for customer satisfaction
   - Identify sentiment patterns across platforms using specific percentages
   - Discuss the strategic implications for brand perception and crisis management
   - End with forward-looking recommendations for sentiment improvement
   - Use professional business language suitable for C-level executives

2. deep_insights: Write 3-4 comprehensive analytical paragraphs (minimum 400 words) that:
   - Analyze the dominant sentiment (positive/neutral/negative) and its business implications
   - Identify sentiment patterns by platform (which platforms are most positive/negative)
   - Highlight concerning negative sentiment trends that need immediate attention
   - Analyze neutral sentiment as engagement opportunities
   - Examine common keywords and their sentiment associations
   - Look for sentiment correlations across different data points
   - Explain WHY each pattern matters for the business in paragraph form (NOT bullet points)
   - Connect insights to real business outcomes and strategic implications

3. strategic_recommendations: Write 3-4 comprehensive recommendation paragraphs (minimum 400 words) that:
   - Address negative sentiment with crisis management protocols
   - Provide tactics to convert neutral sentiment into positive engagement
   - Suggest ways to amplify and sustain positive sentiment
   - Include platform-specific strategies based on sentiment differences
   - Recommend response strategies for different sentiment types
   - Include expected impact on brand reputation (quantified where possible)
   - Mention implementation timeline and priority level
   - Present recommendations in flowing paragraph format with clear action steps
   - Prioritize recommendations from highest to lowest impact

4. detailed_analysis: Write 5-6 comprehensive paragraphs (minimum 600 words) that:
   - Deep dive into sentiment distribution patterns with specific numbers
   - Analyze positive comments: what customers love and how to amplify it
   - Examine negative comments: pain points, complaints, and crisis indicators
   - Discuss neutral sentiment: missed opportunities for engagement
   - Platform-by-platform sentiment breakdown with strategic implications
   - Keyword sentiment analysis: which topics drive positive vs negative sentiment
   - Provide sentiment trend predictions and proactive recommendations
   - Use data-driven language with specific percentages and numbers

5. conclusion: Write 2-3 summary paragraphs (minimum 250 words) that:
   - Summarize the overall sentiment health of the brand
   - Highlight the most critical action items from the recommendations
   - Provide a forward-looking perspective on sentiment trajectory
   - End with a clear call-to-action for stakeholders
   - Emphasize both opportunities and risks identified in the analysis

IMPORTANT: Write in professional, flowing paragraphs. Do NOT use bullet points or numbered lists. Use transition words and cohesive paragraph structure throughout.

Return ONLY valid JSON with NO markdown formatting:
{{
    "executive_summary": "...",
    "deep_insights": "...",
    "strategic_recommendations": "...",
    "detailed_analysis": "...",
    "conclusion": "..."
}}
"""
        else:
            prompt = f"""
You are a senior data analyst at FutureObjects creating an executive PDF report for a client.

REPORT TYPE: {report_type.replace('_', ' ').title()}

ACTUAL DATA METRICS:
{metrics_summary}

TOP PERFORMING CONTENT:
{top_performers}

VISUALIZATION DATA AVAILABLE:
{visualizations_info}

Your task is to provide deep, data-driven analysis that a C-level executive would find valuable.

Generate a comprehensive analysis in JSON format with these exact sections:

1. executive_summary: Write 3-4 professional paragraphs (minimum 300 words) that:
   - Start with the most critical finding and its business impact
   - Quantify performance using specific numbers from the data above
   - Compare against industry benchmarks
   - End with forward-looking strategic implications

2. deep_insights: Provide exactly 7 insights that are SPECIFIC to the actual numbers:
   - Each 2-3 sentences explaining the pattern AND why it matters
   - Based on data correlations you can infer
   - Must be actionable

3. strategic_recommendations: Provide exactly 7 prioritized recommendations that:
   - Are specific actions with clear next steps
   - Include expected impact (quantified)
   - Mention implementation timeline
   - Ordered by priority

4. detailed_analysis: Write 3-4 comprehensive paragraphs (minimum 400 words) diving into data patterns with specific numbers.

Return ONLY valid JSON:
{{
    "executive_summary": "...",
    "deep_insights": ["insight1", "insight2", "insight3", "insight4", "insight5", "insight6", "insight7"],
    "strategic_recommendations": ["rec1", "rec2", "rec3", "rec4", "rec5", "rec6", "rec7"],
    "detailed_analysis": "..."
}}
"""

        try:
            # Call OpenAI API
            response = report_openai_service.generate_insights(prompt)

            # Parse the response
            import json
            enhanced_data = json.loads(response)

            return enhanced_data

        except Exception as e:
            logger.error(f"Error calling OpenAI for enhanced analysis: {e}")
            logger.error(f"Full error details: {str(e)}", exc_info=True)

            # Convert arrays to paragraphs if needed
            insights_data = results.get('insights', [])
            recs_data = results.get('recommendations', [])

            insights_paragraph = ' '.join(insights_data) if isinstance(insights_data, list) else str(insights_data)
            recs_paragraph = ' '.join(recs_data) if isinstance(recs_data, list) else str(recs_data)

            # Return basic enhanced data if OpenAI fails
            return {
                'executive_summary': f'This {report_type.replace("_", " ")} report provides comprehensive analysis of your data across multiple platforms and metrics. The analysis reveals key trends, patterns, and actionable insights designed to improve your social media performance and brand engagement. Based on the data collected, we have identified both opportunities for growth and areas requiring strategic attention.',
                'deep_insights': insights_paragraph or 'The sentiment analysis reveals important patterns in audience engagement and brand perception. The data shows varying levels of sentiment across different platforms and content types, providing valuable insights for strategic decision-making. Understanding these patterns enables more targeted and effective communication strategies.',
                'strategic_recommendations': recs_paragraph or 'Based on the analysis, we recommend implementing a multi-faceted approach to sentiment management. This includes monitoring key sentiment indicators, responding proactively to negative feedback, and amplifying positive brand mentions. Platform-specific strategies should be developed to address unique audience characteristics and engagement patterns.',
                'detailed_analysis': f'The data analysis shows nuanced performance across key metrics, with particular attention to sentiment distribution and engagement quality. Further examination reveals opportunities for growth through targeted content optimization, strategic audience engagement, and platform-specific tactics. The sentiment patterns indicate both strengths to leverage and areas requiring immediate attention.',
                'conclusion': 'In summary, the sentiment analysis provides a comprehensive foundation for strategic decision-making. By addressing the identified opportunities and implementing the recommended actions, significant improvements in brand perception and customer satisfaction can be achieved. Continued monitoring and adaptive strategies will be essential for sustained success.'
            }

    def _extract_metrics_summary(self, results):
        """Extract key metrics from results for the prompt"""
        return self._extract_detailed_metrics(results)

    def _extract_detailed_metrics(self, results):
        """Extract detailed metrics with full context"""
        summary_parts = []

        # SENTIMENT ANALYSIS METRICS (Priority for sentiment reports)
        if 'sentiment_counts' in results or 'sentiment_breakdown' in results:
            sent = results.get('sentiment_counts') or results.get('sentiment_breakdown', {})
            total = results.get('total_comments') or results.get('data_source_count', 0)

            summary_parts.append(f"- Total Comments Analyzed: {total:,}")
            summary_parts.append(f"- Positive Sentiment: {sent.get('positive', 0):,} comments")
            summary_parts.append(f"- Neutral Sentiment: {sent.get('neutral', 0):,} comments")
            summary_parts.append(f"- Negative Sentiment: {sent.get('negative', 0):,} comments")

            if 'sentiment_percentages' in results:
                sent_pct = results['sentiment_percentages']
                summary_parts.append(f"- Sentiment Distribution: {sent_pct.get('positive', 0):.1f}% positive, {sent_pct.get('neutral', 0):.1f}% neutral, {sent_pct.get('negative', 0):.1f}% negative")

            if 'overall_sentiment' in results:
                summary_parts.append(f"- Overall Sentiment: {results['overall_sentiment'].title()}")

            if 'confidence_score' in results:
                summary_parts.append(f"- Analysis Confidence: {results['confidence_score'] * 100:.1f}%")

            # Platform breakdown for sentiment
            if 'platform_breakdown' in results:
                summary_parts.append("\n- Platform Sentiment Breakdown:")
                for platform, data in list(results['platform_breakdown'].items())[:5]:
                    if isinstance(data, dict) and 'sentiment_distribution' in data:
                        dist = data['sentiment_distribution']
                        summary_parts.append(f"  • {platform}: {dist.get('positive', 0):.0f}% pos, {dist.get('neutral', 0):.0f}% neu, {dist.get('negative', 0):.0f}% neg ({data.get('total_comments', 0)} comments)")

            # Top keywords
            if 'trending_keywords' in results:
                keywords = results['trending_keywords'][:10]
                if keywords:
                    try:
                        keyword_list = []
                        for kw in keywords:
                            if isinstance(kw, dict):
                                # Handle both 'keyword' and 'word' keys
                                keyword_list.append(kw.get('keyword', kw.get('word', str(kw))))
                            else:
                                keyword_list.append(str(kw))
                        if keyword_list:
                            summary_parts.append(f"\n- Top Keywords: {', '.join(keyword_list)}")
                    except Exception as e:
                        logger.error(f"Error extracting keywords: {e}")

            # Word sentiment details
            if 'word_sentiment_details' in results:
                words = results['word_sentiment_details'][:5]
                if words:
                    summary_parts.append("\n- Common Words with Sentiment:")
                    for word_data in words:
                        word = word_data.get('word', '')
                        sent_breakdown = word_data.get('sentiment_breakdown', {})
                        total_mentions = word_data.get('total_mentions', 0)
                        summary_parts.append(f"  • '{word}': {total_mentions} mentions - {sent_breakdown.get('positive', 0)} pos, {sent_breakdown.get('neutral', 0)} neu, {sent_breakdown.get('negative', 0)} neg")

        # Core engagement metrics (for non-sentiment reports)
        elif 'total_engagement' in results:
            if 'total_engagement' in results:
                summary_parts.append(f"- Total Engagement: {results['total_engagement']:,} interactions")
            if 'avg_engagement_rate' in results:
                summary_parts.append(f"- Average Engagement Rate: {results['avg_engagement_rate']:.2f}% (Industry avg: 3-5%)")
            if 'total_posts' in results:
                summary_parts.append(f"- Total Posts Analyzed: {results['total_posts']:,}")
            if 'total_likes' in results:
                summary_parts.append(f"- Total Likes: {results['total_likes']:,}")
            if 'total_comments' in results:
                summary_parts.append(f"- Total Comments: {results['total_comments']:,}")
            if 'total_views' in results:
                summary_parts.append(f"- Total Views: {results['total_views']:,}")

            # Growth and trend metrics
            if 'growth_rate' in results:
                summary_parts.append(f"- Growth Rate: {results['growth_rate']:+.1f}%")
            if 'follower_growth' in results:
                summary_parts.append(f"- Follower Growth: {results['follower_growth']:+,}")

        # User behavior metrics
        elif 'total_users' in results:
            summary_parts.append(f"- Total Users: {results['total_users']:,}")
            if 'active_users' in results:
                summary_parts.append(f"- Active Users: {results['active_users']:,}")
            if 'avg_session_time' in results:
                summary_parts.append(f"- Average Session Time: {results['avg_session_time']:.1f} minutes")
            if 'total_posts' in results:
                summary_parts.append(f"- Total Posts Analyzed: {results['total_posts']:,}")

        # Content performance
        if 'content_type_counts' in results:
            types = results['content_type_counts']
            summary_parts.append(f"- Content Types: {', '.join([f'{k}: {v}' for k, v in list(types.items())[:5]])}")

        return "\n".join(summary_parts) if summary_parts else "No detailed metrics available"

    def _extract_top_performers(self, results):
        """Extract top performing content details"""
        performers = []

        # SENTIMENT ANALYSIS: Sample comments by sentiment
        if 'sample_comments' in results:
            samples = results['sample_comments']

            if samples.get('positive'):
                performers.append("POSITIVE COMMENTS:")
                for i, comment in enumerate(samples['positive'][:3], 1):
                    performers.append(f"{i}. \"{comment[:150]}...\"")

            if samples.get('negative'):
                performers.append("\nNEGATIVE COMMENTS:")
                for i, comment in enumerate(samples['negative'][:3], 1):
                    performers.append(f"{i}. \"{comment[:150]}...\"")

            if samples.get('neutral'):
                performers.append("\nNEUTRAL COMMENTS:")
                for i, comment in enumerate(samples['neutral'][:2], 1):
                    performers.append(f"{i}. \"{comment[:150]}...\"")

        # REGULAR REPORTS: Top performing posts
        elif 'top_performing_posts' in results:
            posts = results['top_performing_posts'][:5]
            performers.append("TOP PERFORMING POSTS:")
            for i, post in enumerate(posts, 1):
                content = post.get('content', '')[:100] + '...' if len(post.get('content', '')) > 100 else post.get('content', 'N/A')
                likes = post.get('likes', 0)
                comments = post.get('comments', 0)
                views = post.get('views', 0)
                performers.append(f"{i}. '{content}' - {likes:,} likes, {comments:,} comments, {views:,} views")

        if 'most_engaged_users' in results:
            users = results['most_engaged_users'][:3]
            performers.append("\nTOP ENGAGED USERS:")
            for user in users:
                performers.append(f"- @{user.get('username', 'unknown')}: {user.get('engagement_score', 0):.0f} engagement score")

        return "\n".join(performers) if performers else "No top performers data available"

    def _extract_visualization_info(self, results):
        """Extract visualization data context"""
        viz_info = []

        if 'visualizations' in results:
            viz = results['visualizations']
            for key in viz.keys():
                viz_info.append(f"- {key.replace('_', ' ').title()} chart available")

        if 'platform_breakdown' in results:
            platforms = results['platform_breakdown']
            viz_info.append(f"- Platform data: {', '.join(platforms.keys())}")

        return "\n".join(viz_info) if viz_info else "Standard visualizations available"
