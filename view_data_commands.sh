# View all your scraped posts
upsun ssh -p inhoolfrqniuu -e main --app trackfutura 'cd backend && python manage.py shell -c "from brightdata_integration.models import BrightDataScrapedPost; [print(f\"{p.created_at}: {p.platform} - {p.content[:100]}...\") for p in BrightDataScrapedPost.objects.all()[:10]]"'

# Check webhook events
upsun ssh -p inhoolfrqniuu -e main --app trackfutura 'cd backend && python manage.py shell -c "from brightdata_integration.models import BrightDataWebhookEvent; [print(f\"{e.created_at}: {e.platform} - {e.status}\") for e in BrightDataWebhookEvent.objects.all()[:5]]"'

# Database direct query
upsun ssh -p inhoolfrqniuu -e main --app trackfutura 'psql -c "SELECT COUNT(*) as total_posts, platform FROM brightdata_integration_brightdatascrapedpost GROUP BY platform;"'