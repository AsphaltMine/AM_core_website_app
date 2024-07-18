from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core_website_app", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="accountrequest",
            name="organization",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.AddField(
            model_name="accountrequest",
            name="country",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="accountrequest",
            name="standard",
            field=models.CharField(blank=True, default="", max_length=30),
        ),
        migrations.AddField(
            model_name="accountrequest",
            name="standard_other",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.AddField(
            model_name="accountrequest",
            name="reason",
            field=models.TextField(blank=True, default=""),
        ),
    ]
