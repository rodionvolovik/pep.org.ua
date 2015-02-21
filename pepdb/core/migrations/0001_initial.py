# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='\u041f\u043e\u0432\u043d\u0430 \u043d\u0430\u0437\u0432\u0430')),
                ('state_company', models.BooleanField(default=True, verbose_name='\u0404 \u0434\u0435\u0440\u0436\u0430\u0432\u043d\u043e\u044e \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u043e\u044e')),
                ('edrpou', models.CharField(max_length=10, verbose_name='\u0404\u0414\u0420\u041f\u041e\u0423/\u0456\u0434\u0435\u043d\u0442\u0438\u0444\u0456\u043a\u0430\u0446\u0456\u0439\u043d\u0438\u0439 \u043a\u043e\u0434')),
                ('zip_code', models.CharField(max_length=10, verbose_name='\u0406\u043d\u0434\u0435\u043a\u0441', blank=True)),
                ('city', models.CharField(max_length=30, verbose_name='\u041c\u0456\u0441\u0442\u043e', blank=True)),
                ('street', models.CharField(max_length=50, verbose_name='\u0412\u0443\u043b\u0438\u0446\u044f', blank=True)),
                ('appt', models.CharField(max_length=10, verbose_name='\u2116 \u0431\u0443\u0434\u0438\u043d\u043a\u0443, \u043e\u0444\u0456\u0441\u0443', blank=True)),
                ('other_founders', models.TextField(help_text='\u0427\u0435\u0440\u0435\u0437 \u043a\u043e\u043c\u0443, \u043d\u0435 PEP', verbose_name='\u0406\u043d\u0448\u0438 \u0437\u0430\u0441\u043d\u043e\u0432\u043d\u0438\u043a\u0438', blank=True)),
                ('other_recipient', models.CharField(help_text='\u042f\u043a\u0449\u043e \u043d\u0435 \u0454 PEP\u043e\u043c', max_length=100, verbose_name='\u0411\u0435\u043d\u0435\u0444\u0456\u0446\u0456\u0430\u0440\u0456\u0439', blank=True)),
                ('other_owners', models.TextField(help_text='\u0427\u0435\u0440\u0435\u0437 \u043a\u043e\u043c\u0443, \u043d\u0435 PEP', verbose_name='\u0406\u043d\u0448\u0438 \u0432\u043b\u0430\u0441\u043d\u0438\u043a\u0438', blank=True)),
                ('other_managers', models.TextField(help_text='\u0427\u0435\u0440\u0435\u0437 \u043a\u043e\u043c\u0443, \u043d\u0435 PEP', verbose_name='\u0406\u043d\u0448\u0438 \u043a\u0435\u0440\u0443\u044e\u0447\u0456', blank=True)),
                ('bank_name', models.CharField(max_length=100, verbose_name='\u041d\u0430\u0437\u0432\u0430 \u0431\u0430\u043d\u043a\u0443', blank=True)),
            ],
            options={
                'verbose_name': '\u042e\u0440\u0456\u0434\u0438\u0447\u043d\u0430 \u043e\u0441\u043e\u0431\u0430',
                'verbose_name_plural': '\u042e\u0440\u0456\u0434\u0438\u0447\u043d\u0456 \u043e\u0441\u043e\u0431\u0438',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Company2Company',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_established', models.DateField(verbose_name="\u041a\u043e\u043b\u0438 \u043f\u043e\u0447\u0430\u0432\u0441\u044f \u0437\u0432'\u044f\u0437\u043e\u043a", blank=True)),
                ('date_finished', models.DateField(verbose_name="\u041a\u043e\u043b\u0438 \u0441\u043a\u0456\u043d\u0447\u0438\u0432\u0441\u044f \u0437\u0432'\u044f\u0437\u043e\u043a", blank=True)),
                ('proof', models.URLField(verbose_name="\u041f\u043e\u0441\u0438\u043b\u0430\u043d\u043d\u044f \u043d\u0430 \u0434\u043e\u043a\u0430\u0437 \u0437\u0432'\u044f\u0437\u043a\u0443", blank=True)),
                ('relationship_type', models.CharField(blank=True, max_length=30, verbose_name="\u0422\u0438\u043f \u0437\u0432'\u044f\u0437\u043a\u0443", choices=[('1', '\u0422\u0438\u043f 1'), ('2', '\u0422\u0438\u043f 2')])),
                ('from_company', models.ForeignKey(related_name='to_companies', to='core.Company')),
                ('to_company', models.ForeignKey(related_name='from_companies', to='core.Company')),
            ],
            options={
                'verbose_name': "\u0417\u0432'\u044f\u0437\u043e\u043a \u0437 \u043a\u043e\u043c\u043f\u0430\u043d\u0456\u0454\u044e",
                'verbose_name_plural': "\u0417\u0432'\u044f\u0437\u043a\u0438 \u0437 \u043a\u043e\u043c\u043f\u0430\u043d\u0456\u044f\u043c\u0438",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30, verbose_name='\u041d\u0430\u0437\u0432\u0430')),
                ('iso2', models.CharField(max_length=2, verbose_name='iso2 \u043a\u043e\u0434', blank=True)),
                ('iso3', models.CharField(max_length=3, verbose_name='iso3 \u043a\u043e\u0434', blank=True)),
                ('is_jurisdiction', models.BooleanField(default=False, verbose_name='\u041d\u0435 \u0454 \u0441\u0442\u0440\u0430\u043d\u043e\u044e')),
            ],
            options={
                'verbose_name': '\u041a\u0440\u0430\u0457\u043d\u0430/\u044e\u0440\u0456\u0441\u0434\u0438\u043a\u0446\u0456\u044f',
                'verbose_name_plural': '\u041a\u0440\u0430\u0457\u043d\u0438/\u044e\u0440\u0456\u0441\u0434\u0438\u043a\u0446\u0456\u0457',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('doc', models.FileField(upload_to=b'', verbose_name='\u0424\u0430\u0439\u043b')),
                ('uploaded', models.DateTimeField(auto_now=True, verbose_name='\u0411\u0443\u0432 \u0437\u0430\u0432\u0430\u043d\u0442\u0430\u0436\u0435\u043d\u0438\u0439')),
                ('source', models.CharField(max_length=255, verbose_name='\u041f\u0435\u0440\u0448\u043e\u0434\u0436\u0435\u0440\u0435\u043b\u043e', blank=True)),
                ('comments', models.TextField(verbose_name='\u041a\u043e\u043c\u0435\u043d\u0442\u0430\u0440\u0456')),
                ('uploader', models.ForeignKey(verbose_name='\u0425\u0442\u043e \u0437\u0430\u0432\u0430\u043d\u0442\u0430\u0436\u0438\u0432', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u0414\u043e\u043a\u0443\u043c\u0435\u043d\u0442',
                'verbose_name_plural': '\u0414\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u0438',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='\u041f\u0440\u0456\u0437\u0432\u0438\u0449\u0435')),
                ('first_name', models.CharField(max_length=30, verbose_name="\u0406\u043c'\u044f")),
                ('patronymic', models.CharField(max_length=30, verbose_name='\u041f\u043e-\u0431\u0430\u0442\u044c\u043a\u043e\u0432\u0456')),
                ('is_pep', models.BooleanField(default=True, verbose_name='\u0404 PEP\u043e\u043c')),
                ('photo', models.ImageField(upload_to=b'', verbose_name='\u0421\u0432\u0456\u0442\u043b\u0438\u043d\u0430', blank=True)),
                ('dob', models.DateField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u043d\u0430\u0440\u043e\u0434\u0436\u0435\u043d\u043d\u044f', blank=True)),
                ('city_of_birth', models.CharField(max_length=30, verbose_name='\u041c\u0456\u0441\u0442\u043e', blank=True)),
                ('registration', models.TextField(verbose_name='\u041e\u0444\u0456\u0446\u0456\u0439\u043d\u0435 \u043c\u0456\u0441\u0446\u0435 \u0440\u0435\u0454\u0441\u0442\u0440\u0430\u0446\u0456\u0457 (\u0432\u043d\u0443\u0442\u0440\u0456\u0448\u043d\u0435 \u043f\u043e\u043b\u0435)', blank=True)),
                ('passport_id', models.CharField(max_length=20, verbose_name='\u041f\u0430\u0441\u043f\u043e\u0440\u0442 \u0430\u0431\u043e \u0456\u043d\u0448\u0438\u0439 \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442 (\u0432\u043d\u0443\u0442\u0440\u0456\u0448\u043d\u0435 \u043f\u043e\u043b\u0435)', blank=True)),
                ('passport_reg', models.TextField(verbose_name='\u0414\u0430\u0442\u0430 \u0432\u0438\u0434\u0430\u0447\u0456 \u0442\u0430 \u043e\u0440\u0433\u0430\u043d (\u0432\u043d\u0443\u0442\u0440\u0456\u0448\u043d\u0435 \u043f\u043e\u043b\u0435)', blank=True)),
                ('tax_payer_id', models.CharField(max_length=30, verbose_name='\u041d\u043e\u043c\u0435\u0440 \u043a\u0430\u0440\u0442\u043a\u0438 \u043f\u043b\u0430\u0442\u043d\u0438\u043a\u0430 \u043f\u043e\u0434\u0430\u0442\u043a\u0456\u0432 (\u0432\u043d\u0443\u0442\u0440\u0456\u0448\u043d\u0435 \u043f\u043e\u043b\u0435)', blank=True)),
                ('id_number', models.CharField(max_length=10, verbose_name='\u0406\u0434\u0435\u043d\u0442\u0438\u0444\u0456\u043a\u0430\u0446\u0456\u0439\u043d\u0438\u0439 \u043d\u043e\u043c\u0435\u0440 (\u0432\u043d\u0443\u0442\u0440\u0456\u0448\u043d\u0435 \u043f\u043e\u043b\u0435)', blank=True)),
                ('reputation_sanctions', models.TextField(verbose_name='\u041d\u0430\u044f\u0432\u043d\u0456\u0441\u0442\u044c \u0441\u0430\u043d\u043a\u0446\u0456\u0439', blank=True)),
                ('reputation_crimes', models.TextField(verbose_name='\u041a\u0440\u0438\u043c\u0456\u043d\u0430\u043b\u044c\u043d\u0456 \u0432\u043f\u0440\u043e\u0432\u0430\u0434\u0436\u0435\u043d\u043d\u044f', blank=True)),
                ('reputation_manhunt', models.TextField(verbose_name='\u041f\u0435\u0440\u0435\u0431\u0443\u0432\u0430\u043d\u043d\u044f \u0443 \u0440\u043e\u0437\u0448\u0443\u043a\u0443', blank=True)),
                ('reputation_convictions', models.TextField(verbose_name='\u041d\u0430\u044f\u0432\u043d\u0456\u0441\u0442\u044c \u0441\u0443\u0434\u0438\u043c\u043e\u0441\u0442\u0456', blank=True)),
                ('wiki', models.TextField(verbose_name='\u0412\u0456\u043a\u0456-\u0441\u0442\u0430\u0442\u0442\u044f', blank=True)),
                ('names', models.TextField(verbose_name='\u0412\u0430\u0440\u0456\u0430\u043d\u0442\u0438 \u043d\u0430\u043f\u0438\u0441\u0430\u043d\u043d\u044f \u0456\u043c\u0435\u043d\u0456', blank=True)),
                ('type_of_official', models.IntegerField(blank=True, max_length=1, verbose_name='\u0422\u0438\u043f \u041f\u0415\u041f', choices=[(1, b'\xd0\x9d\xd0\xb0\xd1\x86\xd1\x96\xd0\xbe\xd0\xbd\xd0\xb0\xd0\xbb\xd1\x8c\xd0\xbd\xd0\xb8\xd0\xb9 \xd0\xbf\xd1\x83\xd0\xb1\xd0\xbb\xd1\x96\xd1\x87\xd0\xbd\xd0\xb8\xd0\xb9 \xd0\xb4\xd1\x96\xd1\x8f\xd1\x87'), (2, b'\xd0\x86\xd0\xbd\xd0\xbe\xd0\xb7\xd0\xb5\xd0\xbc\xd0\xbd\xd0\xb8\xd0\xb9 \xd0\xbf\xd1\x83\xd0\xb1\xd0\xbb\xd1\x96\xd1\x87\xd0\xbd\xd0\xb8\xd0\xb9 \xd0\xb4\xd1\x96\xd1\x8f\xd1\x87'), ('3', '\u0414\u0456\u044f\u0447, \u0449\u043e \u0432\u0438\u043a\u043e\u043d\u0443\u044e\u0454 \u0437\u043d\u0430\u0447\u043d\u0456 \u0444\u0443\u043d\u043a\u0446\u0456\u0457 \u0432 \u043c\u0456\u0436\u043d\u0430\u0440\u043e\u0434\u043d\u0456\u0439 \u043e\u0440\u0433\u0430\u043d\u0456\u0437\u0430\u0446\u0456\u0457'), (4, b"\xd0\x9f\xd0\xbe\xd0\xb2'\xd1\x8f\xd0\xb7\xd0\xb0\xd0\xbd\xd0\xb0 \xd0\xbe\xd1\x81\xd0\xbe\xd0\xb1\xd0\xb0"), (5, b'\xd0\x91\xd0\xbb\xd0\xb8\xd0\xb7\xd1\x8c\xd0\xba\xd0\xb0 \xd0\xbe\xd1\x81\xd0\xbe\xd0\xb1\xd0\xb0')])),
                ('risk_category', models.CharField(blank=True, max_length=6, verbose_name='\u0420\u0456\u0432\u0435\u043d\u044c \u0440\u0438\u0437\u0438\u043a\u0443', choices=[('high', '\u0412\u0438\u0441\u043e\u043a\u0438\u0439'), ('medium', '\u0421\u0435\u0440\u0435\u0434\u043d\u0456\u0439'), ('low', '\u041d\u0438\u0437\u044c\u043a\u0438\u0439')])),
                ('citizenship', models.ForeignKey(related_name='citizens', verbose_name='\u0413\u0440\u043e\u043c\u0430\u0434\u044f\u043d\u0441\u0442\u0432\u043e', blank=True, to='core.Country', null=True)),
                ('country_of_birth', models.ForeignKey(related_name='born_in', verbose_name='\u041a\u0440\u0430\u0457\u043d\u0430 \u043d\u0430\u0440\u043e\u0434\u0436\u0435\u043d\u043d\u044f', blank=True, to='core.Country', null=True)),
            ],
            options={
                'verbose_name': '\u0424\u0456\u0437\u0438\u0447\u043d\u0430 \u043e\u0441\u043e\u0431\u0430',
                'verbose_name_plural': '\u0424\u0456\u0437\u0438\u0447\u043d\u0456 \u043e\u0441\u043e\u0431\u0438',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Person2Company',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_established', models.DateField(verbose_name="\u041a\u043e\u043b\u0438 \u043f\u043e\u0447\u0430\u0432\u0441\u044f \u0437\u0432'\u044f\u0437\u043e\u043a", blank=True)),
                ('date_finished', models.DateField(verbose_name="\u041a\u043e\u043b\u0438 \u0441\u043a\u0456\u043d\u0447\u0438\u0432\u0441\u044f \u0437\u0432'\u044f\u0437\u043e\u043a", blank=True)),
                ('proof', models.URLField(verbose_name="\u041f\u043e\u0441\u0438\u043b\u0430\u043d\u043d\u044f \u043d\u0430 \u0434\u043e\u043a\u0430\u0437 \u0437\u0432'\u044f\u0437\u043a\u0443", blank=True)),
                ('relationship_type', models.CharField(blank=True, max_length=30, verbose_name="\u0422\u0438\u043f \u0437\u0432'\u044f\u0437\u043a\u0443", choices=[('1', '\u0422\u0438\u043f 1'), ('2', '\u0422\u0438\u043f 2')])),
                ('from_person', models.ForeignKey(to='core.Person')),
                ('to_company', models.ForeignKey(to='core.Company')),
            ],
            options={
                'verbose_name': "\u0417\u0432'\u044f\u0437\u043e\u043a \u0437 \u043a\u043e\u043c\u043f\u0430\u043d\u0456\u0454\u044e",
                'verbose_name_plural': "\u0417\u0432'\u044f\u0437\u043a\u0438 \u0437 \u043a\u043e\u043c\u043f\u0430\u043d\u0456\u044f\u043c\u0438",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Person2Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('relationship_type', models.CharField(blank=True, max_length=30, verbose_name="\u0422\u0438\u043f \u0437\u0432'\u044f\u0437\u043a\u0443", choices=[('1', '\u0422\u0438\u043f 1'), ('2', '\u0422\u0438\u043f 2')])),
                ('date_established', models.DateField(verbose_name="\u041a\u043e\u043b\u0438 \u043f\u043e\u0447\u0430\u0432\u0441\u044f \u0437\u0432'\u044f\u0437\u043e\u043a", blank=True)),
                ('date_finished', models.DateField(verbose_name="\u041a\u043e\u043b\u0438 \u0441\u043a\u0456\u043d\u0447\u0438\u0432\u0441\u044f \u0437\u0432'\u044f\u0437\u043e\u043a", blank=True)),
                ('proof', models.URLField(verbose_name="\u041f\u043e\u0441\u0438\u043b\u0430\u043d\u043d\u044f \u043d\u0430 \u0434\u043e\u043a\u0430\u0437 \u0437\u0432'\u044f\u0437\u043a\u0443", blank=True)),
                ('from_person', models.ForeignKey(related_name='to_persons', verbose_name='\u0412\u0456\u0434 \u043f\u0435\u0440\u0441\u043e\u043d\u0438', to='core.Person')),
                ('to_person', models.ForeignKey(related_name='from_persons', verbose_name='\u0414\u043e \u043f\u0435\u0440\u0441\u043e\u043d\u0438', to='core.Person')),
            ],
            options={
                'verbose_name': "\u0417\u0432'\u044f\u0437\u043e\u043a \u0437 \u0456\u043d\u0448\u043e\u044e \u043f\u0435\u0440\u0441\u043e\u043d\u043e\u044e",
                'verbose_name_plural': "\u0417\u0432'\u044f\u0437\u043a\u0438 \u0437 \u0456\u043d\u0448\u0438\u043c\u0438 \u043f\u0435\u0440\u0441\u043e\u043d\u0430\u043c\u0438",
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='person',
            name='related_companies',
            field=models.ManyToManyField(to='core.Company', through='core.Person2Company'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='related_persons',
            field=models.ManyToManyField(to='core.Person', through='core.Person2Person'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='company',
            name='related_companies',
            field=models.ManyToManyField(to='core.Company', through='core.Company2Company'),
            preserve_default=True,
        ),
    ]
