import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import axios from 'axios';
import { FUTUREOBJECTS_COLORS } from '../constants/colors';

interface EnhancedReportData {
  title: string;
  reportType: string;
  executiveSummary: string;
  keyMetrics: Array<{ label: string; value: string; description?: string }>;
  insights: string | string[]; // Support both paragraph and array formats
  recommendations: string | string[];
  detailedAnalysis?: string;
  conclusion?: string;
  charts?: string[]; // base64 chart images
}

// Generate enhanced PDF report with LLM analysis
export const generateEnhancedPDF = async (
  reportId: number,
  reportTitle: string,
  reportType: string,
  results: any
) => {
  try {
    // Show loading indicator
    console.log('Generating enhanced PDF report...');

    // Step 1: Get LLM-enhanced analysis from backend
    const enhancedData = await getEnhancedAnalysis(reportId, reportType, results);

    // Step 2: Capture charts from the page
    const chartImages = await captureCharts();

    // Step 3: Create PDF with enhanced content
    const pdf = await createEnhancedPDF({
      title: reportTitle,
      reportType: reportType,
      executiveSummary: enhancedData.executive_summary || '',
      keyMetrics: extractKeyMetrics(results),
      insights: enhancedData.deep_insights || enhancedData.insights || [],
      recommendations: enhancedData.strategic_recommendations || enhancedData.recommendations || [],
      detailedAnalysis: enhancedData.detailed_analysis || '',
      charts: chartImages
    });

    // Step 4: Save the PDF
    const timestamp = new Date().toISOString().split('T')[0];
    const filename = `${reportTitle.replace(/\s+/g, '_')}_Enhanced_${timestamp}.pdf`;
    pdf.save(filename);

    console.log('Enhanced PDF generated successfully:', filename);
    return true;
  } catch (error) {
    console.error('Error generating enhanced PDF:', error);
    alert('Failed to generate enhanced PDF. Please try again.');
    return false;
  }
};

