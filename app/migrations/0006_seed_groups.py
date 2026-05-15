from django.db import migrations


def create_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    admin_group, _ = Group.objects.get_or_create(name='Admin')
    author_group, _ = Group.objects.get_or_create(name='Author')

    # Grant all permissions to Admin group
    all_perms = Permission.objects.all()
    admin_group.permissions.add(*all_perms)

    # Grant add/change blog permissions to Author group
    blog_perms = Permission.objects.filter(
        content_type__app_label='app',
        content_type__model='blog',
        codename__in=['add_blog', 'change_blog', 'view_blog']
    )
    author_group.permissions.add(*blog_perms)


def remove_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['Admin', 'Author']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_blog_image'),
    ]

    operations = [
        migrations.RunPython(create_groups, remove_groups),
    ]
