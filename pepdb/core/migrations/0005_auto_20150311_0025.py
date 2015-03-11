# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20150227_0258'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company2Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_established', models.DateField(null=True, verbose_name="\u041a\u043e\u043b\u0438 \u043f\u043e\u0447\u0430\u0432\u0441\u044f \u0437\u0432'\u044f\u0437\u043e\u043a", blank=True)),
                ('date_finished', models.DateField(null=True, verbose_name="\u041a\u043e\u043b\u0438 \u0441\u043a\u0456\u043d\u0447\u0438\u0432\u0441\u044f \u0437\u0432'\u044f\u0437\u043e\u043a", blank=True)),
                ('proof_title', models.CharField(help_text='\u041d\u0430\u043f\u0440\u0438\u043a\u043b\u0430\u0434: \u0432\u0438\u0442\u044f\u0433', max_length=100, verbose_name="\u041d\u0430\u0437\u0432\u0430 \u0434\u043e\u043a\u0430\u0437\u0443 \u0437\u0432'\u044f\u0437\u043a\u0443", blank=True)),
                ('proof', models.URLField(verbose_name="\u041f\u043e\u0441\u0438\u043b\u0430\u043d\u043d\u044f \u043d\u0430 \u0434\u043e\u043a\u0430\u0437 \u0437\u0432'\u044f\u0437\u043a\u0443", blank=True)),
                ('relationship_type', models.CharField(max_length=30, verbose_name="\u0422\u0438\u043f \u0437\u0432'\u044f\u0437\u043a\u0443", choices=[('registered_in', '\u0417\u0430\u0440\u0435\u0454\u0441\u0442\u0440\u043e\u0432\u0430\u043d\u0430')])),
                ('from_company', models.ForeignKey(verbose_name='\u041a\u043e\u043c\u043f\u0430\u043d\u0456\u044f', to='core.Company')),
                ('to_country', models.ForeignKey(verbose_name='\u041a\u0440\u0430\u0457\u043d\u0430', to='core.Country')),
            ],
            options={
                'verbose_name': "\u0417\u0432'\u044f\u0437\u043e\u043a \u0437 \u043a\u0440\u0430\u0457\u043d\u043e\u044e",
                'verbose_name_plural': "\u0417\u0432'\u044f\u0437\u043a\u0438 \u0437 \u043a\u0440\u0430\u0457\u043d\u0430\u043c\u0438",
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='document',
            name='name_en',
            field=models.CharField(max_length=255, null=True, verbose_name='\u041b\u044e\u0434\u0441\u044c\u043a\u0430 \u043d\u0430\u0437\u0432\u0430'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='document',
            name='name_ua',
            field=models.CharField(max_length=255, null=True, verbose_name='\u041b\u044e\u0434\u0441\u044c\u043a\u0430 \u043d\u0430\u0437\u0432\u0430'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='company',
            name='other_founders',
            field=models.TextField(help_text='\u0427\u0435\u0440\u0435\u0437 \u043a\u043e\u043c\u0443, \u043d\u0435 PEP', verbose_name='\u0406\u043d\u0448\u0456 \u0437\u0430\u0441\u043d\u043e\u0432\u043d\u0438\u043a\u0438', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='company',
            name='other_managers',
            field=models.TextField(help_text='\u0427\u0435\u0440\u0435\u0437 \u043a\u043e\u043c\u0443, \u043d\u0435 PEP', verbose_name='\u0406\u043d\u0448\u0456 \u043a\u0435\u0440\u0443\u044e\u0447\u0456', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='company',
            name='other_owners',
            field=models.TextField(help_text='\u0427\u0435\u0440\u0435\u0437 \u043a\u043e\u043c\u0443, \u043d\u0435 PEP', verbose_name='\u0406\u043d\u0448\u0456 \u0432\u043b\u0430\u0441\u043d\u0438\u043a\u0438', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='company2company',
            name='relationship_type',
            field=models.CharField(blank=True, max_length=30, verbose_name="\u0422\u0438\u043f \u0437\u0432'\u044f\u0437\u043a\u0443", choices=[('\u0412\u043b\u0430\u0441\u043d\u0438\u043a', '\u0412\u043b\u0430\u0441\u043d\u0438\u043a'), ('\u0421\u043f\u0456\u0432\u0432\u043b\u0430\u0441\u043d\u0438\u043a', '\u0421\u043f\u0456\u0432\u0432\u043b\u0430\u0441\u043d\u0438\u043a'), ('\u0421\u043f\u043e\u0440\u0456\u0434\u043d\u0435\u043d\u0430', '\u0421\u043f\u043e\u0440\u0456\u0434\u043d\u0435\u043d\u0430'), ('\u041a\u0440\u0435\u0434\u0438\u0442\u043e\u0440 (\u0444\u0456\u043d\u0430\u043d\u0441\u043e\u0432\u0438\u0439 \u043f\u0430\u0440\u0442\u043d\u0435\u0440)', '\u041a\u0440\u0435\u0434\u0438\u0442\u043e\u0440 (\u0444\u0456\u043d\u0430\u043d\u0441\u043e\u0432\u0438\u0439 \u043f\u0430\u0440\u0442\u043d\u0435\u0440)'), ('\u041d\u0430\u0434\u0430\u0432\u0430\u0447 \u043f\u0440\u043e\u0444\u0435\u0441\u0456\u0439\u043d\u0438\u0445 \u043f\u043e\u0441\u043b\u0443\u0433', '\u041d\u0430\u0434\u0430\u0432\u0430\u0447 \u043f\u0440\u043e\u0444\u0435\u0441\u0456\u0439\u043d\u0438\u0445 \u043f\u043e\u0441\u043b\u0443\u0433')]),
            preserve_default=True,
        ),
    ]