// Get enhanced analysis from backend using LLM
async function getEnhancedAnalysis(reportId: number, reportType: string, results: any) {
  try {
    // Try both token storage keys (authToken for main app, token for legacy)
    const token = localStorage.getItem('authToken') || localStorage.getItem('token');

    if (!token) {
      console.warn('No auth token found, using fallback data');
      throw new Error('No authentication token');
    }

    const response = await axios.post(
      `/api/reports/enhance-pdf-analysis/`,
      {
        report_id: reportId,
        report_type: reportType,
        results: results
      },
      {
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );

    return response.data;
  } catch (error) {
    console.error('Error getting enhanced analysis:', error);
    // Return basic data if LLM fails - use paragraphs if available, otherwise use arrays
    const insightsParagraph = Array.isArray(results.insights)
      ? results.insights.join(' ')
      : (results.insights || 'Comprehensive insights are being analyzed.');

    const recsParagraph = Array.isArray(results.recommendations)
      ? results.recommendations.join(' ')
      : (results.recommendations || 'Strategic recommendations are being developed.');

    return {
      executive_summary: 'This report provides comprehensive analysis of sentiment data, revealing key trends and actionable insights to improve brand perception and customer satisfaction.',
      deep_insights: insightsParagraph,
      strategic_recommendations: recsParagraph,
      detailed_analysis: 'Detailed analysis of sentiment patterns and trends is available in the full report data.',
      conclusion: 'The sentiment analysis provides valuable insights for strategic decision-making and brand management.'
    };
  }
}

// Capture chart images from the page
async function captureCharts(): Promise<string[]> {
  const chartImages: string[] = [];
  const chartElements = document.querySelectorAll('canvas');

  for (const canvas of Array.from(chartElements)) {
    try {
      const dataUrl = canvas.toDataURL('image/png', 1.0);
      chartImages.push(dataUrl);
    } catch (error) {
      console.error('Error capturing chart:', error);
    }
  }

  return chartImages;
}

// Extract key metrics from results
function extractKeyMetrics(results: any): Array<{ label: string; value: string; description?: string }> {
  const metrics: Array<{ label: string; value: string; description?: string }> = [];

  // SENTIMENT ANALYSIS METRICS
  if (results.sentiment_counts || results.sentiment_breakdown) {
    const counts = results.sentiment_counts || results.sentiment_breakdown;

    if (counts.positive !== undefined) {
      const percentage = results.sentiment_percentages?.positive || 0;
      metrics.push({
        label: 'Positive Sentiment',
        value: `${counts.positive.toLocaleString()} (${percentage.toFixed(1)}%)`,
        description: 'Comments with positive sentiment'
      });
    }

    if (counts.neutral !== undefined) {
      const percentage = results.sentiment_percentages?.neutral || 0;
      metrics.push({
        label: 'Neutral Sentiment',
        value: `${counts.neutral.toLocaleString()} (${percentage.toFixed(1)}%)`,
        description: 'Comments with neutral sentiment'
      });
    }

    if (counts.negative !== undefined) {
      const percentage = results.sentiment_percentages?.negative || 0;
      metrics.push({
        label: 'Negative Sentiment',
        value: `${counts.negative.toLocaleString()} (${percentage.toFixed(1)}%)`,
        description: 'Comments with negative sentiment'
      });
    }

    if (results.total_comments !== undefined || results.data_source_count !== undefined) {
      const total = results.total_comments || results.data_source_count;
      metrics.push({
        label: 'Total Analyzed',
        value: `${total.toLocaleString()} Comments`,
        description: 'Total comments analyzed'
      });
    }
  }
  // ENGAGEMENT METRICS
  else if (results.total_engagement !== undefined) {
    metrics.push({
      label: 'Total Engagement',
      value: results.total_engagement.toLocaleString(),
      description: 'Total interactions across all posts'
    });

    if (results.avg_engagement_rate !== undefined) {
      metrics.push({
        label: 'Avg Engagement Rate',
        value: `${results.avg_engagement_rate.toFixed(2)}%`,
        description: 'Average engagement percentage'
      });
    }

    if (results.total_posts !== undefined) {
      metrics.push({
        label: 'Total Posts',
        value: results.total_posts.toLocaleString(),
        description: 'Total number of posts analyzed'
      });
    }

    if (results.growth_rate !== undefined) {
      metrics.push({
        label: 'Growth Rate',
        value: `${results.growth_rate > 0 ? '+' : ''}${results.growth_rate.toFixed(1)}%`,
        description: 'Period-over-period growth'
      });
    }
  }
  // USER BEHAVIOR METRICS
  else if (results.total_users !== undefined) {
    metrics.push({
      label: 'Total Users',
      value: results.total_users.toLocaleString(),
      description: 'Total users in analysis'
    });

    if (results.active_users !== undefined) {
      metrics.push({
        label: 'Active Users',
        value: results.active_users.toLocaleString(),
        description: 'Active users in period'
      });
    }

    if (results.total_posts !== undefined) {
      metrics.push({
        label: 'Total Posts',
        value: results.total_posts.toLocaleString(),
        description: 'Total posts analyzed'
      });
    }
  }

  return metrics;
}

// Create the enhanced PDF document
async function createEnhancedPDF(data: EnhancedReportData): Promise<jsPDF> {
  const pdf = new jsPDF('p', 'mm', 'a4');
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 20;
  const contentWidth = pageWidth - (2 * margin);
  let yPosition = margin;

  // Helper function to check if we need a new page
  const checkNewPage = (requiredSpace: number) => {
    if (yPosition + requiredSpace > pageHeight - margin) {
      pdf.addPage();
      yPosition = margin;
      return true;
    }
    return false;
  };

  // Helper function to add text with word wrap and proper encoding
  const addWrappedText = (text: string, fontSize: number, fontStyle: string = 'normal', color: string = '#2D3748') => {
    pdf.setFontSize(fontSize);
    pdf.setFont('helvetica', fontStyle);
    pdf.setTextColor(color);

    // Clean text to remove problematic characters
    const cleanText = text
      .replace(/[^\x00-\x7F]/g, '') // Remove non-ASCII characters
      .replace(/\s+/g, ' ') // Normalize whitespace
      .trim();

    const lines = pdf.splitTextToSize(cleanText, contentWidth);

    for (const line of lines) {
      checkNewPage(fontSize * 0.5);
      pdf.text(line, margin, yPosition);
      yPosition += fontSize * 0.5;
    }
  };

  // 1. COVER PAGE
  pdf.setFillColor(79, 209, 197); // FutureObjects teal
  pdf.rect(0, 0, pageWidth, 80, 'F');

  pdf.setTextColor('#FFFFFF');
  pdf.setFontSize(32);
  pdf.setFont('helvetica', 'bold');
  pdf.text('ENHANCED REPORT', margin, 35);

  pdf.setFontSize(24);
  pdf.setFont('helvetica', 'normal');
  pdf.text(data.title, margin, 50);

  pdf.setFontSize(12);
  pdf.setFont('helvetica', 'normal');
  const date = new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
  pdf.text(`Generated: ${date}`, margin, 65);

  pdf.setFontSize(10);
  pdf.text(`Report Type: ${data.reportType}`, margin, 72);

  // FutureObjects branding
  pdf.setTextColor('#FFFFFF');
  pdf.setFontSize(14);
  pdf.setFont('helvetica', 'bold');
  pdf.text('FutureObjects Analytics', pageWidth - margin - 60, pageHeight - 20);

  // 2. EXECUTIVE SUMMARY (New Page)
  pdf.addPage();
  yPosition = margin;

  // Section header
  pdf.setFillColor(79, 209, 197);
  pdf.rect(margin - 5, yPosition - 7, contentWidth + 10, 12, 'F');
  pdf.setTextColor('#FFFFFF');
  pdf.setFontSize(16);
  pdf.setFont('helvetica', 'bold');
  pdf.text('EXECUTIVE SUMMARY', margin, yPosition);
  yPosition += 15;

  // Summary content - Clean encoding
  const cleanSummary = data.executiveSummary
    .replace(/[^\x00-\x7F]/g, '') // Remove non-ASCII
    .replace(/\s+/g, ' ') // Normalize whitespace
    .trim();

  pdf.setTextColor('#2D3748');
  pdf.setFontSize(11);
  pdf.setFont('helvetica', 'normal');
  pdf.setLineHeightFactor(1.5);

  const summaryLines = pdf.splitTextToSize(cleanSummary, contentWidth);
  summaryLines.forEach((line: string) => {
    checkNewPage(7);
    pdf.text(line, margin, yPosition);
    yPosition += 7;
  });

  yPosition += 10;

  // 3. KEY METRICS
  checkNewPage(60);

  pdf.setFillColor(79, 209, 197);
  pdf.rect(margin - 5, yPosition - 7, contentWidth + 10, 12, 'F');
  pdf.setTextColor('#FFFFFF');
  pdf.setFontSize(16);
  pdf.setFont('helvetica', 'bold');
  pdf.text('KEY METRICS', margin, yPosition);
  yPosition += 15;

  // Metrics in a grid
  const metricsPerRow = 2;
  const metricBoxWidth = (contentWidth - 10) / metricsPerRow;
  let metricIndex = 0;

  for (const metric of data.keyMetrics) {
    const col = metricIndex % metricsPerRow;
    const xPos = margin + (col * (metricBoxWidth + 10));

    if (col === 0 && metricIndex > 0) {
      yPosition += 35;
      checkNewPage(40);
    }

    // Metric box
    pdf.setDrawColor(79, 209, 197);
    pdf.setLineWidth(0.5);
    pdf.rect(xPos, yPosition, metricBoxWidth, 30);

    // Metric label
    pdf.setTextColor('#718096');
    pdf.setFontSize(9);
    pdf.setFont('helvetica', 'normal');
    pdf.text(metric.label.toUpperCase(), xPos + 5, yPosition + 8);

    // Metric value
    pdf.setTextColor('#2D3748');
    pdf.setFontSize(18);
    pdf.setFont('helvetica', 'bold');
    pdf.text(metric.value, xPos + 5, yPosition + 18);

    // Metric description
    if (metric.description) {
      pdf.setTextColor('#A0AEC0');
      pdf.setFontSize(8);
      pdf.setFont('helvetica', 'normal');
      const descLines = pdf.splitTextToSize(metric.description, metricBoxWidth - 10);
      pdf.text(descLines[0], xPos + 5, yPosition + 25);
    }

    metricIndex++;
  }

  yPosition += 40;

  // 4. VISUALIZATIONS
  if (data.charts && data.charts.length > 0) {
    checkNewPage(100);

    pdf.setFillColor(79, 209, 197);
    pdf.rect(margin - 5, yPosition - 7, contentWidth + 10, 12, 'F');
    pdf.setTextColor('#FFFFFF');
    pdf.setFontSize(16);
    pdf.setFont('helvetica', 'bold');
    pdf.text('DATA VISUALIZATIONS', margin, yPosition);
    yPosition += 15;

    for (const chartImage of data.charts) {
      checkNewPage(90);

      try {
        const imgWidth = contentWidth;
        const imgHeight = 80;
        pdf.addImage(chartImage, 'PNG', margin, yPosition, imgWidth, imgHeight);
        yPosition += imgHeight + 10;
      } catch (error) {
        console.error('Error adding chart to PDF:', error);
      }
    }
  }

  // 5. KEY INSIGHTS (Paragraph Format)
  if (data.insights) {
    checkNewPage(60);

    pdf.setFillColor(79, 209, 197);
    pdf.rect(margin - 5, yPosition - 7, contentWidth + 10, 12, 'F');
    pdf.setTextColor('#FFFFFF');
    pdf.setFontSize(16);
    pdf.setFont('helvetica', 'bold');
    pdf.text('KEY INSIGHTS', margin, yPosition);
    yPosition += 15;

    // Support both paragraph string and array formats
    const insightsText = typeof data.insights === 'string'
      ? data.insights
      : data.insights.join(' ');

    // Clean text for proper rendering
    const cleanInsights = insightsText
      .replace(/[^\x00-\x7F]/g, '') // Remove non-ASCII
      .replace(/\s+/g, ' ') // Normalize whitespace
      .trim();

    pdf.setTextColor('#2D3748');
    pdf.setFontSize(11);
    pdf.setFont('helvetica', 'normal');
    pdf.setLineHeightFactor(1.5);

    const insightLines = pdf.splitTextToSize(cleanInsights, contentWidth);
    insightLines.forEach((line: string) => {
      checkNewPage(7);
      pdf.text(line, margin, yPosition);
      yPosition += 7;
    });

    yPosition += 10;
  }

  // 6. RECOMMENDATIONS (Paragraph Format)
  if (data.recommendations) {
    checkNewPage(60);

    pdf.setFillColor(203, 213, 224); // Very light grey #CBD5E0
    pdf.rect(margin - 5, yPosition - 7, contentWidth + 10, 12, 'F');
    pdf.setTextColor('#FFFFFF');
    pdf.setFontSize(16);
    pdf.setFont('helvetica', 'bold');
    pdf.text('RECOMMENDATIONS', margin, yPosition);
    yPosition += 15;

    // Support both paragraph string and array formats
    const recommendationsText = typeof data.recommendations === 'string'
      ? data.recommendations
      : data.recommendations.join(' ');

    // Clean text for proper rendering
    const cleanRecommendations = recommendationsText
      .replace(/[^\x00-\x7F]/g, '') // Remove non-ASCII
      .replace(/\s+/g, ' ') // Normalize whitespace
      .trim();

    pdf.setTextColor('#2D3748');
    pdf.setFontSize(11);
    pdf.setFont('helvetica', 'normal');
    pdf.setLineHeightFactor(1.5);

    const recLines = pdf.splitTextToSize(cleanRecommendations, contentWidth);
    recLines.forEach((line: string) => {
      checkNewPage(7);
      pdf.text(line, margin, yPosition);
      yPosition += 7;
    });

    yPosition += 10;
  }

  // 7. DETAILED ANALYSIS
  if (data.detailedAnalysis) {
    checkNewPage(60);

    pdf.setFillColor(203, 213, 224); // Very light grey #CBD5E0
    pdf.rect(margin - 5, yPosition - 7, contentWidth + 10, 12, 'F');
    pdf.setTextColor('#FFFFFF');
    pdf.setFontSize(16);
    pdf.setFont('helvetica', 'bold');
    pdf.text('DETAILED ANALYSIS', margin, yPosition);
    yPosition += 15;

    // Clean text for proper rendering
    const cleanAnalysis = data.detailedAnalysis
      .replace(/[^\x00-\x7F]/g, '') // Remove non-ASCII
      .replace(/\s+/g, ' ') // Normalize whitespace
      .trim();

    pdf.setTextColor('#2D3748');
    pdf.setFontSize(11);
    pdf.setFont('helvetica', 'normal');
    pdf.setLineHeightFactor(1.5);

    const analysisLines = pdf.splitTextToSize(cleanAnalysis, contentWidth);
    analysisLines.forEach((line: string) => {
      checkNewPage(7);
      pdf.text(line, margin, yPosition);
      yPosition += 7;
    });

    yPosition += 10;
  }

  // 8. CONCLUSION
  if ((data as any).conclusion) {
    checkNewPage(60);

    pdf.setFillColor(104, 211, 145); // Green
    pdf.rect(margin - 5, yPosition - 7, contentWidth + 10, 12, 'F');
    pdf.setTextColor('#FFFFFF');
    pdf.setFontSize(16);
    pdf.setFont('helvetica', 'bold');
    pdf.text('CONCLUSION', margin, yPosition);
    yPosition += 15;

    // Clean text for proper rendering
    const cleanConclusion = (data as any).conclusion
      .replace(/[^\x00-\x7F]/g, '') // Remove non-ASCII
      .replace(/\s+/g, ' ') // Normalize whitespace
      .trim();

    pdf.setTextColor('#2D3748');
    pdf.setFontSize(11);
    pdf.setFont('helvetica', 'normal');
    pdf.setLineHeightFactor(1.5);

    const conclusionLines = pdf.splitTextToSize(cleanConclusion, contentWidth);
    conclusionLines.forEach((line: string) => {
      checkNewPage(7);
      pdf.text(line, margin, yPosition);
      yPosition += 7;
    });
  }

  // Footer on last page
  const lastPageNumber = (pdf as any).internal.getNumberOfPages();
  pdf.setPage(lastPageNumber);
  pdf.setTextColor('#718096');
  pdf.setFontSize(8);
  pdf.setFont('helvetica', 'italic');
  pdf.text('Generated by FutureObjects Analytics Platform', pageWidth / 2, pageHeight - 10, { align: 'center' });

  return pdf;
}
