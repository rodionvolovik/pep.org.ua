# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import redactor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0085_auto_20160418_0327'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='appt_en',
            field=models.CharField(max_length=50, null=True, verbose_name='\u2116 \u0431\u0443\u0434\u0438\u043d\u043a\u0443, \u043e\u0444\u0456\u0441\u0443', blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='appt_uk',
            field=models.CharField(max_length=50, null=True, verbose_name='\u2116 \u0431\u0443\u0434\u0438\u043d\u043a\u0443, \u043e\u0444\u0456\u0441\u0443', blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='bank_name_en',
            field=redactor.fields.RedactorField(null=True, verbose_name='\u0424\u0456\u043d\u0430\u043d\u0441\u043e\u0432\u0430 \u0456\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0456\u044f', blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='bank_name_uk',
            field=redactor.fields.RedactorField(null=True, verbose_name='\u0424\u0456\u043d\u0430\u043d\u0441\u043e\u0432\u0430 \u0456\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0456\u044f', blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='city_en',
            field=models.CharField(max_length=255, null=True, verbose_name='\u041c\u0456\u0441\u0442\u043e', blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='city_uk',
            field=models.CharField(max_length=255, null=True, verbose_name='\u041c\u0456\u0441\u0442\u043e', blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='other_founders_en',
            field=redactor.fields.RedactorField(help_text='\u0427\u0435\u0440\u0435\u0437 \u043a\u043e\u043c\u0443, \u043d\u0435 PEP', null=True, verbose_name='\u0406\u043d\u0448\u0456 \u0437\u0430\u0441\u043d\u043e\u0432\u043d\u0438\u043a\u0438', blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='other_founders_uk',
            field=redactor.fields.RedactorField(help_text='\u0427\u0435\u0440\u0435\u0437 \u043a\u043e\u043c\u0443, \u043d\u0435 PEP', null=True, verbose_name='\u0406\u043d\u0448\u0456 \u0437\u0430\u0441\u043d\u043e\u0432\u043d\u0438\u043a\u0438', blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='other_managers_en',
            field=redactor.fields.RedactorField(help_text='\u0427\u0435\u0440\u0435\u0437 \u043a\u043e\u043c\u0443, \u043d\u0435 PEP', null=True, verbose_name='\u0406\u043d\u0448\u0456 \u043a\u0435\u0440\u0443\u044e\u0447\u0456', blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='other_managers_uk',
            field=redactor.fields.RedactorField(help_text='\u0427\u0435\u0440\u0435\u0437 \u043a\u043e\u043c\u0443, \u043d\u0435 PEP', null=True, verbose_name='\u0406\u043d\u0448\u0456 \u043a\u0435\u0440\u0443\u044e\u0447\u0456', blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='other_owners_en',
            field=redactor.fields.RedactorField(help_text='\u0427\u0435\u0440\u0435\u0437 \u043a\u043e\u043c\u0443, \u043d\u0435 PEP', null=True, verbose_name='\u0406\u043d\u0448\u0456 \u0432\u043b\u0430\u0441\u043d\u0438\u043a\u0438', blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='other_owners_uk',
            field=redactor.fields.RedactorField(help_text='\u0427\u0435\u0440\u0435\u0437 \u043a\u043e\u043c\u0443, \u043d\u0435 PEP', null=True, verbose_name='\u0406\u043d\u0448\u0456 \u0432\u043b\u0430\u0441\u043d\u0438\u043a\u0438', blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='other_recipient_en',
            field=models.CharField(help_text='\u042f\u043a\u0449\u043e \u043d\u0435 \u0454 PEP\u043e\u043c', max_length=200, null=True, verbose_name='\u0411\u0435\u043d\u0435\u0444\u0456\u0446\u0456\u0430\u0440\u0456\u0439', blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='other_recipient_uk',
            field=models.CharField(help_text='\u042f\u043a\u0449\u043e \u043d\u0435 \u0454 PEP\u043e\u043c', max_length=200, null=True, verbose_name='\u0411\u0435\u043d\u0435\u0444\u0456\u0446\u0456\u0430\u0440\u0456\u0439', blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='sanctions_en',
            field=redactor.fields.RedactorField(null=True, verbose_name='\u0421\u0430\u043d\u043a\u0446\u0456\u0457', blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='sanctions_uk',
            field=redactor.fields.RedactorField(null=True, verbose_name='\u0421\u0430\u043d\u043a\u0446\u0456\u0457', blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='street_en',
            field=models.CharField(max_length=100, null=True, verbose_name='\u0412\u0443\u043b\u0438\u0446\u044f', blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='street_uk',
            field=models.CharField(max_length=100, null=True, verbose_name='\u0412\u0443\u043b\u0438\u0446\u044f', blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='wiki_en',
            field=redactor.fields.RedactorField(null=True, verbose_name='\u0412\u0456\u043a\u0456-\u0441\u0442\u0430\u0442\u0442\u044f', blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='wiki_uk',
            field=redactor.fields.RedactorField(null=True, verbose_name='\u0412\u0456\u043a\u0456-\u0441\u0442\u0430\u0442\u0442\u044f', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='related_companies',
            field=models.ManyToManyField(to='core.Company', through='core.Person2Company'),
        ),
    ]
