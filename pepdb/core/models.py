# coding: utf-8
from __future__ import unicode_literals
from django.db import models

from django.db.models import Q
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.utils import formats
from django.core.urlresolvers import reverse

import select2.fields
import select2.models
from django_markdown.models import MarkdownField


# to_*_dict methods are used to convert two main entities that we have, Person
# and Company into document indexable by ElasticSearch.
# Links between Persons, Person and Company, Companies, Person and Country,
# Company and Country is also converted to subdocuments and attached to
# Person/Company documents. Because Person and Company needs different
# subdocuments, Person2Company has two different methods, to_person_dict and
# to_company_dict. For the same reason Person2Person and Company2Company has
# to_dict/to_dict_reverse because same link provides info to both persons.


class Person(models.Model):
    last_name = models.CharField("Прізвище", max_length=30)
    first_name = models.CharField("Ім'я", max_length=30)
    patronymic = models.CharField("По-батькові", max_length=30, blank=True)

    publish = models.BooleanField("Опублікувати", default=False)
    is_pep = models.BooleanField("Є PEPом", default=True)

    photo = models.ImageField("Світлина", blank=True, upload_to="images")
    dob = models.DateField("Дата народження", blank=True, null=True)
    dob_details = models.IntegerField(
        "Дата народження: точність",
        choices=(
            (0, "Точна дата"),
            (1, "Рік та місяць"),
            (2, "Тільки рік"),
        ),
        default=0)

    city_of_birth = models.CharField(
        "Місто народження", max_length=100, blank=True)
    registration = models.TextField(
        "Офіційне місце реєстрації (внутрішне поле)", blank=True)

    related_countries = models.ManyToManyField(
        "Country", verbose_name="Пов'язані країни",
        through="Person2Country", related_name="people")

    passport_id = models.CharField(
        "Паспорт або інший документ (внутрішне поле)", max_length=20,
        blank=True)
    passport_reg = models.TextField(
        "Дата видачі та орган (внутрішне поле)", blank=True)
    tax_payer_id = models.CharField(
        "Номер картки платника податків (внутрішне поле)", max_length=30,
        blank=True)
    id_number = models.CharField(
        "Ідентифікаційний номер (внутрішне поле)", max_length=10,
        blank=True)

    reputation_assets = MarkdownField(
        "Майно", blank=True)

    reputation_sanctions = MarkdownField(
        "Наявність санкцій", blank=True)
    reputation_crimes = MarkdownField(
        "Кримінальні впровадження", blank=True)
    reputation_manhunt = MarkdownField(
        "Перебування у розшуку", blank=True)
    reputation_convictions = MarkdownField(
        "Наявність судимості", blank=True)

    related_persons = select2.fields.ManyToManyField(
        "self", through="Person2Person", symmetrical=False,
        ajax=True,
        search_field=(
            lambda q: Q(last_name__icontains=q) | Q(first_name__icontains=q)))

    related_companies = models.ManyToManyField(
        "Company", through="Person2Company")

    wiki = MarkdownField("Вікі-стаття", blank=True)
    names = models.TextField("Варіанти написання імені", blank=True)

    type_of_official = models.IntegerField(
        "Тип ПЕП",
        choices=(
            (1, "Національний публічний діяч"),
            (2, "Іноземний публічний діяч"),
            (3,
             "Діяч, що виконуює значні функції в міжнародній організації"),
            (4, "Пов'язана особа"),
            (5, "Близька особа"),
        ),
        blank=True,
        null=True)

    risk_category = models.CharField(
        "Рівень ризику",
        choices=(
            ("high", "Високий"),
            ("medium", "Середній"),
            ("low", "Низький"),
        ),
        max_length=6, default="low")

    hash = models.CharField("Хеш", max_length=40, blank=True)

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "last_name__icontains", "first_name__icontains")

    def __unicode__(self):
        return "%s %s %s" % (self.last_name, self.first_name, self.patronymic)

    @property
    def date_of_birth(self):
        if not self.dob:
            return ""

        if self.dob_details == 0:
            return formats.date_format(self.dob, "DATE_FORMAT")
        elif self.dob_details == 1:
            return formats.date_format(
                self.dob, "MONTH_YEAR_DATE_FORMAT")
        elif self.dob_details == 2:
            return formats.date_format(self.dob, "YEAR_DATE_FORMAT")

    @property
    def last_workplace(self):
        qs = self.person2company_set.filter(
            is_employee=True, date_finished__exact=None)

        if not qs:
            qs = self.person2company_set.filter(
                is_employee=True).order_by("-date_finished")
        if not qs:
            qs = self.person2company_set.filter(
                is_employee=False, date_finished__exact=None)
        if not qs:
            qs = self.person2company_set.filter(
                is_employee=False).order_by("-date_finished")

        if qs:
            l = qs[0]
            return "%s, %s" % (l.to_company, l.relationship_type)

        return ""

    @property
    def workplaces(self):
        timeline = []

        for p2c in self.person2company_set.select_related("to_company").filter(
                is_employee=True):
            if p2c.date_established:
                timeline.append((p2c.date_established, "from", p2c))
            if p2c.date_finished:
                timeline.append((p2c.date_finished, "to", p2c))
            if p2c.date_established is None and p2c.date_finished is None:
                timeline.append(None, None, p2c)

        timeline.sort(key=lambda x: 1000000.
                      if x[0] is None else x[0].toordinal() +
                      (0.5 if x[1] == "to" else 0.0))

        return timeline

    @property
    def assets(self):
        return self.person2company_set.select_related("to_company").filter(
            is_employee=False,
            relationship_type__in=["Засновник/учасник",
                                   "Колишній засновник/учасник",
                                   "Бенефіціарний власник",
                                   "Номінальний власник",])

    @property
    def all_related_persons(self):
        related_persons = [
            (i.to_relationship_type, i.to_person)
            for i in self.to_persons.select_related("to_person")] + [
            (i.from_relationship_type, i.from_person)
            for i in self.from_persons.select_related("from_person")
        ]

        res = {
            "family": [],
            "personal": [],
            "business": [],
            "all": []
        }

        for rtp, p in related_persons:
            p.rtype = rtp

            if rtp in ["особисті зв'язки"]:
                res["personal"].append(p)
            elif rtp in ["ділові зв'язки"]:
                res["business"].append(p)
            else:
                res["family"].append(p)

            res["all"].append(p)

        return res

    @property
    def parsed_names(self):
        return filter(None, self.names.split("\n"))

    def to_dict(self):
        """
        Convert Person model to an indexable presentation for ES.
        """
        d = model_to_dict(self, fields=[
            "id", "last_name", "first_name", "patronymic", "dob",
            "dob_details", "city_of_birth", "is_pep", "wiki",
            "reputation_sanctions", "reputation_convictions",
            "reputation_crimes", "reputation_manhunt", "names"])

        d["related_persons"] = [
            i.to_dict()
            for i in self.to_persons.select_related("to_person")] + [
            i.to_dict_reverse()
            for i in self.from_persons.select_related("from_person")
        ]
        d["related_countries"] = [
            i.to_dict()
            for i in self.person2country_set.select_related("to_country")]
        d["related_companies"] = [
            i.to_company_dict()
            for i in self.person2company_set.select_related("to_company")]

        d["photo"] = self.photo.name if self.photo else ""
        d["date_of_birth"] = self.date_of_birth
        d["last_workplace"] = self.last_workplace
        d["type_of_official"] = self.get_type_of_official_display()
        d["risk_category"] = self.get_risk_category_display()
        d["full_name"] = ("%s %s %s" % (self.first_name, self.patronymic,
                                        self.last_name)).replace("  ", " ")

        d["full_name_suggest"] = {
            "input": [
                " ".join([d["last_name"], d["first_name"],
                          d["patronymic"]]),
                " ".join([d["first_name"],
                          d["patronymic"],
                          d["last_name"]]),
                " ".join([d["first_name"],
                          d["last_name"]])
            ],
            "output": d["full_name"]
        }

        d["_id"] = d["id"]

        return d

    def get_absolute_url(self):
        return reverse("person_details", kwargs={"person_id": self.pk})

    class Meta:
        verbose_name = "Фізична особа"
        verbose_name_plural = "Фізичні особи"

        index_together = [
            ["last_name", "first_name"],
        ]


