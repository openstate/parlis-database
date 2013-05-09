import csv
import os
import re

from pprint import pprint

from dateutil import parser

from .dictdiffer import DictDiffer

from core.models import Zaak, Activiteit, Agendapunt, Besluit, Document, \
                        Stemming, Kamerstukdossier, Status, ActiviteitActor, ZaakActor


def tsv_import(folder):

    #order is important
    klasses = [
        Zaken,
        ZakenVervanging,
        ZakenOverig,
        ZakenZieOok,
        Activiteiten,
        ActiviteitenVervangen,
        ActiviteitenVoortgezet,
        Besluiten,
        Documenten,
        Agendapunten,
        Stemmingen,
        ZakenRelatieKamerstukDossier,
        ZakenActiviteiten,
        ZakenBesluiten,
        ZakenDocumenten,
        ZakenStatussen,
        ZakenActoren,
        ZakenVervanging2,
        ZakenOverig2,
        ZakenZieOok2,
        ActiviteitenDocumenten,
        ActiviteitenZaken,
        ActiviteitenVervangen2,
        ActiviteitenVoortgezet2,
        ActiviteitenActoren,
    ]

    for klass in klasses:
        klass(folder).execute()


class TsvImport(object):
    data = False
    folder = ''
    filename = ''
    model = None
    primary_key = 'id'
    should_exist = False

    def __init__(self, folder='', data=False):
        if data:
            self.data = data

        self.folder = folder

    def getData(self, file):
        '''transform tsv data for processing

            #sample data
            >>> data = "Id\tField\n1234\tTekst With return\ris bad"

            #execute
            >>> getData(None, data)
            "id\tfield\n1234\tTekst With return\\nis bad"

        '''

        # lowercase fieldnames
        yield file.next().lower()

        #replace \r, needed for some long teksts which still contain \r
        for line in file:
            yield line.replace('\r', '\\n')

    def execute(self):
        if self.data:
            self.read(self.data)
        else:
            with open(os.path.join(self.folder, self.filename)) as IN:
                self.read(IN)

    def read(self, data):
        reader = csv.DictReader(self.getData(data), dialect=csv.excel_tab, restkey='rest')

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
                row[key] = parser.parse(value + ' CET')

        #always the case
        if self.primary_key:
            try:
                instance, created = self.model.objects.get_or_create(id=row[self.primary_key], defaults=row)
            except Exception as e:
                print e
                print row
            else:
                if self.should_exist and created:
                    print "Unexpected new data:"
                    print row

                #check for strange stuff
                if not created:
                    d = DictDiffer(self.model.objects.filter(id=instance.id).values()[0], row)
                    print row[self.primary_key]
                    if d.added():
                        print "Added:", d.added()

                    if d.removed():
                        print "Removed:", d.removed()

                    def make_list_value(value):
                        # Do some conversions explicit to reduce false positives
                        same = False

                        same = value == 'datum'

                        try:
                            same = re.sub(r'\s+', ' ', row[value].strip()) == re.sub(r'\s+', ' ', getattr(instance, value))
                        except:
                            pass

                        try:
                            same = int(row[value]) == getattr(instance, value)
                        except:
                            pass

                        try:
                            if getattr(instance, value) == None:
                                same = row[value].strip() == ''
                        except:
                            pass

                        try:
                            same = getattr(instance, value).replace(microseconds=0, tzinfo=None) == row[value].replace(microseconds=0, tzinfo=None)
                        except:
                            pass

                        if not same:
                            return {value: (row[value], getattr(instance, value))}

                    list = [x for x in map(make_list_value, d.changed()) if x]

                    if list:
                        print "Changed values:"
                        pprint(list)
        else:
            instance = self.model()

            for key in row:
                setattr(instance, key, row[key])

            instance.save()


class SubtreeImport(TsvImport):
    subfolder = ''
    many_to_many = True
    should_exist = True

#    def __init__(self, folder, data=False):
#        super(SubtreeImport, self).__init__(os.path.join(folder, self.subfolder), data)

    def handle(self, row):
        related_id = row[self.related_key]
        del row[self.related_key]

        super(SubtreeImport, self).handle(row)

        try:
            related = self.related_model.objects.get(id=related_id)
        except:
            print "Missing %s: %s" % (self.related_model._meta.verbose_name.title(), related_id)
        else:
            self.attach_to(related, row['id'])
            related.save()

    def attach_to(self, instance, id):
        if self.many_to_many:
            field = getattr(instance, self.key)
            field.add(id)
        else:
            setattr(instance, self.key + '_id', id)


"""
Actual imports
each class matches a tsv file
"""


class Zaken(TsvImport):
    filename = 'Zaken.tsv'
    model = Zaak


class Activiteiten(TsvImport):
    filename = 'Activiteiten.tsv'
    model = Activiteit


class Agendapunten(TsvImport):
    filename = 'Agendapunten.tsv'
    model = Agendapunt

    def handle(self, row):
        row['activiteit_id'] = row['sid_activiteit']
        del row['sid_activiteit']
        super(Agendapunten, self).handle(row)


class Besluiten(TsvImport):
    filename = 'Besluiten.tsv'
    model = Besluit


