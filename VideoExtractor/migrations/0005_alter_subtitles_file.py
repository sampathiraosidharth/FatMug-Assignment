# Generated by Django 4.2.16 on 2024-09-21 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VideoExtractor', '0004_rename_language_subtitles_languages'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subtitles',
            name='file',
            field=models.TextField(),
        ),
    ]