class Person2Person(models.Model):
    _relationships_explained = {
        "чоловік": ["дружина"],
        "дружина": ["чоловік"],
        "батько": ["син", "дочка"],
        "мати": ["син", "дочка"],
        "вітчим": ["пасинок", "падчерка"],
        "мачуха": ["пасинок", "падчерка"],
        "син": ["батько", "мати"],
        "дочка": ["батько", "мати"],
        "пасинок": ["вітчим", "мачуха"],
        "падчерка": ["вітчим", "мачуха"],
        "рідний брат": ["рідна сестра", "рідний брат"],
        "рідна сестра": ["рідна сестра", "рідний брат"],
        "дід": ["внук", "внучка"],
        "баба": ["внук", "внучка"],
        "прадід": ["правнук", "правнучка"],
        "прабаба": ["правнук", "правнучка"],
        "внук": ["дід", "баба"],
        "внучка": ["дід", "баба"],
        "правнук": ["прадід", "прабаба"],
        "правнучка": ["прадід", "прабаба"],
        "усиновлювач": ["усиновлений"],
        "усиновлений": ["усиновлювач"],
        "опікун чи піклувальник": [
            "особа, яка перебуває під опікою або піклуванням"],
        "особа, яка перебуває під опікою або піклуванням": [
            "опікун чи піклувальник"],
        "особи, які спільно проживають": ["особи, які спільно проживають"],
        "пов'язані спільним побутом і мають взаємні права та обов'язки": [
            "пов'язані спільним побутом і мають взаємні права та обов'язки"],
        "ділові зв'язки": ["ділові зв'язки"],
        "особисті зв'язки": ["особисті зв'язки"]
    }

    from_person = models.ForeignKey(
        "Person", verbose_name="Персона 1", related_name="to_persons")
    to_person = models.ForeignKey(
        "Person", verbose_name="Персона 2", related_name="from_persons")

    from_relationship_type = models.CharField(
        "Персона 1 є",
        choices=(zip(_relationships_explained.keys(),
                     _relationships_explained.keys())),
        max_length=100,
        blank=True)

    to_relationship_type = models.CharField(
        "Персона 2 є",
        choices=(zip(_relationships_explained.keys(),
                     _relationships_explained.keys())),
        max_length=100,
        blank=True)

    date_established = models.DateField(
        "Зв'язок почався", blank=True, null=True)
    date_finished = models.DateField(
        "Зв'язок скінчився", blank=True, null=True)
    date_confirmed = models.DateField(
        "Підтверджено", blank=True, null=True)

    proof_title = models.TextField(
        "Назва доказу зв'язку", blank=True,
        help_text="Наприклад: склад ВР 7-го скликання")
    proof = models.TextField("Посилання на доказ зв'язку", blank=True)

    def __unicode__(self):
        return "%s (%s) -> %s (%s)" % (
            self.from_person, self.get_from_relationship_type_display(),
            self.to_person, self.get_to_relationship_type_display())

    def to_dict(self):
        """
        Convert link between two persons into indexable presentation
        """
        return {
            "relationship_type": self.to_relationship_type,
            "is_pep": self.to_person.is_pep,
            "person": "%s %s %s" % (
                self.to_person.first_name,
                self.to_person.patronymic,
                self.to_person.last_name)
        }

    def to_dict_reverse(self):
        """
        Convert back link between two persons to indexable presentation
        """
        return {
            "relationship_type": self.from_relationship_type,
            "is_pep": self.from_person.is_pep,
            "person": "%s %s %s" % (
                self.from_person.first_name,
                self.from_person.patronymic,
                self.from_person.last_name)
        }

    class Meta:
        verbose_name = "Зв'язок з іншою персоною"
        verbose_name_plural = "Зв'язки з іншими персонами"


