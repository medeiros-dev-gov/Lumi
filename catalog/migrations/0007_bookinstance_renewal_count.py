# Generated by Django 5.1.3 on 2024-11-28 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_alter_book_isbn_alter_bookinstance_id_borrowedbook'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookinstance',
            name='renewal_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
