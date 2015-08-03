from elasticsearch_dsl import DocType, Completion


class Person(DocType):
    """Person document."""
    full_name_suggest = Completion(preserve_separators=False)

    def relevant_related_persons(self):
        hl = getattr(
            self.meta,
            "highlight",
            {"related_persons.person": []})["related_persons.person"]

        highlighted = []
        peps = []
        rest = []

        for p in self.related_persons:
            if p.person in hl:
                highlighted.append(p)
            elif p.is_pep:
                peps.append(p)
            else:
                rest.append(p)

        res = highlighted + peps + rest

        # Sorting the list so best matches will appear on top
        res.sort(key=lambda x: hl.index(x.person) if x.person in hl else 10000)

        return res

    class Meta:
        index = 'peps'


class Company(DocType):
    """Person document."""

    name_suggest = Completion(preserve_separators=False)

    class Meta:
        index = 'peps'
