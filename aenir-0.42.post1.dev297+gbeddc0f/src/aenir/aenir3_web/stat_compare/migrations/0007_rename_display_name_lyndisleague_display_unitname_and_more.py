# Generated by Django 4.2.7 on 2023-12-03 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stat_compare', '0006_rename_display_name_fireemblemgame_display_gamename_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lyndisleague',
            old_name='display_name',
            new_name='display_unitname',
        ),
        migrations.RemoveField(
            model_name='lyndisleague',
            name='will_inherit',
        ),
        migrations.AlterField(
            model_name='fireemblemgenealogy',
            name='game_num',
            field=models.PositiveSmallIntegerField(),
        ),
        migrations.AlterField(
            model_name='fireemblemgenealogy',
            name='unit_name',
            field=models.CharField(max_length=50, primary_key=True, serialize=False),
        ),
    ]