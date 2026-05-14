from datetime import datetime
from django.db import migrations
from django.utils import timezone


def seed_data(apps, schema_editor):
    Author = apps.get_model('app', 'Author')
    Blog = apps.get_model('app', 'Blog')

    Author.objects.create(first_name='Alice', last_name='Johnson', email='alice@example.com')
    Author.objects.create(first_name='Bob', last_name='Smith', email='bob@example.com')
    Author.objects.create(first_name='Charlie', last_name='Brown', email='charlie@example.com')
    Author.objects.create(first_name='Diana', last_name='Prince', email='diana@example.com')
    Author.objects.create(first_name='Eve', last_name='Davis', email='eve@example.com')

    alice = Author.objects.get(email='alice@example.com')
    bob = Author.objects.get(email='bob@example.com')
    charlie = Author.objects.get(email='charlie@example.com')
    diana = Author.objects.get(email='diana@example.com')
    eve = Author.objects.get(email='eve@example.com')

    blog_data = [
        (alice, 'My Travel Adventures',
         'Exploring the hidden gems of Southeast Asia was an unforgettable experience. From bustling markets to serene temples, every day brought a new adventure.',
         datetime(2026, 5, 1, 10, 0, 0)),
        (bob, 'Tech Trends in 2026',
         'Artificial intelligence continues to dominate the tech landscape. This year we are seeing unprecedented advances in machine learning and automation.',
         datetime(2026, 5, 3, 14, 30, 0)),
        (charlie, 'Healthy Living Tips',
         'Maintaining a balanced diet and regular exercise routine is key to a healthy lifestyle. Small consistent changes lead to big results over time.',
         datetime(2026, 5, 5, 8, 15, 0)),
        (diana, 'Photography for Beginners',
         'Getting started with photography does not require expensive gear. Learn to master composition, lighting, and storytelling with any camera you have.',
         datetime(2026, 5, 7, 16, 45, 0)),
        (eve, 'The Future of Renewable Energy',
         'Solar and wind energy are becoming more accessible than ever. Innovations in battery storage are paving the way for a sustainable future.',
         datetime(2026, 5, 10, 12, 0, 0)),
    ]
    for author, title, content, pub_date in blog_data:
        Blog.objects.create(
            author=author, title=title, content=content,
            published_date=timezone.make_aware(pub_date)
        )


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_data),
    ]
