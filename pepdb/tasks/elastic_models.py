from elasticsearch_dsl import Keyword, Text, DocType, Date


class EDRPOU(DocType):
    """EDRPOU."""

    edrpou = Keyword(index=True)
    location = Text(index=True, analyzer='ukrainian')
    company_profile = Text(index=True, analyzer='ukrainian', fields={'raw': Keyword(index=True)})
    head = Text(index=True, analyzer='ukrainian')
    name = Text(index=True, analyzer='ukrainian')
    short_name = Text(index=True, analyzer='ukrainian')
    status = Keyword(index=True)
    founders = Text(index=True, analyzer='ukrainian')
    last_update = Date()

    class Meta:
        index = 'edrpou'
