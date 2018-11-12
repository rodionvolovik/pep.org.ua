# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from elasticsearch_dsl import Q, Keyword, Text, DocType, Date


class EDRPOU(DocType):
    """EDRPOU."""

    status_order = (
        "зареєстровано",
        "зареєстровано, свідоцтво про державну реєстрацію недійсне",
        "порушено справу про банкрутство",
        "порушено справу про банкрутство (санація)",
        "в стані припинення",
        "припинено",
    )

    edrpou = Keyword(index=True)
    location = Text(index=True, analyzer="ukrainian")
    company_profile = Text(
        index=True, analyzer="ukrainian", fields={"raw": Keyword(index=True)}
    )
    head = Text(index=True, analyzer="ukrainian")
    name = Text(index=True, analyzer="ukrainian")
    short_name = Text(index=True, analyzer="ukrainian")
    status = Keyword(index=True)
    founders = Text(index=True, analyzer="ukrainian")
    last_update = Date()

    @classmethod
    def find_by_edrpou(cls, edrpou):
        # Because open copy of registry has no dates and some of companies
        # has more than one record we are using heuristic here to determine
        # latest record using registration status (they have "priorities")
        ans = []
        for order in cls.status_order:
            res = cls.search().query(
                "bool",
                must=[Q("term", edrpou=edrpou.lstrip("0")), Q("term", status=order)],
            )
            ans = res.execute()
            if ans:
                break

        # Last attempt
        if not ans:
            res = cls.search().query("term", edrpou=edrpou.lstrip("0"))
            ans = res.execute()

        return ans

    class Meta:
        index = "edrpou"
