from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_customuser_application_reason_customuser_approved_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='zone_name',
            field=models.CharField(blank=True, help_text='Zone assigned to this zone leader', max_length=100, null=True),
        ),
    ]
