# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [("wagtailcore", "0010_change_page_owner_to_null_on_delete")]

    operations = [
        migrations.CreateModel(
            name="StaticPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.Page",
                    ),
                ),
                ("body", wagtail.wagtailcore.fields.RichTextField()),
            ],
            options={
                "verbose_name": "\u0421\u0442\u0430\u0442\u0438\u0447\u043d\u0430 \u0441\u0442\u043e\u0440\u0456\u043d\u043a\u0430"
            },
            bases=("wagtailcore.page",),
        )
    ]
