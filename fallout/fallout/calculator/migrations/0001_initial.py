# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-09 18:09


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='County',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, verbose_name='County Name')),
                ('has_map', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['state', 'name'],
                'verbose_name_plural': 'counties',
            },
        ),
        migrations.CreateModel(
            name='MappedCountyRegion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, verbose_name='County Region Name')),
                ('county', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='calculator.County', verbose_name='County')),
            ],
            options={
                'ordering': ['county', 'name'],
            },
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('abbreviation', models.CharField(db_index=True, max_length=2, verbose_name='State Abbreviation')),
                ('name', models.CharField(max_length=100, verbose_name='State Name')),
            ],
            options={
                'ordering': ['name', 'abbreviation'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='state',
            unique_together=set([('abbreviation', 'name')]),
        ),
        migrations.AddField(
            model_name='county',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='calculator.State', verbose_name='State'),
        ),
        migrations.AlterUniqueTogether(
            name='mappedcountyregion',
            unique_together=set([('name', 'county')]),
        ),
        migrations.AlterUniqueTogether(
            name='county',
            unique_together=set([('name', 'state')]),
        ),
    ]
