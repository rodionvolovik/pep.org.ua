# coding: utf-8
from django.db import models
import select2.fields
import select2.models
from django.db.models import Q
from django.contrib.auth.models import User


class Person(models.Model):
    last_name = models.CharField(u"Прізвище", max_length=30)
    first_name = models.CharField(u"Ім'я", max_length=30)
    patronymic = models.CharField(u"По-батькові", max_length=30, blank=True)

    publish = models.BooleanField(u"Опублікувати", default=False)
    is_pep = models.BooleanField(u"Є PEPом", default=True)

    photo = models.ImageField(u"Світлина", blank=True)
    dob = models.DateField(u"Дата народження", blank=True, null=True)
    dob_details = models.IntegerField(
        u"Дата народження: точність",
        choices=(
            (0, "Точна дата"),
            (1, "Рік та місяць"),
            (2, "Тільки рік"),
        ),
        default=0)

    city_of_birth = models.CharField(
        u"Місто народження", max_length=100, blank=True)
    registration = models.TextField(
        u"Офіційне місце реєстрації (внутрішне поле)", blank=True)

    related_countries = models.ManyToManyField(
        "Country", verbose_name=u"Пов'язані країни",
        through="Person2Country", related_name="people")

    passport_id = models.CharField(
        u"Паспорт або інший документ (внутрішне поле)", max_length=20,
        blank=True)
    passport_reg = models.TextField(
        u"Дата видачі та орган (внутрішне поле)", blank=True)
    tax_payer_id = models.CharField(
        u"Номер картки платника податків (внутрішне поле)", max_length=30,
        blank=True)
    id_number = models.CharField(
        u"Ідентифікаційний номер (внутрішне поле)", max_length=10,
        blank=True)

    reputation_sanctions = models.TextField(
        u"Наявність санкцій", blank=True)
    reputation_crimes = models.TextField(
        u"Кримінальні впровадження", blank=True)
    reputation_manhunt = models.TextField(
        u"Перебування у розшуку", blank=True)
    reputation_convictions = models.TextField(
        u"Наявність судимості", blank=True)

    related_persons = select2.fields.ManyToManyField(
        "self", through="Person2Person", symmetrical=False,
        ajax=True,
        search_field=(
            lambda q: Q(last_name__icontains=q) | Q(first_name__icontains=q)))

    related_companies = models.ManyToManyField(
        "Company", through="Person2Company")

    wiki = models.TextField(u"Вікі-стаття", blank=True)
    names = models.TextField(u"Варіанти написання імені", blank=True)

    type_of_official = models.IntegerField(
        u"Тип ПЕП",
        choices=(
            (1, "Національний публічний діяч"),
            (2, "Іноземний публічний діяч"),
            (3,
             u"Діяч, що виконуює значні функції в міжнародній організації"),
            (4, "Пов'язана особа"),
            (5, "Близька особа"),
        ),
        max_length=1,
        blank=True,
        null=True)

    risk_category = models.CharField(
        u"Рівень ризику",
        choices=(
            (u"high", u"Високий"),
            (u"medium", u"Середній"),
            (u"low", u"Низький"),
        ),
        max_length=6, default=u"low")

    hash = models.CharField(u"Хеш", max_length=40, blank=True)

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "last_name__icontains", "first_name__icontains")

    def __unicode__(self):
        return u"%s %s %s" % (self.last_name, self.first_name, self.patronymic)

    class Meta:
        verbose_name = u"Фізична особа"
        verbose_name_plural = u"Фізичні особи"

        index_together = [
            ["last_name", "first_name"],
        ]


