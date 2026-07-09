from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cell_groups', '0003_cellgroup_approval_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='cellgroup',
            name='zone_name',
            field=models.CharField(blank=True, help_text='Zone this cell group belongs to', max_length=100, null=True),
        ),
    ]
