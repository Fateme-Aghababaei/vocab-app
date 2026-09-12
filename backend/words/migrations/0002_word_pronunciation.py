from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("words", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="word",
            name="pronunciation",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
    ]
