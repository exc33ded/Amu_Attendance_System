# Generated by Django 5.1.2 on 2025-04-06 19:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0010_alter_enrollstudent_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attendance',
            options={'ordering': ['-date', '-marked_at']},
        ),
        migrations.RenameField(
            model_name='attendance',
            old_name='timestamp',
            new_name='marked_at',
        ),
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.course'),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.student'),
        ),
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together={('course', 'student', 'date', 'marked_at')},
        ),
    ]