class Stemmingen(TsvImport):
    filename = 'Stemmingen.tsv'
    model = Stemming

    def handle(self, row):
        row['besluit_id'] = row['sid_besluit']
        del row['sid_besluit']
        super(Stemmingen, self).handle(row)


class Documenten(TsvImport):
    filename = 'Documenten.tsv'
    model = Document

    def handle(self, row):
        row['aanhangselnummer'] = row['aanhangelnummer']
        del row['aanhangelnummer']
        super(Documenten, self).handle(row)


class ZakenRelatie(SubtreeImport):
    subfolder = 'Zaken'
    related_key = 'sid_zaak'
    related_model = Zaak


class ActiviteitenRelatie(SubtreeImport):
    subfolder = 'ActiviteitRelaties'
    related_key = 'sid_activiteit'
    related_model = Activiteit


class ZakenRelatieKamerstukDossier(ZakenRelatie):
    filename = 'Zaken_KamerstukDossier.tsv'
    model = Kamerstukdossier
    key = 'kamerstukdossier'
    many_to_many = False
    should_exist = False


class ZakenActiviteiten(ZakenRelatie):
    filename = 'Zaken_Activiteiten.tsv'
    model = Activiteit
    key = 'activiteiten'
    many_to_many = True


class ZakenBesluiten(ZakenRelatie):
    filename = 'Zaken_Besluiten.tsv'
    model = Besluit
    key = 'besluiten'
    many_to_many = True


class ZakenDocumenten(ZakenRelatie):
    filename = 'Zaken_Documenten.tsv'
    model = Document
    key = 'documenten'
    many_to_many = True


class ZakenVervanging(ZakenRelatie):
    filename = 'Zaken_VervangenVanuit.tsv'
    model = Zaak
    key = 'vervanging'  # This one is in the right direction, related to ZakenOverig2
    many_to_many = True


class ZakenVervanging2(ZakenRelatie):
    filename = 'Zaken_VervangenDoor.tsv'
    model = Zaak
    key = 'vervanger'
    many_to_many = True


class ZakenOverig(ZakenRelatie):
    filename = 'Zaken_HoofdOverig.tsv'
    model = Zaak
    key = 'overig'  # This one is in the right direction, related to ZakenOverig2
    many_to_many = True


class ZakenOverig2(ZakenRelatie):
    filename = 'Zaken_GerelateerdOverig.tsv'
    model = Zaak
    key = 'overig2'
    many_to_many = True


class ZakenZieOok(ZakenRelatie):
    filename = 'Zaken_GerelateerdNaar.tsv'
    model = Zaak
    key = 'zieook'  # This one is in the right direction, related to ZakenOverig2
    many_to_many = True


class ZakenZieOok2(ZakenRelatie):
    filename = 'Zaken_GerelateerdVanuit.tsv'
    model = Zaak
    key = 'zieook2'
    many_to_many = True


class ZakenStatussen(TsvImport):
    filename = 'Zaken_Statussen.tsv'
    model = Status

    def handle(self, row):
        row['zaak_id'] = row['sid_zaak']
        del row['sid_zaak']
        super(ZakenStatussen, self).handle(row)


class ZakenActoren(TsvImport):
    filename = 'Zaken_ZaakActoren.tsv'
    model = ZaakActor

    def handle(self, row):
        row['zaak_id'] = row['sid_zaak']
        del row['sid_zaak']
        super(ZakenActoren, self).handle(row)


class ActiviteitenZaken(ActiviteitenRelatie):
    filename = 'Activiteiten_Zaken.tsv'
    model = Zaak
    key = 'zaken'
    many_to_many = True


class ActiviteitenDocumenten(ActiviteitenRelatie):
    filename = 'Activiteiten_Documenten.tsv'
    model = Document
    key = 'documenten'
    many_to_many = True


class ActiviteitenVervangen(ActiviteitenRelatie):
    filename = 'Activiteiten_VervangenDoor.tsv'
    model = Activiteit
    key = 'vervanging'  # This one is in the right direction, related to ZakenOverig2
    many_to_many = True


class ActiviteitenVervangen2(ActiviteitenRelatie):
    filename = 'Activiteiten_VervangenVanuit.tsv'
    model = Activiteit
    key = 'vervanger'
    many_to_many = True


class ActiviteitenVoortgezet(ActiviteitenRelatie):
    filename = 'Activiteiten_VoortgezetIn.tsv'
    model = Activiteit
    key = 'voortzetting'  # This one is in the right direction, related to ZakenOverig2
    many_to_many = True


class ActiviteitenVoortgezet2(ActiviteitenRelatie):
    filename = 'Activiteiten_VoortgezetVanuit.tsv'
    model = Activiteit
    key = 'voortzetting_van'
    many_to_many = True


class ActiviteitenActoren(TsvImport):
    filename = 'Activiteiten_ActiviteitActoren.tsv'
    model = ActiviteitActor

    def handle(self, row):
        row['activiteit_id'] = row['sid_activiteit']
        del row['sid_activiteit']
        super(ActiviteitenActoren, self).handle(row)
