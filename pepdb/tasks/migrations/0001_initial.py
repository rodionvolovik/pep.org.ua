# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0093_declaration_nacp_declaration'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonDeduplication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0442\u0430 \u0447\u0430\u0441')),
                ('person1', models.ForeignKey(related_name='task_ent_1', verbose_name='\u041f\u0435\u0440\u0441\u043e\u043d\u0430 1', to='core.Person')),
                ('person2', models.ForeignKey(related_name='task_ent_2', verbose_name='\u041f\u0435\u0440\u0441\u043e\u043d\u0430 2', to='core.Person')),
                ('user', models.ForeignKey(verbose_name='\u041a\u043e\u0440\u0438\u0441\u0442\u0443\u0432\u0430\u0447', blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u0414\u0443\u0431\u043b\u0456\u043a\u0430\u0442 \u0444\u0456\u0437\u0438\u0447\u043d\u0438\u0445 \u043e\u0441\u0456\u0431',
                'verbose_name_plural': '\u0414\u0443\u0431\u043b\u0456\u043a\u0430\u0442\u0438 \u0444\u0456\u0437\u0438\u0447\u043d\u0438\u0445 \u043e\u0441\u0456\u0431',
            },
        ),
    ]
