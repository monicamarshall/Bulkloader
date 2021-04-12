# Generated by Django 2.2.10 on 2021-04-11 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Speaker',
            fields=[
                ('speaker_id', models.AutoField(primary_key=True, serialize=False)),
                ('first_name', models.TextField()),
                ('last_name', models.TextField()),
                ('title', models.TextField()),
                ('company', models.TextField()),
                ('speaker_bio', models.TextField()),
                ('speaker_photo', models.BinaryField(blank=True, default=None, null=True)),
            ],
            options={
                'db_table': 'speakers',
                'ordering': ('speaker_id',),
            },
        ),
    ]