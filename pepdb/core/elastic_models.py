from django.conf import settings

from elasticsearch_dsl import DocType, Completion
from cacheops import cached

from core.utils import (
    TranslatedField,
    blacklist,
    localized_field,
    localized_field_map,
    localized_fields,
)


class RangeRelevantEntitiesMixin(object):
    def relevant_related_persons(self):
        hl = getattr(self.meta, "highlight", None)

        hls = {k: [] for k in settings.LANGUAGE_CODES}

        if hl is not None:
            for lang in settings.LANGUAGE_CODES:
                hls[lang] = getattr(
                    hl, localized_field("related_persons.person", lang), []
                )

        highlighted = []
        peps = []
        rest = []

        for p in getattr(self, "related_persons", []):
            for lang in settings.LANGUAGE_CODES:
                if getattr(p, localized_field("person", lang)) in hls[lang]:
                    highlighted.append(p)
                    break
            else:
                if p.is_pep:
                    peps.append(p)
                else:
                    rest.append(p)

        res = highlighted + peps + rest

        # Sorting the list so best matches will appear on top
        res.sort(
            key=lambda x: min(
                [
                    hls[lang].index(getattr(x, localized_field("person", lang)))
                    if getattr(x, localized_field("person", lang)) in hls[lang]
                    else 10000
                    for lang in settings.LANGUAGE_CODES
                ]
            )
        )

        return res


class Person(DocType, RangeRelevantEntitiesMixin):
    """Person document."""

    full_name_suggest = Completion(preserve_separators=False)

    translated_first_name = TranslatedField(**localized_field_map("first_name"))
    translated_last_name = TranslatedField(**localized_field_map("last_name"))
    translated_patronymic = TranslatedField(**localized_field_map("patronymic"))

    translated_last_workplace = TranslatedField(**localized_field_map("last_workplace"))
    translated_last_job_title = TranslatedField(**localized_field_map("last_job_title"))

    @classmethod
    @cached(timeout=25 * 60 * 60)
    def get_all_persons(cls):
        return [
            blacklist(
                p.to_dict(),
                localized_fields("full_name_suggest")
                + [
                    "dob_details",
                    "dob",
                    "last_job_id",
                    "risk_category",
                    "photo_path",
                    "terminated",
                    "last_modified",
                ],
            )
            for p in cls.search().scan()
        ]

    class Meta:
        index = settings.PERSONS_INDEX_NAME


class Company(DocType, RangeRelevantEntitiesMixin):
    """Person document."""

    name_suggest = Completion(preserve_separators=False)

    translated_name = TranslatedField(**localized_field_map("name"))

    @classmethod
    @cached(timeout=25 * 60 * 60)
    def get_all_companies(cls):
        return [
            blacklist(
                p.to_dict(),
                localized_fields("name_suggest_output")
                + ["code_chunks", "name_suggest", "last_modified"],
            )
            for p in cls.search().scan()
        ]

    class Meta:
        index = settings.COMPANIES_INDEX_NAME
