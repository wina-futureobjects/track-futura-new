# Generated manually for scrape_number field addition

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brightdata_integration', '0004_brightdatascrapedpost'),
    ]

    operations = [
        migrations.AddField(
            model_name='brightdatascraperrequest',
            name='scrape_number',
            field=models.IntegerField(default=1, help_text='Incremental scrape number for this folder'),
        ),
        migrations.AddIndex(
            model_name='brightdatascraperrequest',
            index=models.Index(fields=['folder_id', 'scrape_number'], name='brightdata__folder__scrape_idx'),
        ),
    ]
