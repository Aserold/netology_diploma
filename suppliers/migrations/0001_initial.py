# Generated by Django 5.0.2 on 2024-03-05 17:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
            ],
            options={
                'ordering': ('-name',),
            },
        ),
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
            ],
            options={
                'ordering': ('-name',),
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(db_index=True, max_length=255, unique=True)),
                ('first_name', models.CharField(max_length=240)),
                ('last_name', models.CharField(max_length=240)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_superuser', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_groups', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_permissions', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'ordering': ('email',),
            },
        ),
        migrations.CreateModel(
            name='ConfirmEmailToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='When was this token generated')),
                ('key', models.CharField(db_index=True, max_length=64, unique=True, verbose_name='Key')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='confirm_email_tokens', to=settings.AUTH_USER_MODEL, verbose_name='The User which is associated to this password reset token')),
            ],
            options={
                'verbose_name': 'Email verification token',
                'verbose_name_plural': 'Email verification token list',
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=50, verbose_name='Type')),
                ('value', models.CharField(max_length=128)),
                ('user', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('cart', 'In cart'), ('new', 'New'), ('confirmed', 'Confirmed'), ('assembled', 'Assembled'), ('sent', 'Sent'), ('delivered', 'Delivered'), ('canceled', 'Canceled')], max_length=15, verbose_name='Status')),
                ('contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='suppliers.contact', verbose_name='Contact')),
                ('user', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='order', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'ordering': ('-time_created',),
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('category', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='suppliers.category')),
            ],
            options={
                'ordering': ('-name',),
            },
        ),
        migrations.CreateModel(
            name='ProductInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('quantity', models.PositiveIntegerField(verbose_name='Quantity')),
                ('price', models.PositiveIntegerField(verbose_name='Price')),
                ('price_rrp', models.PositiveIntegerField(verbose_name='Recommended price')),
                ('product', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_info', to='suppliers.product')),
            ],
            options={
                'verbose_name': 'Product information',
                'verbose_name_plural': 'Product information list',
            },
        ),
        migrations.CreateModel(
            name='ProductParameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=128)),
                ('parameter', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_parameters', to='suppliers.parameter')),
                ('product_info', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_parameters', to='suppliers.productinfo')),
            ],
        ),
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('url', models.URLField()),
                ('state', models.BooleanField(default=True, verbose_name='Is active')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'ordering': ('-name',),
            },
        ),
        migrations.AddField(
            model_name='productinfo',
            name='shop',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_info', to='suppliers.shop'),
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordered_items', to='suppliers.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordered_items', to='suppliers.product')),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordered_items', to='suppliers.shop')),
            ],
        ),
        migrations.AddField(
            model_name='category',
            name='shops',
            field=models.ManyToManyField(blank=True, related_name='categories', to='suppliers.shop'),
        ),
        migrations.AddConstraint(
            model_name='productinfo',
            constraint=models.UniqueConstraint(fields=('product', 'shop'), name='unique_product_info'),
        ),
    ]