class Person2Person(models.Model):
    _relationships_explained = {
        u"чоловік": [u"дружина"],
        u"дружина": [u"чоловік"],
        u"батько": [u"син", u"дочка"],
        u"мати": [u"син", u"дочка"],
        u"вітчим": [u"пасинок", u"падчерка"],
        u"мачуха": [u"пасинок", u"падчерка"],
        u"син": [u"батько", u"мати"],
        u"дочка": [u"батько", u"мати"],
        u"пасинок": [u"вітчим", u"мачуха"],
        u"падчерка": [u"вітчим", u"мачуха"],
        u"рідний брат": [u"рідна сестра", u"рідний брат"],
        u"рідна сестра": [u"рідна сестра", u"рідний брат"],
        u"дід": [u"внук", u"внучка"],
        u"баба": [u"внук", u"внучка"],
        u"прадід": [u"правнук", u"правнучка"],
        u"прабаба": [u"правнук", u"правнучка"],
        u"внук": [u"дід", u"баба"],
        u"внучка": [u"дід", u"баба"],
        u"правнук": [u"прадід", u"прабаба"],
        u"правнучка": [u"прадід", u"прабаба"],
        u"усиновлювач": [u"усиновлений"],
        u"усиновлений": [u"усиновлювач"],
        u"опікун чи піклувальник": [
            u"особа, яка перебуває під опікою або піклуванням"],
        u"особа, яка перебуває під опікою або піклуванням": [
            u"опікун чи піклувальник"],
        u"особи, які спільно проживають": [u"особи, які спільно проживають"],
        u"пов'язані спільним побутом і мають взаємні права та обов'язки": [
            u"пов'язані спільним побутом і мають взаємні права та обов'язки"],
        u"ділові зв'язки": [u"ділові зв'язки"],
        u"особисті зв'язки": [u"особисті зв'язки"]
    }

    from_person = models.ForeignKey(
        "Person", verbose_name=u"Персона 1", related_name="to_persons")
    to_person = models.ForeignKey(
        "Person", verbose_name=u"Персона 2", related_name="from_persons")

    from_relationship_type = models.CharField(
        u"Персона 1 є",
        choices=(zip(_relationships_explained.keys(),
                     _relationships_explained.keys())),
        max_length=100,
        blank=True)

    to_relationship_type = models.CharField(
        u"Персона 2 є",
        choices=(zip(_relationships_explained.keys(),
                     _relationships_explained.keys())),
        max_length=100,
        blank=True)

    date_established = models.DateField(
        u"Коли почався зв'язок", blank=True, null=True)
    date_finished = models.DateField(
        u"Коли скінчився зв'язок", blank=True, null=True)
    date_confirmed = models.DateField(
        u"Дата підтвердження зв'язку", blank=True, null=True)

    proof_title = models.CharField(
        u"Назва доказу зв'язку", blank=True, max_length=100,
        help_text=u"Наприклад: склад ВР 7-го скликання")
    proof = models.URLField(u"Посилання на доказ зв'язку", blank=True)

    def __unicode__(self):
        return u"%s (%s) -> %s (%s)" % (
            self.from_person, self.get_from_relationship_type_display(),
            self.to_person, self.get_to_relationship_type_display())

    class Meta:
        verbose_name = u"Зв'язок з іншою персоною"
        verbose_name_plural = u"Зв'язки з іншими персонами"


class Person2Company(models.Model):
    _relationships_explained = [
        u"Президент",
        u"Прем’єр-міністр",
        u"Міністр",
        u"Перший заступник міністра",
        u"Заступник міністра",
        u"Керівник",
        u"Перший заступник керівника",
        u"Заступник керівника",
        u"Народний депутат",
        u"Голова",
        u"Заступник Голови",
        u"Член Правління",
        u"Член Ради",
        u"Суддя",
        u"Член",
        u"Генеральний прокурор",
        u"Заступник Генерального прокурора",
        u"Надзвичайний і повноважний посол",
        u"Головнокомандувач",
        u"Службовець першої категорії посад",
        u"Член центрального статутного органу",
        u"Повірений у справах",
        u"Засновник",
        u"Колишній засновник/учасник",
        u"Бенефіціарний власник",
        u"Номінальний власник",
        u"Номінальний директор",
        u"Фінансові зв'язки",
        u"Секретар",
        u"Керуючий"
    ]

    from_person = models.ForeignKey("Person")
    to_company = models.ForeignKey(
        "Company", verbose_name=u"Компанія або установа")

    date_established = models.DateField(
        u"Коли почався зв'язок", blank=True, null=True)
    date_finished = models.DateField(
        u"Коли скінчився зв'язок", blank=True, null=True)
    date_confirmed = models.DateField(
        u"Дата підтвердження зв'язку", blank=True, null=True)

    proof_title = models.CharField(
        u"Назва доказу зв'язку", blank=True, max_length=100,
        help_text=u"Наприклад: склад ВР 7-го скликання")
    proof = models.URLField(u"Посилання на доказ зв'язку", blank=True)

    relationship_type = models.CharField(
        u"Тип зв'язку",
        choices=zip(_relationships_explained, _relationships_explained),
        max_length=60,
        blank=True)

    def __unicode__(self):
        return u"%s (%s)" % (
            self.to_company, self.get_relationship_type_display())

    class Meta:
        verbose_name = u"Зв'язок з компанією/установою"
        verbose_name_plural = u"Зв'язки з компаніями/установами"


