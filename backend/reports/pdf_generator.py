from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime
import json

class ReportPDFGenerator:
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

    def generate_sentiment_analysis_pdf(self, report_data, title):
        """Generate PDF for sentiment analysis report"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)

        story = []

        # Title
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 20))

        # Report metadata
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", self.styles['Normal']))
        story.append(Paragraph(f"Report Type: Sentiment Analysis", self.styles['Normal']))
        if report_data.get('ai_generated'):
            story.append(Paragraph("Generated with: OpenAI GPT-4o-mini", self.styles['Normal']))
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
            story.append(Spacer(1, 20))

        # Trending keywords section
        keywords = report_data.get('trending_keywords', [])
        if keywords:
            story.append(Paragraph("Trending Keywords", self.styles['CustomSubtitle']))
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

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    def generate_engagement_metrics_pdf(self, report_data, title):
        """Generate PDF for engagement metrics report"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)

        story = []

        # Title
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 20))

        # Report metadata
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", self.styles['Normal']))
        story.append(Paragraph(f"Report Type: Engagement Metrics", self.styles['Normal']))
        if report_data.get('ai_generated'):
            story.append(Paragraph("Generated with: OpenAI GPT-4o-mini", self.styles['Normal']))
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

        # Performance analysis
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
        return buffer

    def generate_content_analysis_pdf(self, report_data, title):
        """Generate PDF for content analysis report"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)

        story = []

        # Title
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 20))

        # Report metadata
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", self.styles['Normal']))
        story.append(Paragraph(f"Report Type: Content Analysis", self.styles['Normal']))
        if report_data.get('ai_generated'):
            story.append(Paragraph("Generated with: OpenAI GPT-4o-mini", self.styles['Normal']))
        story.append(Spacer(1, 20))

        # Content performance section
        content_perf = report_data.get('content_performance', {})
        if content_perf:
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
        return buffer

    def generate_generic_pdf(self, report_data, title, template_type):
        """Generate a generic PDF for other report types"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)

        story = []

        # Title
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 20))

        # Report metadata
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", self.styles['Normal']))
        story.append(Paragraph(f"Report Type: {template_type.replace('_', ' ').title()}", self.styles['Normal']))
        if report_data.get('ai_generated'):
            story.append(Paragraph("Generated with: OpenAI GPT-4o-mini", self.styles['Normal']))
        story.append(Spacer(1, 20))

        # Generic content display
        story.append(Paragraph("Report Data", self.styles['CustomSubtitle']))

        # Display data as formatted text
        for key, value in report_data.items():
            if key not in ['ai_generated', 'generation_timestamp', 'data_source_count']:
                story.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b>", self.styles['Normal']))
                if isinstance(value, (dict, list)):
                    story.append(Paragraph(f"<pre>{json.dumps(value, indent=2)}</pre>", self.styles['Normal']))
                else:
                    story.append(Paragraph(str(value), self.styles['Normal']))
                story.append(Spacer(1, 10))

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

# Global PDF generator instance
pdf_generator = ReportPDFGenerator()