# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import wagtail.wagtailcore.fields
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0005_make_filter_spec_unique'),
        ('wagtailcore', '0010_change_page_owner_to_null_on_delete'),
        ('cms_pages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomePage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
            ],
            options={
                'verbose_name': '\u0413\u043e\u043b\u043e\u0432\u043d\u0430 \u0441\u0442\u043e\u0440\u0456\u043d\u043a\u0430',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='HomePageBannerItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort_order', models.IntegerField(null=True, editable=False, blank=True)),
                ('caption', models.CharField(max_length=255, blank=True)),
                ('link_external', models.URLField(verbose_name=b'External link', blank=True)),
                ('image', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='wagtailimages.Image', null=True)),
                ('link_page', models.ForeignKey(related_name='+', blank=True, to='wagtailcore.Page', null=True)),
                ('page', modelcluster.fields.ParentalKey(related_name='banner_items', to='cms_pages.HomePage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HomePageBottomMenuLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort_order', models.IntegerField(null=True, editable=False, blank=True)),
                ('caption', models.CharField(max_length=255, blank=True)),
                ('link_external', models.URLField(verbose_name=b'External link', blank=True)),
                ('link_page', models.ForeignKey(related_name='+', blank=True, to='wagtailcore.Page', null=True)),
                ('page', modelcluster.fields.ParentalKey(related_name='bottom_menu_links', to='cms_pages.HomePage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HomePageTopMenuLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort_order', models.IntegerField(null=True, editable=False, blank=True)),
                ('caption', models.CharField(max_length=255, blank=True)),
                ('link_external', models.URLField(verbose_name=b'External link', blank=True)),
                ('link_page', models.ForeignKey(related_name='+', blank=True, to='wagtailcore.Page', null=True)),
                ('page', modelcluster.fields.ParentalKey(related_name='top_menu_links', to='cms_pages.HomePage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='staticpage',
            name='body',
            field=wagtail.wagtailcore.fields.RichTextField(verbose_name=b'\xd0\xa2\xd0\xb5\xd0\xba\xd1\x81\xd1\x82 \xd1\x81\xd1\x82\xd0\xbe\xd1\x80\xd1\x96\xd0\xbd\xd0\xba\xd0\xb8'),
            preserve_default=True,
        ),
    ]