class Company(models.Model):
    name = models.CharField(u"Повна назва", max_length=255)
    short_name = models.CharField(u"Скорочена назва", max_length=50,
                                  blank=True)

    publish = models.BooleanField(u"Опублікувати", default=False)
    founded = models.DateField(u"Дата створення", blank=True, null=True)

    state_company = models.BooleanField(
        u"Є державною установою", default=False)

    edrpou = models.CharField(
        u"ЄДРПОУ/ідентифікаційний код", max_length=20, blank=True)

    zip_code = models.CharField(u"Індекс", max_length=10, blank=True)
    city = models.CharField(u"Місто", max_length=255, blank=True)
    street = models.CharField(u"Вулиця", max_length=100, blank=True)
    appt = models.CharField(u"№ будинку, офісу", max_length=50, blank=True)

    other_founders = models.TextField(
        u"Інші засновники",
        help_text=u"Через кому, не PEP", blank=True)

    other_recipient = models.CharField(
        u"Бенефіціарій", help_text=u"Якщо не є PEPом", blank=True,
        max_length=100)

    other_owners = models.TextField(
        u"Інші власники",
        help_text=u"Через кому, не PEP", blank=True)

    other_managers = models.TextField(
        u"Інші керуючі",
        help_text=u"Через кому, не PEP", blank=True)

    bank_name = models.CharField(u"Назва банку", blank=True, max_length=100)

    related_companies = models.ManyToManyField(
        "self", through="Company2Company", symmetrical=False)

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "short_name__icontains", "name__icontains")

    def __unicode__(self):
        return self.short_name or self.name

    class Meta:
        verbose_name = u"Юрідична особа"
        verbose_name_plural = u"Юрідичні особи"


class Company2Company(models.Model):
    _relationships_explained = [
        u"Власник",
        u"Співвласник",
        u"Споріднена",
        u"Кредитор (фінансовий партнер)",
        u"Надавач професійних послуг",
        u"Клієнт",
        u"Виконавець",
        u"Замовник",
        u"Підрядник",
        u"Субпідрядник",
        u"Постачальник",
        u"Орендар",
        u"Орендодавець",
        u"Контрагент",
        u"Правонаступник",
        u"Правовласник",
    ]

    from_company = models.ForeignKey("Company", related_name="to_companies")
    to_company = models.ForeignKey("Company", related_name="from_companies")
    date_established = models.DateField(
        u"Коли почався зв'язок", blank=True, null=True)
    date_finished = models.DateField(
        u"Коли скінчився зв'язок", blank=True, null=True)
    date_confirmed = models.DateField(
        u"Дата підтвердження зв'язку", blank=True, null=True)

    proof_title = models.CharField(
        u"Назва доказу зв'язку", blank=True, max_length=100,
        help_text=u"Наприклад: виписка з реєстру")
    proof = models.URLField(u"Посилання на доказ зв'язку", blank=True)

    relationship_type = models.CharField(
        u"Тип зв'язку",
        choices=zip(_relationships_explained, _relationships_explained),
        max_length=30,
        blank=True)

    equity_part = models.FloatField(
        u"Частка власності (відсотки)", blank=True, null=True)

    class Meta:
        verbose_name = u"Зв'язок з компанією"
        verbose_name_plural = u"Зв'язки з компаніями"


