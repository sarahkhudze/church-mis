from django.db import migrations, models


def populate_member_status(apps, schema_editor):
    Member = apps.get_model('members', 'Member')
    Member.objects.filter(is_active=False).update(member_status='left')
    Member.objects.filter(is_active=True).update(member_status='active')


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0002_member_marital_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='member_status',
            field=models.CharField(
                choices=[('active', 'Active'), ('left', 'Left'), ('deceased', 'Deceased')],
                default='active',
                help_text='Current membership status',
                max_length=20,
            ),
        ),
        migrations.RunPython(populate_member_status, migrations.RunPython.noop),
    ]
