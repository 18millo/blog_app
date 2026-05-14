from django.db import migrations


def remove_seed_blogs(apps, schema_editor):
    Blog = apps.get_model('app', 'Blog')
    Blog.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_author_user'),
    ]

    operations = [
        migrations.RunPython(remove_seed_blogs),
    ]
