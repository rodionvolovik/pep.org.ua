# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0089_auto_20160726_0238'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.CharField(max_length=30, verbose_name='\u0414\u0456\u044f')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='\u0411\u0443\u0432 \u0437\u0430\u0432\u0430\u043d\u0442\u0430\u0436\u0435\u043d\u0438\u0439')),
                ('details', models.TextField(verbose_name='\u0414\u0435\u0442\u0430\u043b\u0456', blank=True)),
                ('user', models.ForeignKey(verbose_name='\u041a\u043e\u0440\u0438\u0441\u0442\u0443\u0432\u0430\u0447', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u0414\u0456\u044f \u043a\u043e\u0440\u0438\u0441\u0442\u0443\u0432\u0430\u0447\u0430',
                'verbose_name_plural': '\u0414\u0456\u0457 \u043a\u043e\u0440\u0438\u0441\u0442\u0443\u0432\u0430\u0447\u0456\u0432',
            },
        ),
        migrations.AlterIndexTogether(
            name='actionlog',
            index_together=set([('user', 'action', 'timestamp')]),
        ),
    ]
