# Generated by Django 5.2 on 2025-04-25 13:26

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user_management', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgricultureProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('unit_of_measure', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('current_market_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('price_last_updated', models.DateField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='BoosterCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'Booster Categories',
            },
        ),
        migrations.CreateModel(
            name='AgricultureCollection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_value', models.DecimalField(decimal_places=2, max_digits=12)),
                ('collection_date', models.DateField(default=django.utils.timezone.now)),
                ('collection_location', models.CharField(max_length=100)),
                ('quality_grade', models.CharField(blank=True, max_length=20, null=True)),
                ('receipt_number', models.CharField(max_length=50, unique=True)),
                ('payment_status', models.CharField(choices=[('PENDING', 'Pending'), ('PARTIAL', 'Partially Paid'), ('PAID', 'Fully Paid')], default='PENDING', max_length=20)),
                ('amount_paid', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('notes', models.TextField(blank=True, null=True)),
                ('is_synced', models.BooleanField(default=True)),
                ('offline_created_at', models.DateTimeField(blank=True, null=True)),
                ('collected_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='user_management.fieldofficer')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_management.member')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boosters.agricultureproduct')),
            ],
        ),
        migrations.CreateModel(
            name='SchoolFeesCollection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_name', models.CharField(max_length=100)),
                ('student_id', models.CharField(blank=True, max_length=50, null=True)),
                ('relation_to_member', models.CharField(max_length=50)),
                ('school_name', models.CharField(max_length=100)),
                ('education_level', models.CharField(choices=[('PRIMARY', 'Primary School'), ('SECONDARY', 'Secondary School'), ('COLLEGE', 'College'), ('UNIVERSITY', 'University'), ('OTHER', 'Other')], max_length=20)),
                ('academic_year', models.CharField(max_length=20)),
                ('term', models.CharField(choices=[('TERM1', 'Term 1'), ('TERM2', 'Term 2'), ('TERM3', 'Term 3'), ('SEMESTER1', 'Semester 1'), ('SEMESTER2', 'Semester 2'), ('YEARLY', 'Full Year'), ('OTHER', 'Other')], max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('collection_date', models.DateField(default=django.utils.timezone.now)),
                ('receipt_number', models.CharField(max_length=50, unique=True)),
                ('payment_method', models.CharField(max_length=50)),
                ('is_complete_payment', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True, null=True)),
                ('is_synced', models.BooleanField(default=True)),
                ('offline_created_at', models.DateTimeField(blank=True, null=True)),
                ('collected_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='user_management.fieldofficer')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_management.member')),
            ],
        ),
        migrations.CreateModel(
            name='BoosterPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_type', models.CharField(choices=[('AGRICULTURE', 'Agriculture Collection Payment'), ('SCHOOL_FEES', 'School Fees Reimbursement'), ('OTHER', 'Other Booster Payment')], max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('payment_date', models.DateField(default=django.utils.timezone.now)),
                ('payment_method', models.CharField(max_length=50)),
                ('reference_number', models.CharField(max_length=50, unique=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('is_synced', models.BooleanField(default=True)),
                ('offline_created_at', models.DateTimeField(blank=True, null=True)),
                ('agriculture_collection', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='boosters.agriculturecollection')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_management.member')),
                ('processed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='user_management.fieldofficer')),
                ('school_fees_collection', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='boosters.schoolfeescollection')),
            ],
        ),
    ]
