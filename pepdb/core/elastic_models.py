from elasticsearch_dsl import DocType, Completion


class Person(DocType):
    """Person document."""
    full_name_suggest = Completion(preserve_separators=False)

    class Meta:
        index = 'peps'


class Company(DocType):
    """Person document."""

    name_suggest = Completion(preserve_separators=False)

    class Meta:
        index = 'peps'
