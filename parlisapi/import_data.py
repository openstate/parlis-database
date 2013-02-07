import csv
import os
import re

from dateutil import parser

from core.models import Zaak, Activiteit, Agendapunt, Besluit, Document, Stemming


def tsv_import(folder):
    Zaken(folder).execute()
    Activiteiten(folder).execute()
    Besluiten(folder).execute()
    Documenten(folder).execute()

    #Agendapunten(folder).execute()
    #Stemmingen(folder).execute()


class TsvImport(object):
    filename = ''
    model = None
    primary_key = 'id'

    def __init__(self, folder, filename=False):
        if filename:
            self.filename = filename

        self.folder = folder

    def getData(self, file):
        '''transform tsv data for processing'''

        # lowercase fieldnames
        yield file.next().lower()

        #replace \r, needed for some long teksts which still contain \r
        for line in file:
            yield line.replace('\r', '\\n')

    def execute(self):
        with open(os.path.join(self.folder, self.filename)) as IN:

            reader = csv.DictReader(self.getData(IN), dialect=csv.excel_tab, restkey='rest')

            for row in reader:
                if 'rest' in row:
                    print row['rest']
                self.handle(row)

    def handle(self, row):

        TIMESTAMP = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?$')

        #replace empty string with none
        for key, value in row.iteritems():
            value = value.decode('utf-8 ')
            row[key] = value

            if value == '':
                row[key] = None
            if value == 'false':
                row[key] = False
            if value == 'true':
                row[key] = True
            if TIMESTAMP.search(value):
                try:
                    row[key] = parser.parse(value + ' CET')
                except:
                    raise
                    pass

        if self.primary_key:
            try:
                instance, created = self.model.objects.get_or_create(id=row[self.primary_key], defaults=row)
            except:
                print row
                raise
            else:
                if not created and False:
                    d = DictDiffer(self.model.objects.filter(id=instance.id).values()[0], row)
                    print "Added:", d.added()
                    print "Removed:", d.removed()
                    print "Changed values:", map(lambda x: {x: (row[x], getattr(instance, x))}, d.changed())


class Zaken(TsvImport):
    filename = 'Zaken.tsv'
    model = Zaak


class Activiteiten(TsvImport):
    filename = 'Activiteiten.tsv'
    model = Activiteit


class Agendapunten(TsvImport):
    filename = 'Agendapunten.tsv'
    model = Agendapunt


class Besluiten(TsvImport):
    filename = 'Besluiten.tsv'
    model = Besluit


class Stemmingen(TsvImport):
    filename = 'Stemmingen.tsv'
    model = Stemming


class Documenten(TsvImport):
    filename = 'Documenten.tsv'
    model = Document



"""
A dictionary difference calculator
Originally posted as:
http://stackoverflow.com/questions/1165352/fast-comparison-between-two-python-dictionary/1165552#1165552
"""


class DictDiffer(object):
    """
Calculate the difference between two dictionaries as:
(1) items added
(2) items removed
(3) keys same in both but changed values
(4) keys same in both and unchanged values
"""
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.current_keys, self.past_keys = [
            set(d.keys()) for d in (current_dict, past_dict)
        ]
        self.intersect = self.current_keys.intersection(self.past_keys)

    def added(self):
        return self.current_keys - self.intersect

    def removed(self):
        return self.past_keys - self.intersect

    def changed(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] == self.current_dict[o])
