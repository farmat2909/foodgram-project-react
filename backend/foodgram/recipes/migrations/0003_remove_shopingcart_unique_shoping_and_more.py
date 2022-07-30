# Generated by Django 4.0.5 on 2022-07-30 17:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='shopingcart',
            name='unique_shoping',
        ),
        migrations.AlterField(
            model_name='shopingcart',
            name='recipe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='shopping_cart', to='recipes.recipe'),
        ),
        migrations.AlterField(
            model_name='shopingcart',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='shopping_cart', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='shopingcart',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_shopping'),
        ),
    ]