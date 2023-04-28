# Generated by Django 4.2 on 2023-04-27 03:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('amazon', '0005_cart_cartitem_cart_products'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='placeorder',
            name='count',
        ),
        migrations.RemoveField(
            model_name='placeorder',
            name='description',
        ),
        migrations.RemoveField(
            model_name='placeorder',
            name='item_id',
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='quantity',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.PositiveIntegerField(default=0)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='amazon.placeorder')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='amazon.product')),
            ],
        ),
        migrations.AddField(
            model_name='placeorder',
            name='items',
            field=models.ManyToManyField(blank=True, through='amazon.OrderItem', to='amazon.product'),
        ),
    ]