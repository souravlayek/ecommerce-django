# Generated by Django 3.0.8 on 2020-07-11 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_item_discount_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='description',
            field=models.TextField(default='this is a demo description'),
            preserve_default=False,
        ),
    ]