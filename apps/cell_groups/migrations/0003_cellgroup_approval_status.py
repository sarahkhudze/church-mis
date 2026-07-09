from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cell_groups', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cellgroup',
            name='approval_status',
            field=models.CharField(
                choices=[('pending', 'Pending Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')],
                default='approved',
                help_text='Whether this cell group has been approved for use',
                max_length=20,
            ),
        ),
    ]