class Person2Company(models.Model):
    _relationships_explained = [
        "Президент",
        "Прем’єр-міністр",
        "Міністр",
        "Перший заступник міністра",
        "Заступник міністра",
        "Керівник",
        "Перший заступник керівника",
        "Заступник керівника",
        "Народний депутат",
        "Голова",
        "Заступник Голови",
        "Член Правління",
        "Член Ради",
        "Суддя",
        "Член",
        "Генеральний прокурор",
        "Заступник Генерального прокурора",
        "Надзвичайний і повноважний посол",
        "Головнокомандувач",
        "Службовець першої категорії посад",
        "Член центрального статутного органу",
        "Повірений у справах",
        "Засновник/учасник",
        "Колишній засновник/учасник",
        "Бенефіціарний власник",
        "Номінальний власник",
        "Номінальний директор",
        "Фінансові зв'язки",
        "Секретар",
        "Керуючий"
    ]

    from_person = models.ForeignKey("Person")
    to_company = models.ForeignKey(
        "Company", verbose_name="Компанія або установа")

    date_established = models.DateField(
        "Зв'язок почався", blank=True, null=True)
    date_finished = models.DateField(
        "Зв'язок скінчився", blank=True, null=True)
    date_confirmed = models.DateField(
        "Підтверджено", blank=True, null=True)

    proof_title = models.TextField(
        "Назва доказу зв'язку", blank=True,
        help_text="Наприклад: склад ВР 7-го скликання")
    proof = models.TextField(
        "Посилання на доказ зв'язку", blank=True, max_length=250)

    relationship_type = models.TextField(
        "Тип зв'язку",
        blank=True)

    is_employee = models.BooleanField(
        "Працює(-вав)",
        default=False
    )

    def __unicode__(self):
        return "%s (%s)" % (
            self.to_company, self.relationship_type)

    def to_company_dict(self):
        return {
            "relationship_type": self.relationship_type,
            "state_company": self.to_company.state_company,
            "to_company": self.to_company.name,
            "to_company_short": self.to_company.short_name
        }

    def to_person_dict(self):
        return {
            "relationship_type": self.relationship_type,
            "is_pep": self.from_person.is_pep,
            "name": "%s %s %s" % (self.from_person.first_name,
                                  self.from_person.patronymic,
                                  self.from_person.last_name)
        }

    class Meta:
        verbose_name = "Зв'язок з компанією/установою"
        verbose_name_plural = "Зв'язки з компаніями/установами"


