import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reports.models import GeneratedReport
from reports.enhanced_report_service import EnhancedReportService

# Get existing competitive analysis reports
reports = GeneratedReport.objects.filter(template__template_type='competitive_analysis').order_by('-created_at')[:5]
print(f'Found {len(reports)} competitive analysis reports:')

for report in reports:
    print(f'  ID: {report.id}, Title: {report.title}, Status: {report.status}')

if reports:
    # Use the first report
    report = reports[0]
    print(f'\nUsing report ID {report.id}: {report.title}')
    
    # Generate enhanced analysis
    enhanced_service = EnhancedReportService()
    
    try:
        result = enhanced_service.generate_competitive_analysis(report)
        
        print('📈 ENHANCED ANALYSIS RESULTS:')
        print(f'   Data Source Count: {result.get("data_source_count")}')
        
        # Show AI insights
        insights = result.get('insights', [])
        print(f'\n🧠 AI INSIGHTS ({len(insights)} insights):')
        for i, insight in enumerate(insights, 1):
            if isinstance(insight, str) and insight.strip():
                print(f'   {i}. {insight}')
            
        # Show recommendations
        recommendations = result.get('recommendations', [])
        print(f'\n💡 RECOMMENDATIONS ({len(recommendations)} recommendations):')
        for i, rec in enumerate(recommendations, 1):
            if isinstance(rec, str) and rec.strip():
                print(f'   {i}. {rec}')
                
        # Update report
        report.results = result
        report.status = 'completed'
        report.save()
        print(f'\n✅ Report {report.id} updated with enhanced AI analysis')
        print(f'🎯 Access at: http://localhost:5185/organizations/5/projects/6/reports/competitive-analysis/{report.id}')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
else:
    print('No competitive analysis reports found in the database')