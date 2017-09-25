# coding: utf-8
from __future__ import unicode_literals

from core.universal_loggers import NoOpLogger
from core.models import Company2Country, Country


class Company2CountryImporter(object):
    def __init__(self, logger=NoOpLogger):
        """
        Accepts specially carved logger proxy to report problems
        to during the creation/update of the object.
        """

        self.logger = logger

    def get_or_create(self, company, country_name, relation):
        """
        Kind of get_or_create method, to create or update company2country model
        instance using data from declaration. DOESN'T SAVE THE MODIFIED OBJECT

        Returns Company2Country instance and a created flag
        """

        created = False

        if not country_name:
            self.logger.warning("Країна без імені")
            return None, False

        try:
            country = Country.objects.get(name_uk__iexact=country_name)
        except Country.DoesNotExist:
            self.logger.warning(
                "Не можу знайти країну %s" % country_name
            )
            return None, False
        except Country.MultipleObjectsReturned:
            self.logger.warning(
                "Забагато країн з назвою %s!" % country_name
            )
            return None, False

        conns = Company2Country.objects.filter(
            from_company=company,
            to_country=country,
            relationship_type=relation
        )

        if conns.count():
            conn = conns[0]
        else:
            created = True
            conn = Company2Country(
                from_company=company,
                to_country=country,
                relationship_type=relation
            )

        return conn, created
