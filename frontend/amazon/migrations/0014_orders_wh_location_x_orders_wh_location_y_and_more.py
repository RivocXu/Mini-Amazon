# Generated by Django 4.2 on 2023-04-28 02:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amazon', '0013_alter_orders_wh_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='wh_location_x',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='orders',
            name='wh_location_y',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='orders',
            name='wh_id',
            field=models.IntegerField(null=True),
        ),
        migrations.DeleteModel(
            name='Warehouse',
        ),
    ]
