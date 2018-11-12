# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("core", "0010_auto_20150311_0249")]

    operations = [
        migrations.AlterField(
            model_name="person",
            name="patronymic",
            field=models.CharField(
                max_length=30,
                verbose_name="\u041f\u043e-\u0431\u0430\u0442\u044c\u043a\u043e\u0432\u0456",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="person2country",
            name="relationship_type",
            field=models.CharField(
                max_length=30,
                verbose_name="\u0422\u0438\u043f \u0437\u0432'\u044f\u0437\u043a\u0443",
                choices=[
                    (
                        "born_in",
                        "\u041d\u0430\u0440\u043e\u0434\u0438\u0432\u0441\u044f(-\u043b\u0430\u0441\u044c)",
                    ),
                    (
                        "registered_in",
                        "\u0417\u0430\u0440\u0435\u0454\u0441\u0442\u0440\u043e\u0432\u0430\u043d\u0438\u0439(-\u0430)",
                    ),
                    (
                        "lived_in",
                        "\u041f\u0440\u043e\u0436\u0438\u0432\u0430\u0432(-\u043b\u0430)",
                    ),
                    (
                        "citizenship",
                        "\u0413\u0440\u043e\u043c\u0430\u0434\u044f\u043d\u0438\u043d(-\u043a\u0430)",
                    ),
                    (
                        "business",
                        "\u041c\u0430\u0454 \u0437\u0430\u0440\u0435\u0454\u0441\u0442\u0440\u043e\u0432\u0430\u043d\u0438\u0439 \u0431\u0456\u0437\u043d\u0435\u0441",
                    ),
                ],
            ),
            preserve_default=True,
        ),
    ]