class Company(models.Model):
    name = models.CharField("Повна назва", max_length=255)
    short_name = models.CharField("Скорочена назва", max_length=50,
                                  blank=True)

    publish = models.BooleanField("Опублікувати", default=False)
    founded = models.DateField("Дата створення", blank=True, null=True)

    state_company = models.BooleanField(
        "Є державною установою", default=False)

    edrpou = models.CharField(
        "ЄДРПОУ/ідентифікаційний код", max_length=20, blank=True)

    zip_code = models.CharField("Індекс", max_length=10, blank=True)
    city = models.CharField("Місто", max_length=255, blank=True)
    street = models.CharField("Вулиця", max_length=100, blank=True)
    appt = models.CharField("№ будинку, офісу", max_length=50, blank=True)

    wiki = MarkdownField("Вікі-стаття", blank=True)

    other_founders = models.TextField(
        "Інші засновники",
        help_text="Через кому, не PEP", blank=True)

    other_recipient = models.CharField(
        "Бенефіціарій", help_text="Якщо не є PEPом", blank=True,
        max_length=100)

    other_owners = models.TextField(
        "Інші власники",
        help_text="Через кому, не PEP", blank=True)

    other_managers = models.TextField(
        "Інші керуючі",
        help_text="Через кому, не PEP", blank=True)

    bank_name = models.CharField("Назва банку", blank=True, max_length=100)

    related_companies = models.ManyToManyField(
        "self", through="Company2Company", symmetrical=False)

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "short_name__icontains", "name__icontains")

    def __unicode__(self):
        return self.short_name or self.name

    def to_dict(self):
        d = model_to_dict(self, fields=[
            "id", "name", "short_name", "state_company", "edrpo", "wiki",
            "other_founders", "other_recipient", "other_owners",
            "other_managers", "bank_name"])

        d["related_persons"] = [
            i.to_person_dict()
            for i in self.person2company_set.select_related("from_person")]

        d["related_countries"] = [
            i.to_dict()
            for i in self.company2country_set.select_related("to_country")]

        d["related_companies"] = [
            i.to_dict()
            for i in self.to_companies.select_related("to_company")] + [
            i.to_dict_reverse()
            for i in self.from_companies.select_related("from_company")
        ]

        d["name_suggest"] = {
            "input": filter(None, [d["name"], d["short_name"]]),
            "output": d["name"]
        }

        d["_id"] = d["id"]

        return d

    class Meta:
        verbose_name = "Юрідична особа"
        verbose_name_plural = "Юрідичні особи"


class Company2Company(models.Model):
    _relationships_explained = [
        "Власник",
        "Співвласник",
        "Споріднена",
        "Кредитор (фінансовий партнер)",
        "Надавач професійних послуг",
        "Клієнт",
        "Виконавець",
        "Замовник",
        "Підрядник",
        "Субпідрядник",
        "Постачальник",
        "Орендар",
        "Орендодавець",
        "Контрагент",
        "Правонаступник",
        "Правовласник",
    ]

    from_company = models.ForeignKey("Company", related_name="to_companies")
    to_company = models.ForeignKey("Company", related_name="from_companies")
    date_established = models.DateField(
        "Зв'язок почався", blank=True, null=True)
    date_finished = models.DateField(
        "Зв'язок скінчився", blank=True, null=True)
    date_confirmed = models.DateField(
        "Підтверджено", blank=True, null=True)

    proof_title = models.TextField(
        "Назва доказу зв'язку", blank=True,
        help_text="Наприклад: виписка з реєстру")
    proof = models.TextField("Посилання на доказ зв'язку", blank=True)

    relationship_type = models.CharField(
        "Тип зв'язку",
        choices=zip(_relationships_explained, _relationships_explained),
        max_length=30,
        blank=True)

    equity_part = models.FloatField(
        "Частка власності (відсотки)", blank=True, null=True)

    def to_dict(self):
        return {
            "relationship_type": self.relationship_type,
            "state_company": self.to_company.state_company,
            "company": self.to_company.name
        }

    def to_dict_reverse(self):
        return {
            "relationship_type": self.relationship_type,
            "state_company": self.from_company.state_company,
            "company": self.from_company.name
        }

    class Meta:
        verbose_name = "Зв'язок з компанією"
        verbose_name_plural = "Зв'язки з компаніями"