class Person2Country(models.Model):
    from_person = models.ForeignKey("Person", verbose_name=u"Персона")
    to_country = models.ForeignKey("Country", verbose_name=u"Країна")
    date_established = models.DateField(
        u"Коли почався зв'язок", blank=True, null=True)
    date_finished = models.DateField(
        u"Коли скінчився зв'язок", blank=True, null=True)
    date_confirmed = models.DateField(
        u"Дата підтвердження зв'язку", blank=True, null=True)

    proof_title = models.CharField(
        u"Назва доказу зв'язку", blank=True, max_length=100,
        help_text=u"Наприклад: офіційна відповідь")
    proof = models.URLField(u"Посилання на доказ зв'язку", blank=True)

    relationship_type = models.CharField(
        u"Тип зв'язку",
        choices=(
            (u"born_in", u"Народився(-лась)"),
            (u"registered_in", u"Зареєстрований(-а)"),
            (u"lived_in", u"Проживав(-ла)"),
            (u"citizenship", u"Громадянин(-ка)"),
            (u"business", u"Має зареєстрований бізнес")
        ),

        max_length=30,
        blank=False)

    def __unicode__(self):
        return u"%s у %s" % (
            self.get_relationship_type_display(), self.to_country)

    class Meta:
        verbose_name = u"Зв'язок з країною"
        verbose_name_plural = u"Зв'язки з країнами"


class Company2Country(models.Model):
    from_company = models.ForeignKey("Company", verbose_name=u"Компанія")
    to_country = models.ForeignKey("Country", verbose_name=u"Країна")
    date_established = models.DateField(
        u"Коли почався зв'язок", blank=True, null=True)
    date_finished = models.DateField(
        u"Коли скінчився зв'язок", blank=True, null=True)
    date_confirmed = models.DateField(
        u"Дата підтвердження зв'язку", blank=True, null=True)

    proof_title = models.CharField(
        u"Назва доказу зв'язку", blank=True, max_length=100,
        help_text=u"Наприклад: витяг")
    proof = models.URLField(u"Посилання на доказ зв'язку", blank=True)

    relationship_type = models.CharField(
        u"Тип зв'язку",
        choices=(
            (u"registered_in", u"Зареєстрована"),
        ),

        max_length=30,
        blank=False)

    def __unicode__(self):
        return u"%s у %s" % (
            self.get_relationship_type_display(), self.to_country)

    class Meta:
        verbose_name = u"Зв'язок з країною"
        verbose_name_plural = u"Зв'язки з країнами"


class Country(models.Model):
    name = models.CharField(u"Назва", max_length=100)
    iso2 = models.CharField(u"iso2 код", max_length=2, blank=True)
    iso3 = models.CharField(u"iso3 код", max_length=3, blank=True)
    is_jurisdiction = models.BooleanField(u"Не є країною", default=False)

    def __unicode__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ("name_en__icontains", "name_ua__icontains")

    class Meta:
        verbose_name = u"Країна/юрісдикція"
        verbose_name_plural = u"Країни/юрісдикції"


class Document(models.Model):
    doc = models.FileField(u"Файл")
    name = models.CharField(u"Людська назва", max_length=255)
    uploaded = models.DateTimeField(u"Був завантажений", auto_now=True)
    source = models.CharField(u"Першоджерело", blank=True, max_length=255)
    uploader = models.ForeignKey(User, verbose_name=u"Хто завантажив")
    comments = models.TextField(u"Коментарі", blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u"Документ"
        verbose_name_plural = u"Документи"


class Ua2RuDictionary(models.Model):
    term = models.CharField(u"Термін", max_length=255)
    translation = models.CharField(u"Переклад російською", max_length=255)
    alt_translation = models.CharField(
        u"Альтернативний переклад", max_length=255, blank=True)
    comments = models.CharField(u"Коментарі", blank=True, max_length=100)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u"Переклад російською"
        verbose_name_plural = u"Переклади російською"
