# Generated by Django 3.0.3 on 2020-03-02 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('librarian', '0003_auto_20200302_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='title',
            field=models.CharField(max_length=150),
        ),
    ]
