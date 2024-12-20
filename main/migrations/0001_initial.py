# Generated by Django 4.2.16 on 2024-11-12 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TablaCorrespondencias',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lexema', models.CharField(max_length=100, unique=True)),
                ('token', models.IntegerField(blank=True, choices=[(0, 'POSITIVO'), (1, 'NEGATIVO'), (2, 'PROHIBIDO'), (3, 'SALUDO'), (4, 'DESPEDIDA'), (5, 'IDENTIFICACION')], max_length=10)),
                ('ponderacion', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Texto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto', models.TextField()),
            ],
        ),
    ]