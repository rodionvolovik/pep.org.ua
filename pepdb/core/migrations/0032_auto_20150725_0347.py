# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("core", "0031_auto_20150506_0326")]

    operations = [
        migrations.AlterField(
            model_name="person",
            name="type_of_official",
            field=models.IntegerField(
                blank=True,
                null=True,
                verbose_name="\u0422\u0438\u043f \u041f\u0415\u041f",
                choices=[
                    (
                        1,
                        b"\xd0\x9d\xd0\xb0\xd1\x86\xd1\x96\xd0\xbe\xd0\xbd\xd0\xb0\xd0\xbb\xd1\x8c\xd0\xbd\xd0\xb8\xd0\xb9 \xd0\xbf\xd1\x83\xd0\xb1\xd0\xbb\xd1\x96\xd1\x87\xd0\xbd\xd0\xb8\xd0\xb9 \xd0\xb4\xd1\x96\xd1\x8f\xd1\x87",
                    ),
                    (
                        2,
                        b"\xd0\x86\xd0\xbd\xd0\xbe\xd0\xb7\xd0\xb5\xd0\xbc\xd0\xbd\xd0\xb8\xd0\xb9 \xd0\xbf\xd1\x83\xd0\xb1\xd0\xbb\xd1\x96\xd1\x87\xd0\xbd\xd0\xb8\xd0\xb9 \xd0\xb4\xd1\x96\xd1\x8f\xd1\x87",
                    ),
                    (
                        3,
                        "\u0414\u0456\u044f\u0447, \u0449\u043e \u0432\u0438\u043a\u043e\u043d\u0443\u044e\u0454 \u0437\u043d\u0430\u0447\u043d\u0456 \u0444\u0443\u043d\u043a\u0446\u0456\u0457 \u0432 \u043c\u0456\u0436\u043d\u0430\u0440\u043e\u0434\u043d\u0456\u0439 \u043e\u0440\u0433\u0430\u043d\u0456\u0437\u0430\u0446\u0456\u0457",
                    ),
                    (
                        4,
                        b"\xd0\x9f\xd0\xbe\xd0\xb2'\xd1\x8f\xd0\xb7\xd0\xb0\xd0\xbd\xd0\xb0 \xd0\xbe\xd1\x81\xd0\xbe\xd0\xb1\xd0\xb0",
                    ),
                    (
                        5,
                        b"\xd0\x91\xd0\xbb\xd0\xb8\xd0\xb7\xd1\x8c\xd0\xba\xd0\xb0 \xd0\xbe\xd1\x81\xd0\xbe\xd0\xb1\xd0\xb0",
                    ),
                ],
            ),
        )
    ]
