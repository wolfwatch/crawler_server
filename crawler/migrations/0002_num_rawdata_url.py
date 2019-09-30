# Generated by Django 2.2.5 on 2019-09-29 21:00

import crawler.models
from django.db import migrations, models
import djongo.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Num',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='RawData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('site', models.CharField(max_length=20)),
                ('board', djongo.models.fields.ArrayModelField(model_container=crawler.models.Post, model_form_class=crawler.models.PostForm)),
                ('post_num', djongo.models.fields.ArrayModelField(model_container=crawler.models.Num)),
                ('gallery_url', djongo.models.fields.ArrayModelField(model_container=crawler.models.Url)),
            ],
        ),
        migrations.CreateModel(
            name='Url',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.TextField()),
            ],
        ),
    ]
