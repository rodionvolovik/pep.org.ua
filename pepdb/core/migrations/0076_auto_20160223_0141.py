# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import redactor.fields


class Migration(migrations.Migration):

    dependencies = [("core", "0075_auto_20160216_0357")]

    operations = [
        migrations.RemoveField(model_name="person", name="related_companies"),
        migrations.AlterField(
            model_name="company",
            name="wiki",
            field=redactor.fields.RedactorField(
                verbose_name="\u0412\u0456\u043a\u0456-\u0441\u0442\u0430\u0442\u0442\u044f",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="reputation_assets",
            field=redactor.fields.RedactorField(
                verbose_name="\u041c\u0430\u0439\u043d\u043e", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="reputation_assets_en",
            field=redactor.fields.RedactorField(
                null=True, verbose_name="\u041c\u0430\u0439\u043d\u043e", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="reputation_assets_uk",
            field=redactor.fields.RedactorField(
                null=True, verbose_name="\u041c\u0430\u0439\u043d\u043e", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="reputation_convictions",
            field=redactor.fields.RedactorField(
                verbose_name="\u041d\u0430\u044f\u0432\u043d\u0456\u0441\u0442\u044c \u0441\u0443\u0434\u0438\u043c\u043e\u0441\u0442\u0456",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="reputation_convictions_en",
            field=redactor.fields.RedactorField(
                null=True,
                verbose_name="\u041d\u0430\u044f\u0432\u043d\u0456\u0441\u0442\u044c \u0441\u0443\u0434\u0438\u043c\u043e\u0441\u0442\u0456",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="reputation_convictions_uk",
            field=redactor.fields.RedactorField(
                null=True,
                verbose_name="\u041d\u0430\u044f\u0432\u043d\u0456\u0441\u0442\u044c \u0441\u0443\u0434\u0438\u043c\u043e\u0441\u0442\u0456",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="reputation_crimes",
            field=redactor.fields.RedactorField(
                verbose_name="\u041a\u0440\u0438\u043c\u0456\u043d\u0430\u043b\u044c\u043d\u0456 \u0432\u043f\u0440\u043e\u0432\u0430\u0434\u0436\u0435\u043d\u043d\u044f",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="reputation_crimes_en",
            field=redactor.fields.RedactorField(
                null=True,
                verbose_name="\u041a\u0440\u0438\u043c\u0456\u043d\u0430\u043b\u044c\u043d\u0456 \u0432\u043f\u0440\u043e\u0432\u0430\u0434\u0436\u0435\u043d\u043d\u044f",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="reputation_crimes_uk",
            field=redactor.fields.RedactorField(
                null=True,
                verbose_name="\u041a\u0440\u0438\u043c\u0456\u043d\u0430\u043b\u044c\u043d\u0456 \u0432\u043f\u0440\u043e\u0432\u0430\u0434\u0436\u0435\u043d\u043d\u044f",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="reputation_manhunt",
            field=redactor.fields.RedactorField(
                verbose_name="\u041f\u0435\u0440\u0435\u0431\u0443\u0432\u0430\u043d\u043d\u044f \u0443 \u0440\u043e\u0437\u0448\u0443\u043a\u0443",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="reputation_manhunt_en",
            field=redactor.fields.RedactorField(
                null=True,
                verbose_name="\u041f\u0435\u0440\u0435\u0431\u0443\u0432\u0430\u043d\u043d\u044f \u0443 \u0440\u043e\u0437\u0448\u0443\u043a\u0443",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="reputation_manhunt_uk",
            field=redactor.fields.RedactorField(
                null=True,
                verbose_name="\u041f\u0435\u0440\u0435\u0431\u0443\u0432\u0430\u043d\u043d\u044f \u0443 \u0440\u043e\u0437\u0448\u0443\u043a\u0443",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="reputation_sanctions",
            field=redactor.fields.RedactorField(
                verbose_name="\u041d\u0430\u044f\u0432\u043d\u0456\u0441\u0442\u044c \u0441\u0430\u043d\u043a\u0446\u0456\u0439",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="reputation_sanctions_en",
            field=redactor.fields.RedactorField(
                null=True,
                verbose_name="\u041d\u0430\u044f\u0432\u043d\u0456\u0441\u0442\u044c \u0441\u0430\u043d\u043a\u0446\u0456\u0439",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="reputation_sanctions_uk",
            field=redactor.fields.RedactorField(
                null=True,
                verbose_name="\u041d\u0430\u044f\u0432\u043d\u0456\u0441\u0442\u044c \u0441\u0430\u043d\u043a\u0446\u0456\u0439",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="wiki",
            field=redactor.fields.RedactorField(
                verbose_name="\u0412\u0456\u043a\u0456-\u0441\u0442\u0430\u0442\u0442\u044f",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="wiki_en",
            field=redactor.fields.RedactorField(
                null=True,
                verbose_name="\u0412\u0456\u043a\u0456-\u0441\u0442\u0430\u0442\u0442\u044f",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="wiki_uk",
            field=redactor.fields.RedactorField(
                null=True,
                verbose_name="\u0412\u0456\u043a\u0456-\u0441\u0442\u0430\u0442\u0442\u044f",
                blank=True,
            ),
        ),
    ]
