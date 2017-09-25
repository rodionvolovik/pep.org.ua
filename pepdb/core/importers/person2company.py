# coding: utf-8
from __future__ import unicode_literals
from datetime import date

from core.universal_loggers import NoOpLogger
from core.models import Person2Company


class Person2CompanyImporter(object):
    def __init__(self, logger=NoOpLogger):
        """
        Accepts specially carved logger proxy to report problems
        to during the creation/update of the object.
        """

        self.logger = logger

    def get_or_create_from_declaration(self, person, company, relation, decl):
        """
        Kind of get_or_create method, to create or update person2company model
        instance using data from declaration. DOESN'T SAVE THE MODIFIED OBJECT

        Returns Person2Company instance and a created flag
        """

        created = False
        conns = Person2Company.objects.filter(
            from_person=person,
            to_company=company,
            relationship_type=relation)

        last_day_of_year = date(int(decl.year), 12, 31)
        if conns.count():
            conn = conns[0]

            if conn.date_confirmed:
                if last_day_of_year > conn.date_confirmed:
                    conn.date_confirmed_details = 0
                    conn.date_confirmed = last_day_of_year
            else:
                conn.date_confirmed_details = 0
                conn.date_confirmed = last_day_of_year
        else:
            created = True
            conn = Person2Company(
                from_person=person,
                to_company=company,
                relationship_type=relation,
                date_confirmed_details=0,
                date_confirmed=last_day_of_year,
            )

        conn.declarations = list(
            set(conn.declarations or []) |
            set([decl.pk])
        )

        conn.proof_title = ", ".join(filter(
            None,
            set(conn.proof_title.split(", ")) |
            set(["Декларація за %s рік" % decl.year])
        ))

        conn.proof = ", ".join(filter(
            None,
            set(conn.proof.split(", ")) |
            set([decl.url + "?source"])
        ))

        return conn, created
