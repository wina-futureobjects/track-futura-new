#!/usr/bin/env python3
"""
BrightData Dashboard Investigation Script
Based on manager's guidance: "look at brightdata logs, use matching snapshot id"

This script provides step-by-step instructions for investigating
BrightData dashboard and finding the correct data access method.
"""

import webbrowser
import time
from datetime import datetime

class BrightDataDashboardInvestigation:
    def __init__(self):
        self.snapshot_ids = [
            "s_mggq02qnd20yqnt78",  # Instagram, processing
            "s_mggpf9c8d4954otj6"   # Instagram, processing
        ]
        self.customer_id = "hl_f7614f18"
        self.dataset_ids = {
            "instagram": "gd_lk5ns7kz21pck8jpis",
            "facebook": "gd_lkaxegm826bjpoo9m5"
        }
    
    def show_investigation_plan(self):
        """Display the investigation plan based on manager's guidance."""
        print("🎯 BRIGHTDATA DASHBOARD INVESTIGATION")
        print("=" * 50)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💬 Manager's Guidance: 'Look at BrightData logs, use matching snapshot ID'")
        print()
        
        print("🔍 INVESTIGATION TARGETS:")
        print("-" * 25)
        for i, snapshot_id in enumerate(self.snapshot_ids, 1):
            print(f"{i}. Snapshot ID: {snapshot_id}")
        print(f"3. Customer ID: {self.customer_id}")
        print(f"4. Instagram Dataset: {self.dataset_ids['instagram']}")
        print(f"5. Facebook Dataset: {self.dataset_ids['facebook']}")
        print()
        
        print("📋 STEP-BY-STEP INVESTIGATION:")
        print("-" * 32)
        self.show_dashboard_steps()
        print()
        
        print("🔧 WHAT TO LOOK FOR:")
        print("-" * 20)
        self.show_investigation_targets()
        print()
        
        print("📊 EXPECTED OUTCOMES:")
        print("-" * 21)
        self.show_expected_outcomes()
    
    def show_dashboard_steps(self):
        """Show step-by-step dashboard investigation."""
        steps = [
            "1. Open BrightData Dashboard (brightdata.com)",
            "2. Login with account credentials",
            "3. Navigate to 'Datasets' or 'Data Collection' section",
            "4. Look for Instagram dataset: gd_lk5ns7kz21pck8jpis",
            "5. Check for snapshots or jobs with IDs:",
            f"   - {self.snapshot_ids[0]}",
            f"   - {self.snapshot_ids[1]}",
            "6. Inspect any download/export buttons",
            "7. Open browser dev tools (F12)",
            "8. Monitor network requests when clicking data access",
            "9. Document any API calls made by the dashboard",
            "10. Check for CSV/JSON export options"
        ]
        
        for step in steps:
            print(f"   {step}")
    
    def show_investigation_targets(self):
        """Show what specific things to investigate."""
        targets = [
            "✅ Snapshot status (completed, processing, failed)",
            "✅ Data download buttons or links",
            "✅ Export options (CSV, JSON, XML)",
            "✅ API endpoints called by dashboard",
            "✅ Authentication headers in network requests",
            "✅ URL patterns for data access",
            "✅ File download URLs",
            "✅ Any 'logs' or 'history' sections"
        ]
        
        for target in targets:
            print(f"   {target}")
    
    def show_expected_outcomes(self):
        """Show what we expect to find."""
        outcomes = [
            "🎯 Discovery of working data access URLs",
            "🎯 Correct API endpoints for snapshot data",
            "🎯 Manual export capability as fallback",
            "🎯 Authentication requirements for API",
            "🎯 Evidence that snapshots contain real data"
        ]
        
        for outcome in outcomes:
            print(f"   {outcome}")
    
    def open_dashboard(self):
        """Open BrightData dashboard in browser."""
        dashboard_url = "https://brightdata.com/cp"
        print(f"🌐 Opening BrightData Dashboard: {dashboard_url}")
        try:
            webbrowser.open(dashboard_url)
            return True
        except Exception as e:
            print(f"❌ Error opening browser: {e}")
            print(f"📋 Manual URL: {dashboard_url}")
            return False
    
    def show_network_monitoring_guide(self):
        """Show how to monitor network requests."""
        print("\n🔍 NETWORK MONITORING GUIDE:")
        print("-" * 30)
        
        guide = [
            "1. Open browser Developer Tools (F12)",
            "2. Go to 'Network' tab",
            "3. Clear existing requests (trash icon)",
            "4. Navigate to datasets in BrightData dashboard",
            "5. Look for requests to api.brightdata.com",
            "6. Click on any data download/view buttons",
            "7. Document successful API calls:",
            "   - Request URL",
            "   - Request headers",
            "   - Response status",
            "   - Response data",
            "8. Right-click successful requests → 'Copy as cURL'",
            "9. Test cURL commands in terminal"
        ]
        
        for item in guide:
            print(f"   {item}")
    
    def create_findings_template(self):
        """Create a template for documenting findings."""
        template = f"""
# BRIGHTDATA DASHBOARD INVESTIGATION FINDINGS
=============================================

Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Investigator: [Your Name]

## SNAPSHOT STATUS
================
Snapshot ID: {self.snapshot_ids[0]}
- Status: [completed/processing/failed]
- Data Available: [yes/no]
- Download Option: [yes/no]
- Export Format: [CSV/JSON/other]

Snapshot ID: {self.snapshot_ids[1]}
- Status: [completed/processing/failed]
- Data Available: [yes/no]
- Download Option: [yes/no]
- Export Format: [CSV/JSON/other]

## API ENDPOINTS DISCOVERED
===========================
[Document any API calls made by the dashboard]

Example:
- URL: https://api.brightdata.com/[endpoint]
- Method: GET/POST
- Headers: [authentication headers]
- Response: [success/error]

## DASHBOARD CAPABILITIES
=========================
- Manual data export: [yes/no]
- Bulk download: [yes/no]
- Real-time access: [yes/no]
- Historical data: [yes/no]

## NEXT STEPS
=============
Based on findings:
1. [Action item 1]
2. [Action item 2]
3. [Action item 3]

## CURL COMMANDS TO TEST
========================
[Paste any cURL commands copied from browser dev tools]

"""
        
        filename = f"brightdata_investigation_findings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = f"C:\\Users\\winam\\OneDrive\\문서\\PREVIOUS\\TrackFutura - Copy\\{filename}"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(template)
            print(f"📄 Created findings template: {filename}")
            return filepath
        except Exception as e:
            print(f"❌ Error creating template: {e}")
            return None

def main():
    """Main investigation function."""
    investigator = BrightDataDashboardInvestigation()
    
    print("🚀 STARTING BRIGHTDATA DASHBOARD INVESTIGATION")
    print("=" * 55)
    print()
    
    # Show the investigation plan
    investigator.show_investigation_plan()
    
    # Create findings template
    template_path = investigator.create_findings_template()
    
    # Show network monitoring guide
    investigator.show_network_monitoring_guide()
    
    print("\n" + "=" * 55)
    print("🎯 READY TO INVESTIGATE!")
    print("=" * 55)
    
    # Ask if user wants to open dashboard
    response = input("\n🌐 Open BrightData dashboard now? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        investigator.open_dashboard()
        print("\n✅ Dashboard opened! Follow the investigation steps above.")
        print(f"📄 Document findings in: {template_path if template_path else 'manual file'}")
    else:
        print("\n📋 Manual URL: https://brightdata.com/cp")
        print("📄 Follow the investigation steps above")
    
    print("\n🔄 After investigation, run this script again to process findings.")

if __name__ == "__main__":
    main()