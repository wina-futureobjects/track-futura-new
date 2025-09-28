from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime
import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
import tempfile
import os

# Set matplotlib style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class EnhancedReportPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()

    def setup_custom_styles(self):
        """Setup custom styles for the PDF"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#1976d2'),
            alignment=TA_CENTER
        ))

        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor('#424242'),
            alignment=TA_LEFT
        ))

        # Chart caption style
        self.styles.add(ParagraphStyle(
            name='ChartCaption',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=15,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        ))

        # Insight style
        self.styles.add(ParagraphStyle(
            name='InsightStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            leftIndent=20,
            textColor=colors.HexColor('#2e7d32')
        ))

        # Recommendation style
        self.styles.add(ParagraphStyle(
            name='RecommendationStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            leftIndent=20,
            textColor=colors.HexColor('#d32f2f')
        ))

    def create_chart_image(self, fig, dpi=150):
        """Convert matplotlib figure to image for PDF"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            fig.savefig(tmp_file.name, dpi=dpi, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            plt.close(fig)
            return tmp_file.name

    def create_sentiment_pie_chart(self, sentiment_distribution):
        """Create pie chart for sentiment distribution"""
        if not sentiment_distribution:
            return None

        fig, ax = plt.subplots(figsize=(8, 6))

        labels = []
        sizes = []
        colors_list = []

        for sentiment, percentage in sentiment_distribution.items():
            if percentage > 0:
                labels.append(f'{sentiment.title()}\n({percentage}%)')
                sizes.append(percentage)
                if sentiment.lower() == 'positive':
                    colors_list.append('#4CAF50')
                elif sentiment.lower() == 'negative':
                    colors_list.append('#F44336')
                else:
                    colors_list.append('#FF9800')

        if sizes:
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors_list,
                                            autopct='%1.1f%%', startangle=90,
                                            textprops={'fontsize': 12})

            # Enhance text appearance
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(11)

        ax.set_title('Sentiment Distribution', fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()

        return self.create_chart_image(fig)

    def create_engagement_trends_chart(self, trend_data):
        """Create line chart for engagement trends"""
        if not trend_data:
            return None

        fig, ax = plt.subplots(figsize=(10, 6))

        # Sample trend data structure: [{'date': '2024-01', 'likes': 100, 'comments': 50, 'shares': 25}, ...]
        dates = [item.get('date', '') for item in trend_data]
        likes = [item.get('likes', 0) for item in trend_data]
        comments = [item.get('comments', 0) for item in trend_data]
        shares = [item.get('shares', 0) for item in trend_data]

        if dates and any([likes, comments, shares]):
            x = range(len(dates))

            ax.plot(x, likes, marker='o', linewidth=2, label='Likes', color='#2196F3')
            ax.plot(x, comments, marker='s', linewidth=2, label='Comments', color='#4CAF50')
            ax.plot(x, shares, marker='^', linewidth=2, label='Shares', color='#FF9800')

            ax.set_xlabel('Time Period', fontsize=12, fontweight='bold')
            ax.set_ylabel('Engagement Count', fontsize=12, fontweight='bold')
            ax.set_title('Engagement Trends Over Time', fontsize=16, fontweight='bold', pad=20)

            ax.set_xticks(x)
            ax.set_xticklabels(dates, rotation=45, ha='right')
            ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
            ax.grid(True, alpha=0.3)

            # Add value annotations on peaks
            if likes:
                max_likes_idx = likes.index(max(likes))
                ax.annotate(f'Peak: {max(likes)}',
                           xy=(max_likes_idx, max(likes)),
                           xytext=(10, 10), textcoords='offset points',
                           bbox=dict(boxstyle='round,pad=0.3', fc='yellow', alpha=0.7),
                           arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

        plt.tight_layout()
        return self.create_chart_image(fig)

    def create_platform_performance_chart(self, platform_data):
        """Create bar chart for platform performance"""
        if not platform_data:
            return None

        fig, ax = plt.subplots(figsize=(10, 6))

        platforms = list(platform_data.keys())
        engagement_rates = [data.get('avg_engagement', 0) for data in platform_data.values()]

        if platforms and engagement_rates:
            colors_list = ['#E1306C', '#1877F2', '#0A66C2', '#000000', '#FF0000'][:len(platforms)]

            bars = ax.bar(platforms, engagement_rates, color=colors_list, alpha=0.8, edgecolor='black', linewidth=1)

            # Add value labels on bars
            for bar, rate in zip(bars, engagement_rates):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')

            ax.set_xlabel('Platform', fontsize=12, fontweight='bold')
            ax.set_ylabel('Average Engagement Rate (%)', fontsize=12, fontweight='bold')
            ax.set_title('Platform Performance Comparison', fontsize=16, fontweight='bold', pad=20)
            ax.grid(True, alpha=0.3, axis='y')

            # Customize platform labels
            ax.tick_params(axis='x', labelsize=11, rotation=45)
            ax.tick_params(axis='y', labelsize=11)

        plt.tight_layout()
        return self.create_chart_image(fig)

    def create_content_type_chart(self, content_performance):
        """Create horizontal bar chart for content type performance"""
        if not content_performance:
            return None

        fig, ax = plt.subplots(figsize=(10, 6))

        content_types = list(content_performance.keys())
        engagement_values = [data.get('avg_engagement', 0) for data in content_performance.values()]

        if content_types and engagement_values:
            colors_list = plt.cm.Set3(np.linspace(0, 1, len(content_types)))

            bars = ax.barh(content_types, engagement_values, color=colors_list, alpha=0.8, edgecolor='black')

            # Add value labels
            for bar, value in zip(bars, engagement_values):
                width = bar.get_width()
                ax.text(width + 0.5, bar.get_y() + bar.get_height()/2.,
                       f'{value:.1f}', ha='left', va='center', fontweight='bold')

            ax.set_xlabel('Average Engagement', fontsize=12, fontweight='bold')
            ax.set_ylabel('Content Type', fontsize=12, fontweight='bold')
            ax.set_title('Content Type Performance', fontsize=16, fontweight='bold', pad=20)
            ax.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()
        return self.create_chart_image(fig)

    def create_keyword_cloud_chart(self, keywords):
        """Create a visual representation of trending keywords"""
        if not keywords:
            return None

        fig, ax = plt.subplots(figsize=(10, 6))

        # Extract top 15 keywords
        top_keywords = keywords[:15]
        keyword_names = [k.get('keyword', '') for k in top_keywords]
        keyword_counts = [k.get('count', 0) for k in top_keywords]

        if keyword_names and keyword_counts:
            # Create bubble chart
            colors = plt.cm.viridis(np.linspace(0, 1, len(keyword_names)))
            sizes = [count * 50 for count in keyword_counts]  # Scale for visibility

            scatter = ax.scatter(range(len(keyword_names)), keyword_counts,
                               s=sizes, c=colors, alpha=0.7, edgecolors='black')

            # Add keyword labels
            for i, (keyword, count) in enumerate(zip(keyword_names, keyword_counts)):
                ax.annotate(keyword, (i, count), xytext=(5, 5),
                           textcoords='offset points', fontsize=9, fontweight='bold')

            ax.set_xlabel('Keywords (ranked by frequency)', fontsize=12, fontweight='bold')
            ax.set_ylabel('Frequency Count', fontsize=12, fontweight='bold')
            ax.set_title('Trending Keywords Analysis', fontsize=16, fontweight='bold', pad=20)
            ax.set_xticks(range(len(keyword_names)))
            ax.set_xticklabels([f'#{i+1}' for i in range(len(keyword_names))])
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return self.create_chart_image(fig)

    def generate_sentiment_analysis_pdf(self, report_data, title):
        """Generate enhanced PDF for sentiment analysis report with visualizations"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)

        story = []
        chart_files = []  # Track temporary files for cleanup

        try:
            # Title
            story.append(Paragraph(title, self.styles['CustomTitle']))
            story.append(Spacer(1, 20))

            # Report metadata
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", self.styles['Normal']))
            story.append(Paragraph(f"Report Type: Sentiment Analysis with Visualizations", self.styles['Normal']))
            if report_data.get('ai_generated'):
                story.append(Paragraph("Generated with: OpenAI GPT-4o-mini + Data Visualizations", self.styles['Normal']))
            story.append(Spacer(1, 20))

            # Summary section
            summary = report_data.get('summary', {})
            story.append(Paragraph("Executive Summary", self.styles['CustomSubtitle']))

            summary_data = [
                ['Total Comments Analyzed', str(summary.get('total_comments_analyzed', 0))],
                ['Overall Sentiment', summary.get('overall_sentiment', 'N/A').title()],
                ['Average Confidence', f"{summary.get('confidence_average', 0)}%"],
            ]

            distribution = summary.get('sentiment_distribution', {})
            if distribution:
                summary_data.extend([
                    ['Positive Sentiment', f"{distribution.get('positive', 0)}%"],
                    ['Negative Sentiment', f"{distribution.get('negative', 0)}%"],
                    ['Neutral Sentiment', f"{distribution.get('neutral', 0)}%"]
                ])

            summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5f5f5')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 20))

            # Sentiment Distribution Chart
            if distribution:
                chart_file = self.create_sentiment_pie_chart(distribution)
                if chart_file:
                    chart_files.append(chart_file)
                    story.append(Image(chart_file, width=5*inch, height=3.5*inch))
                    story.append(Paragraph("Figure 1: Sentiment Distribution Analysis", self.styles['ChartCaption']))
                    story.append(Spacer(1, 20))

            # Trending Keywords Chart
            keywords = report_data.get('trending_keywords', [])
            if keywords:
                story.append(Paragraph("Keyword Analysis", self.styles['CustomSubtitle']))

                chart_file = self.create_keyword_cloud_chart(keywords)
                if chart_file:
                    chart_files.append(chart_file)
                    story.append(Image(chart_file, width=6*inch, height=3.5*inch))
                    story.append(Paragraph("Figure 2: Trending Keywords Frequency Analysis", self.styles['ChartCaption']))
                    story.append(Spacer(1, 20))

                # Keywords table
                keyword_data = [['Keyword', 'Count', 'Sentiment']]
                for keyword in keywords[:10]:  # Top 10
                    keyword_data.append([
                        keyword.get('keyword', ''),
                        str(keyword.get('count', 0)),
                        keyword.get('sentiment', '').title()
                    ])

                keyword_table = Table(keyword_data, colWidths=[2*inch, 1*inch, 1.5*inch])
                keyword_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e3f2fd')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(keyword_table)
                story.append(Spacer(1, 20))

            # Insights section
            insights = report_data.get('insights', [])
            if insights:
                story.append(Paragraph("Key Insights", self.styles['CustomSubtitle']))
                for insight in insights:
                    story.append(Paragraph(f"• {insight}", self.styles['InsightStyle']))
                story.append(Spacer(1, 20))

            # Recommendations section
            recommendations = report_data.get('recommendations', [])
            if recommendations:
                story.append(Paragraph("Recommendations", self.styles['CustomSubtitle']))
                for recommendation in recommendations:
                    story.append(Paragraph(f"• {recommendation}", self.styles['RecommendationStyle']))

            # Build PDF
            doc.build(story)
            buffer.seek(0)

            # Cleanup temporary chart files
            for chart_file in chart_files:
                try:
                    os.unlink(chart_file)
                except:
                    pass

            return buffer

        except Exception as e:
            # Cleanup on error
            for chart_file in chart_files:
                try:
                    os.unlink(chart_file)
                except:
                    pass
            raise e

    def generate_engagement_metrics_pdf(self, report_data, title):
        """Generate enhanced PDF for engagement metrics report with visualizations"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)

        story = []
        chart_files = []

        try:
            # Title
            story.append(Paragraph(title, self.styles['CustomTitle']))
            story.append(Spacer(1, 20))

            # Report metadata
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", self.styles['Normal']))
            story.append(Paragraph(f"Report Type: Engagement Metrics with Visualizations", self.styles['Normal']))
            if report_data.get('ai_generated'):
                story.append(Paragraph("Generated with: OpenAI GPT-4o-mini + Data Visualizations", self.styles['Normal']))
            story.append(Spacer(1, 20))

            # Summary section
            summary = report_data.get('summary', {})
            story.append(Paragraph("Engagement Overview", self.styles['CustomSubtitle']))

            summary_data = [
                ['Total Posts', str(summary.get('total_posts', 0))],
                ['Total Likes', str(summary.get('total_likes', 0))],
                ['Total Comments', str(summary.get('total_comments', 0))],
                ['Total Shares', str(summary.get('total_shares', 0))],
                ['Average Engagement Rate', f"{summary.get('average_engagement_rate', 0)}%"]
            ]

            summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5f5f5')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 20))

            # Platform Performance Chart
            platform_data = report_data.get('platform_performance', {})
            if platform_data:
                chart_file = self.create_platform_performance_chart(platform_data)
                if chart_file:
                    chart_files.append(chart_file)
                    story.append(Image(chart_file, width=6*inch, height=3.5*inch))
                    story.append(Paragraph("Figure 1: Platform Performance Comparison", self.styles['ChartCaption']))
                    story.append(Spacer(1, 20))

            # Engagement Trends Chart
            trends = report_data.get('engagement_trends', [])
            if trends:
                chart_file = self.create_engagement_trends_chart(trends)
                if chart_file:
                    chart_files.append(chart_file)
                    story.append(Image(chart_file, width=6*inch, height=3.5*inch))
                    story.append(Paragraph("Figure 2: Engagement Trends Over Time", self.styles['ChartCaption']))
                    story.append(Spacer(1, 20))

            # Performance analysis table
            performance = report_data.get('performance_analysis', [])
            if performance:
                story.append(Paragraph("Top Performing Content", self.styles['CustomSubtitle']))
                perf_data = [['Content Title', 'Likes', 'Comments', 'Shares', 'Engagement Rate']]
                for item in performance[:5]:  # Top 5
                    perf_data.append([
                        item.get('title', '')[:30] + ('...' if len(item.get('title', '')) > 30 else ''),
                        str(item.get('likes', 0)),
                        str(item.get('comments', 0)),
                        str(item.get('shares', 0)),
                        f"{item.get('engagement_rate', 0)}%"
                    ])

                perf_table = Table(perf_data, colWidths=[2.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1*inch])
                perf_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8f5e8')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(perf_table)
                story.append(Spacer(1, 20))

            # Insights and recommendations
            insights = report_data.get('insights', [])
            if insights:
                story.append(Paragraph("Key Insights", self.styles['CustomSubtitle']))
                for insight in insights:
                    story.append(Paragraph(f"• {insight}", self.styles['InsightStyle']))
                story.append(Spacer(1, 20))

            recommendations = report_data.get('recommendations', [])
            if recommendations:
                story.append(Paragraph("Recommendations", self.styles['CustomSubtitle']))
                for recommendation in recommendations:
                    story.append(Paragraph(f"• {recommendation}", self.styles['RecommendationStyle']))

            # Build PDF
            doc.build(story)
            buffer.seek(0)

            # Cleanup temporary chart files
            for chart_file in chart_files:
                try:
                    os.unlink(chart_file)
                except:
                    pass

            return buffer

        except Exception as e:
            # Cleanup on error
            for chart_file in chart_files:
                try:
                    os.unlink(chart_file)
                except:
                    pass
            raise e

    def generate_content_analysis_pdf(self, report_data, title):
        """Generate enhanced PDF for content analysis report with visualizations"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)

        story = []
        chart_files = []

        try:
            # Title
            story.append(Paragraph(title, self.styles['CustomTitle']))
            story.append(Spacer(1, 20))

            # Report metadata
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", self.styles['Normal']))
            story.append(Paragraph(f"Report Type: Content Analysis with Visualizations", self.styles['Normal']))
            if report_data.get('ai_generated'):
                story.append(Paragraph("Generated with: OpenAI GPT-4o-mini + Data Visualizations", self.styles['Normal']))
            story.append(Spacer(1, 20))

            # Content Performance Chart
            content_perf = report_data.get('content_performance', {})
            if content_perf:
                chart_file = self.create_content_type_chart(content_perf)
                if chart_file:
                    chart_files.append(chart_file)
                    story.append(Image(chart_file, width=6*inch, height=3.5*inch))
                    story.append(Paragraph("Figure 1: Content Type Performance Analysis", self.styles['ChartCaption']))
                    story.append(Spacer(1, 20))

                # Content performance table
                story.append(Paragraph("Content Performance by Type", self.styles['CustomSubtitle']))
                perf_data = [['Content Type', 'Average Engagement', 'Percentage of Total']]
                for content_type, metrics in content_perf.items():
                    perf_data.append([
                        content_type.title(),
                        str(metrics.get('avg_engagement', 0)),
                        f"{metrics.get('percentage', 0)}%"
                    ])

                perf_table = Table(perf_data, colWidths=[2*inch, 2*inch, 2*inch])
                perf_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fff3e0')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(perf_table)
                story.append(Spacer(1, 20))

            # Hashtag analysis
            hashtag_analysis = report_data.get('hashtag_analysis', [])
            if hashtag_analysis:
                story.append(Paragraph("Hashtag Performance", self.styles['CustomSubtitle']))
                hashtag_data = [['Hashtag', 'Usage Count', 'Average Engagement']]
                for hashtag in hashtag_analysis[:10]:
                    hashtag_data.append([
                        hashtag.get('hashtag', ''),
                        str(hashtag.get('usage', 0)),
                        str(hashtag.get('avg_engagement', 0))
                    ])

                hashtag_table = Table(hashtag_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
                hashtag_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3e5f5')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(hashtag_table)
                story.append(Spacer(1, 20))

            # Insights and recommendations
            insights = report_data.get('insights', [])
            if insights:
                story.append(Paragraph("Key Insights", self.styles['CustomSubtitle']))
                for insight in insights:
                    story.append(Paragraph(f"• {insight}", self.styles['InsightStyle']))
                story.append(Spacer(1, 20))

            recommendations = report_data.get('recommendations', [])
            if recommendations:
                story.append(Paragraph("Recommendations", self.styles['CustomSubtitle']))
                for recommendation in recommendations:
                    story.append(Paragraph(f"• {recommendation}", self.styles['RecommendationStyle']))

            # Build PDF
            doc.build(story)
            buffer.seek(0)

            # Cleanup temporary chart files
            for chart_file in chart_files:
                try:
                    os.unlink(chart_file)
                except:
                    pass

            return buffer

        except Exception as e:
            # Cleanup on error
            for chart_file in chart_files:
                try:
                    os.unlink(chart_file)
                except:
                    pass
            raise e

# Global enhanced PDF generator instance
enhanced_pdf_generator = EnhancedReportPDFGenerator()