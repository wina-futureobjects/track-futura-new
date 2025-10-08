from datetime import datetime, timedelta

# Simulate what our system should do
today = datetime.now()
print(f'Today: {today.strftime("%Y-%m-%d")}')

# What our system should generate
default_end = today - timedelta(days=2)  # 2 days ago
default_start = default_end - timedelta(days=30)  # 30 days before

print(f'System should generate:')
print(f'Start: {default_start.strftime("%d-%m-%Y")}')
print(f'End: {default_end.strftime("%d-%m-%Y")}')

# Check if the user input dates would be adjusted
user_start = datetime(2025, 10, 1)
user_end = datetime(2025, 10, 8)

print(f'\nUser input dates:')
print(f'Start: {user_start.strftime("%d-%m-%Y")}')
print(f'End: {user_end.strftime("%d-%m-%Y")}')

if user_end.date() >= today.date():
    print('❌ End date is today/future - should be adjusted!')
    adjusted_end = today - timedelta(days=1)
    print(f'Should adjust to: {adjusted_end.strftime("%d-%m-%Y")}')
else:
    print('✅ End date is in the past')

print('\n🎯 WORKING EXAMPLE FROM BRIGHTDATA:')
print('01-09-2025,30-09-2025 (September dates - all in past)')
print('\n❌ FAILING EXAMPLE:') 
print('01-10-2025,08-10-2025 (October 8 is TODAY - causes discovery error)')