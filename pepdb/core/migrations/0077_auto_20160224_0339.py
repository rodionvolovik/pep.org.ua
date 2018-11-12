# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import redactor.fields


class Migration(migrations.Migration):

    dependencies = [("core", "0076_auto_20160223_0141")]

    operations = [
        migrations.AddField(
            model_name="company",
            name="sanctions",
            field=redactor.fields.RedactorField(
                verbose_name="\u0421\u0430\u043d\u043a\u0446\u0456\u0457", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="company",
            name="bank_name",
            field=redactor.fields.RedactorField(
                verbose_name="\u0424\u0456\u043d\u0430\u043d\u0441\u043e\u0432\u0430 \u0456\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0456\u044f",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="company",
            name="other_founders",
            field=redactor.fields.RedactorField(
                help_text="\u0427\u0435\u0440\u0435\u0437 \u043a\u043e\u043c\u0443, \u043d\u0435 PEP",
                verbose_name="\u0406\u043d\u0448\u0456 \u0437\u0430\u0441\u043d\u043e\u0432\u043d\u0438\u043a\u0438",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="company",
            name="other_managers",
            field=redactor.fields.RedactorField(
                help_text="\u0427\u0435\u0440\u0435\u0437 \u043a\u043e\u043c\u0443, \u043d\u0435 PEP",
                verbose_name="\u0406\u043d\u0448\u0456 \u043a\u0435\u0440\u0443\u044e\u0447\u0456",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="company",
            name="other_owners",
            field=redactor.fields.RedactorField(
                help_text="\u0427\u0435\u0440\u0435\u0437 \u043a\u043e\u043c\u0443, \u043d\u0435 PEP",
                verbose_name="\u0406\u043d\u0448\u0456 \u0432\u043b\u0430\u0441\u043d\u0438\u043a\u0438",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="company2country",
            name="from_company",
            field=models.ForeignKey(
                related_name="from_countries",
                verbose_name="\u041a\u043e\u043c\u043f\u0430\u043d\u0456\u044f",
                to="core.Company",
            ),
        ),
        migrations.AlterField(
            model_name="person2company",
            name="to_company",
            field=models.ForeignKey(
                related_name="from_persons",
                verbose_name="\u041a\u043e\u043c\u043f\u0430\u043d\u0456\u044f \u0430\u0431\u043e \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u0430",
                to="core.Company",
            ),
        ),
    ]
