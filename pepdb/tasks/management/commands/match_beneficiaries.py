# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re

from django.core.management.base import BaseCommand
from django.utils.translation import activate
from django.conf import settings

from elasticsearch_dsl import Q

from core.models import Declaration, Country, Person
from core.model.exc import CannotResolveRelativeException
from tasks.elastic_models import EDRPOU
from tasks.models import BeneficiariesMatching


class Command(BaseCommand):
    help = """
    Collect companies where pep persons are beneficiary owners, clean it up,
    reconcile with companies registry, create tasks for manual verification
    """

    _countries = {
        "1": "Україна",
        "2": "Австралія",
        "3": "Австрія",
        "4": "Азербайджан",
        "5": "Аландські острови",
        "6": "Албанія",
        "7": "Алжир",
        "8": "Американське Самоа",
        "9": "Американські Віргінські острови",
        "10": "Ангілья",
        "11": "Ангола",
        "12": "Андорра",
        "13": "Антарктида",
        "14": "Антигуа і Барбуда",
        "15": "Аргентина",
        "16": "Аруба",
        "17": "Афганістан",
        "18": "Багамські Острови",
        "19": "Бангладеш",
        "20": "Барбадос",
        "21": "Бахрейн",
        "23": "Бельгія",
        "22": "Беліз",
        "24": "Бенін",
        "25": "Бермудські острови",
        "26": "Білорусь",
        "27": "Болгарія",
        "28": "Болівія",
        "29": "Боснія і Герцеговина",
        "30": "Ботсвана",
        "31": "Бразилія",
        "32": "Британська територія в Індійському океані",
        "33": "Британські Віргінські острови",
        "34": "Бруней",
        "35": "Буркіна-Фасо",
        "36": "Бурунді",
        "37": "Бутан",
        "38": "Вануату",
        "39": "Ватикан",
        "40": "Велика Британія",
        "41": "Венесуела",
        "42": "В'єтнам",
        "43": "Вірменія",
        "44": "Волліс і Футуна",
        "45": "Габон",
        "46": "Гаїті",
        "48": "Гамбія",
        "49": "Гана",
        "47": "Гаяна",
        "50": "Гваделупа",
        "51": "Гватемала",
        "52": "Гвінея",
        "53": "Гвінея-Бісау",
        "54": "Гернсі",
        "61": "Гібралтар",
        "55": "Гондурас",
        "56": "Гонконг",
        "57": "Гренада",
        "58": "Греція",
        "59": "Грузія",
        "60": "Гуам",
        "62": "Ґренландія",
        "63": "Данія",
        "65": "Джерсі",
        "66": "Джибуті",
        "67": "Домініка",
        "68": "Домініканська Республіка",
        "64": "ДР Конго",
        "75": "Єгипет",
        "70": "Еквадор",
        "71": "Екваторіальна Гвінея",
        "76": "Ємен",
        "72": "Еритрея",
        "73": "Естонія",
        "74": "Ефіопія",
        "77": "Замбія",
        "78": "Західна Сахара",
        "79": "Зімбабве",
        "69": "Зовнішні малі острови США",
        "80": "Ізраїль",
        "81": "Індія",
        "82": "Індонезія",
        "83": "Ірак",
        "84": "Іран",
        "85": "Ірландія",
        "86": "Ісландія",
        "87": "Іспанія",
        "88": "Італія",
        "89": "Йорданія",
        "90": "Кабо-Верде",
        "91": "Казахстан",
        "92": "Кайманові острови",
        "93": "Камбоджа",
        "94": "Камерун",
        "95": "Канада",
        "96": "Катар",
        "97": "Кенія",
        "98": "Киргизстан",
        "101": "Кіпр",
        "102": "Кірибаті",
        "99": "КНР",
        "103": "Кокосові острови (Кілінг)",
        "104": "Колумбія",
        "105": "Коморські Острови",
        "106": "Конго",
        "107": "Коста-Рика",
        "108": "Кот-д'Івуар",
        "109": "Куба",
        "110": "Кувейт",
        "111": "Лаос",
        "112": "Латвія",
        "113": "Лесото",
        "114": "Литва",
        "115": "Ліберія",
        "116": "Ліван",
        "117": "Лівія",
        "118": "Ліхтенштейн",
        "119": "Люксембург",
        "120": "Маврикій",
        "121": "Мавританія",
        "122": "Мадагаскар",
        "123": "Майотта",
        "124": "Макао",
        "125": "Македонія",
        "126": "Малаві",
        "127": "Малайзія",
        "129": "Мальдіви",
        "128": "Малі",
        "130": "Мальта",
        "131": "Марокко",
        "132": "Мартиніка",
        "133": "Маршаллові Острови",
        "134": "Мексика",
        "135": "Мозамбік",
        "136": "Молдова",
        "137": "Монако",
        "138": "Монголія",
        "139": "Монтсеррат",
        "140": "М'янма",
        "141": "Намібія",
        "142": "Науру",
        "143": "Непал",
        "144": "Нігер",
        "145": "Нігерія",
        "146": "Нідерланди",
        "147": "Нідерландські Антильські острови",
        "148": "Нікарагуа",
        "149": "Німеччина",
        "150": "Ніуе",
        "151": "Нова Зеландія",
        "152": "Нова Каледонія",
        "153": "Норвегія",
        "154": "ОАЕ",
        "155": "Оман",
        "156": "Острів Буве",
        "157": "Острів Мен",
        "158": "Острів Норфолк",
        "159": "Острів Різдва",
        "161": "Острови Герд і Макдональд",
        "162": "Острови Кука",
        "160": "Острови Святої Єлени, Вознесіння і Тристан-да-Кунья",
        "214": "Острови Теркс і Кайкос",
        "163": "Пакистан",
        "164": "Палау",
        "165": "Палестина",
        "166": "Панама",
        "167": "Папуа — Нова Гвінея",
        "173": "ПАР",
        "168": "Парагвай",
        "169": "Перу",
        "170": "Південна Джорджія та Південні Сандвічеві острови",
        "171": "Південна Корея",
        "172": "Південний Судан",
        "100": "Північна Корея",
        "174": "Північні Маріанські острови",
        "175": "Піткерн",
        "176": "Польща",
        "177": "Португалія",
        "178": "Пуерто-Рико",
        "179": "Реюньйон",
        "180": "Росія",
        "181": "Руанда",
        "182": "Румунія",
        "183": "Сальвадор",
        "184": "Самоа",
        "185": "Сан-Марино",
        "186": "Сан-Томе і Принсіпі",
        "187": "Саудівська Аравія",
        "188": "Свазіленд",
        "189": "Свальбард і Ян-Маєн",
        "190": "Сейшельські Острови",
        "191": "Сен-Бартельмі",
        "192": "Сенегал",
        "193": "Сен-Мартін",
        "194": "Сен-П'єр і Мікелон",
        "195": "Сент-Вінсент і Гренадини",
        "196": "Сент-Кіттс і Невіс",
        "197": "Сент-Люсія",
        "198": "Сербія",
        "209": "Сьєрра-Леоне",
        "199": "Сирія",
        "200": "Сінгапур",
        "201": "Словаччина",
        "202": "Словенія",
        "203": "Соломонові Острови",
        "204": "Сомалі",
        "206": "Судан",
        "207": "Суринам",
        "208": "Східний Тимор",
        "205": "США",
        "210": "Таджикистан",
        "211": "Таїланд",
        "212": "Тайвань",
        "213": "Танзанія",
        "215": "Того",
        "216": "Токелау",
        "217": "Тонга",
        "218": "Тринідад і Тобаго",
        "219": "Тувалу",
        "220": "Туніс",
        "221": "Туреччина",
        "222": "Туркменістан",
        "223": "Уганда",
        "224": "Угорщина",
        "225": "Узбекистан",
        "227": "Уругвай",
        "228": "Фарерські острови",
        "229": "Федеративні Штати Мікронезії",
        "230": "Фіджі",
        "231": "Філіппіни",
        "232": "Фінляндія",
        "233": "Фолклендські (Мальвінські) острови",
        "234": "Франція",
        "235": "Французька Гвіана",
        "236": "Французька Полінезія",
        "237": "Французькі Південні території",
        "238": "Хорватія",
        "239": "Центральноафриканська Республіка",
        "240": "Чад",
        "241": "Чехія",
        "242": "Чилі",
        "243": "Чорногорія",
        "244": "Швейцарія",
        "245": "Швеція",
        "246": "Шрі-Ланка",
        "247": "Ямайка",
        "248": "Японія"
    }

    def search_me(self, ownership, fuzziness=1, candidates=10):
        matches = []
        edrpous_found = []

        for company in ownership.pep_company_information:
            if company["country"] != "Україна":
                self.stdout.write(
                    "Skipping company %s, as it is abroad" %
                    company["company_name"]
                )
                continue

            ans = None
            if company["beneficial_owner_company_code"]:
                res = EDRPOU.search().query(
                    "term",
                    edrpou=company["beneficial_owner_company_code"].lstrip("0")
                )
                ans = res.execute()
                if not ans:
                    self.stdout.write(
                        "Cannot find a company by code %s, falling back to search by name %s" %
                        (
                            company["beneficial_owner_company_code"],
                            company["company_name"]
                        )
                    )

            if not ans:
                should = [
                    Q(
                        "multi_match",
                        query=company["company_name"],
                        fuzziness=fuzziness,
                        fields=["name", "short_name", "location"],
                        boost=2.
                    )
                ]

                if company["address"]:
                    should.append(
                        Q(
                            "match",
                            location={
                                "query": company["address"],
                                "fuzziness": fuzziness
                            }
                        )
                    )

                res = EDRPOU.search() \
                    .query(Q("bool", should=should)) \
                    .highlight_options(
                        order='score',
                        fragment_size=500,
                        number_of_fragments=100,
                        pre_tags=['<u class="match">'], post_tags=["</u>"]) \
                    .highlight("name", "short_name", "location")

                ans = res.execute()

            for a in ans[:candidates]:
                highlight = getattr(a.meta, "highlight", {})

                name = " ".join(a.meta.highlight.name) \
                    if "name" in highlight else a.name
                short_name = " ".join(a.meta.highlight.short_name) \
                    if "short_name" in highlight else a.short_name
                location = " ".join(a.meta.highlight.location) \
                    if "location" in highlight else a.location

                rec = {
                    "name": name,
                    "short_name": short_name,
                    "location": location,

                    "head": a.head,
                    "edrpou": a.edrpou,
                    "status": a.status,
                    "company_profile": a.company_profile,
                    "score": a._score
                }

                if rec["edrpou"] not in edrpous_found:
                    matches.append(rec)
                    edrpous_found.append(rec["edrpou"])

        return matches[:candidates]

    def resolve_person(self, declaration, ownership):
        try:
            person, _ = declaration.resolve_person(
                ownership.get("person"))
            return person.pk
        except CannotResolveRelativeException as e:
            self.stderr.write(unicode(e))

    def retrieve_countries(self):
        self.countries_mapping = {}

        for num, name in self._countries.items():
            try:
                self.countries_mapping[num] = \
                    Country.objects.get(name_uk=name)
            except Country.DoesNotExist:
                self.stderr.write("Cannot find country %s " % name)

    def get_key(self, obj, declarant):
        company_name = re.sub(
            "[\s%s]+" % (re.escape("'\"-.,№()")),
            "",
            obj["company_name"].lower(),
            re.U
        )

        return "!!".join((
            declarant.full_name,
            company_name,
        ))

    def insert_record(self, obj, declaration):
        if obj["country"] != "Україна":
            self.stdout.write(
                "Skipping company %s, as it is abroad" %
                obj["company_name"]
            )
            return

        if obj["declarant_id"] is None:
            return

        declarant = Person.objects.get(pk=obj["declarant_id"])
        key = self.get_key(obj, declarant)

        try:
            rec = BeneficiariesMatching.objects.get(company_key=key)
        except BeneficiariesMatching.DoesNotExist:
            rec = BeneficiariesMatching(
                company_key=key, pep_company_information=[]
            )

        rec.person = obj["declarant_id"]
        rec.person_json = declarant.to_dict()
        rec.is_family_member = obj["owner"] == "FAMILY"
        rec.declarations = list(
            set(rec.declarations or []) | set([declaration.pk]))

        if obj not in rec.pep_company_information:
            rec.pep_company_information.append(obj)

        rec.candidates_json = {}
        rec.save()

    def handle(self, *args, **options):
        activate(settings.LANGUAGE_CODE)
        self.stdout.write("Matching records for countries")
        self.retrieve_countries()
        self.stdout.write("Retrieving beneficiary ownership information")
        for d in Declaration.objects.filter(
                nacp_declaration=True, confirmed="a").select_related(
                "person"):
            data = d.source["nacp_orig"]
            if isinstance(data.get("step_9"), dict):
                for ownership in data["step_9"].values():
                    self.insert_record({
                        "declarant_id": (
                            d.person_id if ownership.get("person") == "1"
                            else self.resolve_person(d, ownership)
                        ),
                        "declarant_name": d.person.full_name,
                        "company_name": ownership.get("name"),
                        "legalForm": ownership.get("legalForm"),
                        "country": self._countries[
                            ownership.get("country", "1") or "1"],
                        "en_name": ownership.get("en_name"),
                        "location": ownership.get("location"),
                        "en_address": ownership.get("en_address"),
                        "phone": ownership.get("phone"),
                        "address": ownership.get("address"),
                        "mail": ownership.get("mail"),
                        "year_declared": d.year,
                        "beneficial_owner_company_code": ownership.get(
                            "beneficial_owner_company_code"),
                        "owner": "DECLARANT" if ownership.get(
                            "person") == "1" else "FAMILY"
                    }, declaration=d
                    )

        self.stdout.write("Matching with EDR registry")
        for ownership in BeneficiariesMatching.objects.all(status="p"):
            ownership.candidates_json = self.search_me(ownership)
            ownership.save()
