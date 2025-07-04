# Generated by Django 5.2.3 on 2025-06-30 19:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('revisions', models.IntegerField()),
                ('delivery_time_in_days', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('features', models.JSONField(default=list)),
                ('offer_type', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('business_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_orders', to=settings.AUTH_USER_MODEL)),
                ('customer_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer_orders', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
