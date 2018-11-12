# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("core", "0016_auto_20150409_2257")]

    operations = [
        migrations.AlterField(
            model_name="person2company",
            name="relationship_type",
            field=models.CharField(
                blank=True,
                max_length=60,
                verbose_name="\u0422\u0438\u043f \u0437\u0432'\u044f\u0437\u043a\u0443",
                choices=[
                    (
                        "\u041f\u0440\u0435\u0437\u0438\u0434\u0435\u043d\u0442",
                        "\u041f\u0440\u0435\u0437\u0438\u0434\u0435\u043d\u0442",
                    ),
                    (
                        "\u041f\u0440\u0435\u043c\u2019\u0454\u0440-\u043c\u0456\u043d\u0456\u0441\u0442\u0440",
                        "\u041f\u0440\u0435\u043c\u2019\u0454\u0440-\u043c\u0456\u043d\u0456\u0441\u0442\u0440",
                    ),
                    (
                        "\u041c\u0456\u043d\u0456\u0441\u0442\u0440",
                        "\u041c\u0456\u043d\u0456\u0441\u0442\u0440",
                    ),
                    (
                        "\u041f\u0435\u0440\u0448\u0438\u0439 \u0437\u0430\u0441\u0442\u0443\u043f\u043d\u0438\u043a \u043c\u0456\u043d\u0456\u0441\u0442\u0440\u0430",
                        "\u041f\u0435\u0440\u0448\u0438\u0439 \u0437\u0430\u0441\u0442\u0443\u043f\u043d\u0438\u043a \u043c\u0456\u043d\u0456\u0441\u0442\u0440\u0430",
                    ),
                    (
                        "\u0417\u0430\u0441\u0442\u0443\u043f\u043d\u0438\u043a \u043c\u0456\u043d\u0456\u0441\u0442\u0440\u0430",
                        "\u0417\u0430\u0441\u0442\u0443\u043f\u043d\u0438\u043a \u043c\u0456\u043d\u0456\u0441\u0442\u0440\u0430",
                    ),
                    (
                        "\u041a\u0435\u0440\u0456\u0432\u043d\u0438\u043a",
                        "\u041a\u0435\u0440\u0456\u0432\u043d\u0438\u043a",
                    ),
                    (
                        "\u041f\u0435\u0440\u0448\u0438\u0439 \u0437\u0430\u0441\u0442\u0443\u043f\u043d\u0438\u043a \u043a\u0435\u0440\u0456\u0432\u043d\u0438\u043a\u0430",
                        "\u041f\u0435\u0440\u0448\u0438\u0439 \u0437\u0430\u0441\u0442\u0443\u043f\u043d\u0438\u043a \u043a\u0435\u0440\u0456\u0432\u043d\u0438\u043a\u0430",
                    ),
                    (
                        "\u0417\u0430\u0441\u0442\u0443\u043f\u043d\u0438\u043a \u043a\u0435\u0440\u0456\u0432\u043d\u0438\u043a\u0430",
                        "\u0417\u0430\u0441\u0442\u0443\u043f\u043d\u0438\u043a \u043a\u0435\u0440\u0456\u0432\u043d\u0438\u043a\u0430",
                    ),
                    (
                        "\u041d\u0430\u0440\u043e\u0434\u043d\u0438\u0439 \u0434\u0435\u043f\u0443\u0442\u0430\u0442",
                        "\u041d\u0430\u0440\u043e\u0434\u043d\u0438\u0439 \u0434\u0435\u043f\u0443\u0442\u0430\u0442",
                    ),
                    (
                        "\u0413\u043e\u043b\u043e\u0432\u0430",
                        "\u0413\u043e\u043b\u043e\u0432\u0430",
                    ),
                    (
                        "\u0417\u0430\u0441\u0442\u0443\u043f\u043d\u0438\u043a \u0413\u043e\u043b\u043e\u0432\u0438",
                        "\u0417\u0430\u0441\u0442\u0443\u043f\u043d\u0438\u043a \u0413\u043e\u043b\u043e\u0432\u0438",
                    ),
                    (
                        "\u0427\u043b\u0435\u043d \u041f\u0440\u0430\u0432\u043b\u0456\u043d\u043d\u044f",
                        "\u0427\u043b\u0435\u043d \u041f\u0440\u0430\u0432\u043b\u0456\u043d\u043d\u044f",
                    ),
                    (
                        "\u0427\u043b\u0435\u043d \u0420\u0430\u0434\u0438",
                        "\u0427\u043b\u0435\u043d \u0420\u0430\u0434\u0438",
                    ),
                    (
                        "\u0421\u0443\u0434\u0434\u044f",
                        "\u0421\u0443\u0434\u0434\u044f",
                    ),
                    ("\u0427\u043b\u0435\u043d", "\u0427\u043b\u0435\u043d"),
                    (
                        "\u0413\u0435\u043d\u0435\u0440\u0430\u043b\u044c\u043d\u0438\u0439 \u043f\u0440\u043e\u043a\u0443\u0440\u043e\u0440",
                        "\u0413\u0435\u043d\u0435\u0440\u0430\u043b\u044c\u043d\u0438\u0439 \u043f\u0440\u043e\u043a\u0443\u0440\u043e\u0440",
                    ),
                    (
                        "\u0417\u0430\u0441\u0442\u0443\u043f\u043d\u0438\u043a \u0413\u0435\u043d\u0435\u0440\u0430\u043b\u044c\u043d\u043e\u0433\u043e \u043f\u0440\u043e\u043a\u0443\u0440\u043e\u0440\u0430",
                        "\u0417\u0430\u0441\u0442\u0443\u043f\u043d\u0438\u043a \u0413\u0435\u043d\u0435\u0440\u0430\u043b\u044c\u043d\u043e\u0433\u043e \u043f\u0440\u043e\u043a\u0443\u0440\u043e\u0440\u0430",
                    ),
                    (
                        "\u041d\u0430\u0434\u0437\u0432\u0438\u0447\u0430\u0439\u043d\u0438\u0439 \u0456 \u043f\u043e\u0432\u043d\u043e\u0432\u0430\u0436\u043d\u0438\u0439 \u043f\u043e\u0441\u043e\u043b",
                        "\u041d\u0430\u0434\u0437\u0432\u0438\u0447\u0430\u0439\u043d\u0438\u0439 \u0456 \u043f\u043e\u0432\u043d\u043e\u0432\u0430\u0436\u043d\u0438\u0439 \u043f\u043e\u0441\u043e\u043b",
                    ),
                    (
                        "\u0413\u043e\u043b\u043e\u0432\u043d\u043e\u043a\u043e\u043c\u0430\u043d\u0434\u0443\u0432\u0430\u0447",
                        "\u0413\u043e\u043b\u043e\u0432\u043d\u043e\u043a\u043e\u043c\u0430\u043d\u0434\u0443\u0432\u0430\u0447",
                    ),
                    (
                        "\u0421\u043b\u0443\u0436\u0431\u043e\u0432\u0435\u0446\u044c \u043f\u0435\u0440\u0448\u043e\u0457 \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0456\u0457 \u043f\u043e\u0441\u0430\u0434",
                        "\u0421\u043b\u0443\u0436\u0431\u043e\u0432\u0435\u0446\u044c \u043f\u0435\u0440\u0448\u043e\u0457 \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0456\u0457 \u043f\u043e\u0441\u0430\u0434",
                    ),
                    (
                        "\u0427\u043b\u0435\u043d \u0446\u0435\u043d\u0442\u0440\u0430\u043b\u044c\u043d\u043e\u0433\u043e \u0441\u0442\u0430\u0442\u0443\u0442\u043d\u043e\u0433\u043e \u043e\u0440\u0433\u0430\u043d\u0443",
                        "\u0427\u043b\u0435\u043d \u0446\u0435\u043d\u0442\u0440\u0430\u043b\u044c\u043d\u043e\u0433\u043e \u0441\u0442\u0430\u0442\u0443\u0442\u043d\u043e\u0433\u043e \u043e\u0440\u0433\u0430\u043d\u0443",
                    ),
                    (
                        "\u041f\u043e\u0432\u0456\u0440\u0435\u043d\u0438\u0439 \u0443 \u0441\u043f\u0440\u0430\u0432\u0430\u0445",
                        "\u041f\u043e\u0432\u0456\u0440\u0435\u043d\u0438\u0439 \u0443 \u0441\u043f\u0440\u0430\u0432\u0430\u0445",
                    ),
                    (
                        "\u0417\u0430\u0441\u043d\u043e\u0432\u043d\u0438\u043a/\u0443\u0447\u0430\u0441\u043d\u0438\u043a",
                        "\u0417\u0430\u0441\u043d\u043e\u0432\u043d\u0438\u043a/\u0443\u0447\u0430\u0441\u043d\u0438\u043a",
                    ),
                    (
                        "\u041a\u043e\u043b\u0438\u0448\u043d\u0456\u0439 \u0437\u0430\u0441\u043d\u043e\u0432\u043d\u0438\u043a/\u0443\u0447\u0430\u0441\u043d\u0438\u043a",
                        "\u041a\u043e\u043b\u0438\u0448\u043d\u0456\u0439 \u0437\u0430\u0441\u043d\u043e\u0432\u043d\u0438\u043a/\u0443\u0447\u0430\u0441\u043d\u0438\u043a",
                    ),
                    (
                        "\u0411\u0435\u043d\u0435\u0444\u0456\u0446\u0456\u0430\u0440\u043d\u0438\u0439 \u0432\u043b\u0430\u0441\u043d\u0438\u043a",
                        "\u0411\u0435\u043d\u0435\u0444\u0456\u0446\u0456\u0430\u0440\u043d\u0438\u0439 \u0432\u043b\u0430\u0441\u043d\u0438\u043a",
                    ),
                    (
                        "\u041d\u043e\u043c\u0456\u043d\u0430\u043b\u044c\u043d\u0438\u0439 \u0432\u043b\u0430\u0441\u043d\u0438\u043a",
                        "\u041d\u043e\u043c\u0456\u043d\u0430\u043b\u044c\u043d\u0438\u0439 \u0432\u043b\u0430\u0441\u043d\u0438\u043a",
                    ),
                    (
                        "\u041d\u043e\u043c\u0456\u043d\u0430\u043b\u044c\u043d\u0438\u0439 \u0434\u0438\u0440\u0435\u043a\u0442\u043e\u0440",
                        "\u041d\u043e\u043c\u0456\u043d\u0430\u043b\u044c\u043d\u0438\u0439 \u0434\u0438\u0440\u0435\u043a\u0442\u043e\u0440",
                    ),
                    (
                        "\u0424\u0456\u043d\u0430\u043d\u0441\u043e\u0432\u0456 \u0437\u0432'\u044f\u0437\u043a\u0438",
                        "\u0424\u0456\u043d\u0430\u043d\u0441\u043e\u0432\u0456 \u0437\u0432'\u044f\u0437\u043a\u0438",
                    ),
                    (
                        "\u0421\u0435\u043a\u0440\u0435\u0442\u0430\u0440",
                        "\u0421\u0435\u043a\u0440\u0435\u0442\u0430\u0440",
                    ),
                    (
                        "\u041a\u0435\u0440\u0443\u044e\u0447\u0438\u0439",
                        "\u041a\u0435\u0440\u0443\u044e\u0447\u0438\u0439",
                    ),
                ],
            ),
            preserve_default=True,
        )
    ]
