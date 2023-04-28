# Generated by Django 4.2 on 2023-04-26 22:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amazon', '0003_userinfo_delete_users'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=64)),
                ('price', models.DecimalField(decimal_places=2, max_digits=6)),
            ],
        ),
    ]
