import csv
import os

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

    def __init__(self, folder, filename=False):
        if filename:
            self.filename = filename

        self.folder = folder

    def getData(self, file):
        '''Open file, returns csvreader'''
        for line in file:
            yield line.replace('\r', '\\n')

    def execute(self):
        self.model.objects.all().delete()

        with open(os.path.join(self.folder, self.filename)) as IN:

            reader = csv.DictReader(self.getData(IN), dialect=csv.excel_tab, restkey='rest')

            for row in reader:
                if 'rest' in row:
                    print row['rest']
                self.handle(row)

    def handle(self, row):
        instance = self.model()
        for key in row:
            if row[key]:
                data = row[key]

                setattr(instance, key.lower(), data)
        try:
            instance.save()
        except:
            print row
            raise


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
