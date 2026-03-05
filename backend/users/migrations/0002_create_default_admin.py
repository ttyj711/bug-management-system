from django.db import migrations


def create_default_admin(apps, schema_editor):
    User = apps.get_model('users', 'User')
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123456',
            role='super_admin',
            status='active'
        )


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_admin),
    ]
