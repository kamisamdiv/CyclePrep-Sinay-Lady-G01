from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='last_reminder_for',
            field=models.DateField(blank=True, editable=False, null=True),
        ),
    ]
