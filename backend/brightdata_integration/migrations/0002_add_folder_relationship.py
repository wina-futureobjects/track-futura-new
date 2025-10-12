"""
Migration to add proper folder relationship to BrightDataScraperRequest
"""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('track_accounts', '0001_initial'),  # Adjust based on your latest track_accounts migration
        ('brightdata_integration', '0001_initial'),  # Adjust based on your latest brightdata migration
    ]

    operations = [
        migrations.AddField(
            model_name='brightdatascraperrequest',
            name='run_folder',
            field=models.ForeignKey(
                blank=True, 
                null=True, 
                on_delete=django.db.models.deletion.CASCADE, 
                related_name='scraper_requests',
                to='track_accounts.unifiedrunfolder',
                help_text='Associated job folder for this scrape request'
            ),
        ),
        
        # Add index for better query performance
        migrations.AddIndex(
            model_name='brightdatascraperrequest',
            index=models.Index(fields=['run_folder', 'scrape_number'], name='bd_run_folder_scrape_idx'),
        ),
    ]