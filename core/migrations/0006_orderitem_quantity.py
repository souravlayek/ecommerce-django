# Generated by Django 3.0.8 on 2020-07-11 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_item_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
    ]
