# Generated by Django 3.0.3 on 2020-03-02 23:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('librarian', '0005_auto_20200302_1824'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='author',
            field=models.CharField(max_length=60),
        ),
    ]