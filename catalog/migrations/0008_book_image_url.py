# Generated by Django 5.1.3 on 2024-11-28 23:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0007_bookinstance_renewal_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='image_url',
            field=models.ImageField(blank=True, null=True, upload_to='book_covers/'),
        ),
    ]