class Person2Country(models.Model):
    from_person = models.ForeignKey("Person", verbose_name="Персона")
    to_country = models.ForeignKey("Country", verbose_name="Країна")
    date_established = models.DateField(
        "Зв'язок почався", blank=True, null=True)
    date_finished = models.DateField(
        "Зв'язок скінчився", blank=True, null=True)
    date_confirmed = models.DateField(
        "Підтверджено", blank=True, null=True)

    proof_title = models.TextField(
        "Назва доказу зв'язку", blank=True,
        help_text="Наприклад: офіційна відповідь")
    proof = models.TextField("Посилання на доказ зв'язку", blank=True)

    relationship_type = models.CharField(
        "Тип зв'язку",
        choices=(
            ("born_in", "Народився(-лась)"),
            ("registered_in", "Зареєстрований(-а)"),
            ("lived_in", "Проживав(-ла)"),
            ("citizenship", "Громадянин(-ка)"),
            ("business", "Має зареєстрований бізнес"),
            ("under_sanctions", "Під санкціями"),
        ),

        max_length=30,
        blank=False)

    def __unicode__(self):
        return "%s у %s" % (
            self.get_relationship_type_display(), self.to_country)

    def to_dict(self):
        return {
            "relationship_type": self.relationship_type,
            "to_country": self.to_country.name
        }

    class Meta:
        verbose_name = "Зв'язок з країною"
        verbose_name_plural = "Зв'язки з країнами"


class Company2Country(models.Model):
    from_company = models.ForeignKey("Company", verbose_name="Компанія")
    to_country = models.ForeignKey("Country", verbose_name="Країна")
    date_established = models.DateField(
        "Зв'язок почався", blank=True, null=True)
    date_finished = models.DateField(
        "Зв'язок скінчився", blank=True, null=True)
    date_confirmed = models.DateField(
        "Підтверджено", blank=True, null=True)

    proof_title = models.TextField(
        "Назва доказу зв'язку", blank=True,
        help_text="Наприклад: витяг")
    proof = models.TextField("Посилання на доказ зв'язку", blank=True)

    relationship_type = models.CharField(
        "Тип зв'язку",
        choices=(
            ("registered_in", "Зареєстрована"),
            ("under_sanctions", "Під санкціями"),
        ),

        max_length=30,
        blank=False)

    def to_dict(self):
        return {
            "relationship_type": self.relationship_type,
            "to_country": self.to_country.name
        }

    def __unicode__(self):
        return "%s у %s" % (
            self.get_relationship_type_display(), self.to_country)

    class Meta:
        verbose_name = "Зв'язок з країною"
        verbose_name_plural = "Зв'язки з країнами"


class Country(models.Model):
    name = models.CharField("Назва", max_length=100)
    iso2 = models.CharField("iso2 код", max_length=2, blank=True)
    iso3 = models.CharField("iso3 код", max_length=3, blank=True)
    is_jurisdiction = models.BooleanField("Не є країною", default=False)

    def __unicode__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ("name_en__icontains", "name_ua__icontains")

    class Meta:
        verbose_name = "Країна/юрісдикція"
        verbose_name_plural = "Країни/юрісдикції"


class Document(models.Model):
    doc = models.FileField("Файл", upload_to="documents", max_length=1000)
    name = models.CharField("Людська назва", max_length=255)
    uploaded = models.DateTimeField("Був завантажений", auto_now=True)
    source = models.CharField("Першоджерело", blank=True, max_length=255)
    uploader = models.ForeignKey(User, verbose_name="Хто завантажив",
                                 related_name="pep_document")
    hash = models.CharField("Хеш", max_length=40, blank=True)
    comments = models.TextField("Коментарі", blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документи"


class Ua2RuDictionary(models.Model):
    term = models.CharField("Термін", max_length=255)
    translation = models.CharField("Переклад російською", max_length=255)
    alt_translation = models.CharField(
        "Альтернативний переклад", max_length=255, blank=True)
    comments = models.CharField("Коментарі", blank=True, max_length=100)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "Переклад російською"
        verbose_name_plural = "Переклади російською"
