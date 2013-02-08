import csv
import os
import re

from pprint import pprint

from dateutil import parser

from core.models import Zaak, Activiteit, Agendapunt, Besluit, Document, Stemming, Kamerstukdossier, Status, ActiviteitActor, ZaakActor


def tsv_import(folder):
    #Zaken(folder).execute()
    #Activiteiten(folder).execute()
    #Besluiten(folder).execute()
    #Documenten(folder).execute()

    #Agendapunten(folder).execute()
    #Stemmingen(folder).execute()
    #ZakenRelatieKamerstukDossier(folder).execute()
    #ZakenActiviteiten(folder).execute()
    #ZakenBesluiten(folder).execute()
    #ZakenDocumenten(folder).execute()
    #ZakenStatussen(folder).execute()
    ZakenActoren(folder).execute()
    #ZakenVervanging(folder).execute()
    #ZakenOverig(folder).execute()
    #ZakenZieOok(folder).execute()
    #ZakenVervanging2(folder).execute()
    #ZakenOverig2(folder).execute()
    #ZakenZieOok2(folder).execute()
    #ActiviteitenDocumenten(folder).execute()
    #ActiviteitenZaken(folder).execute()
    #ActiviteitenVervangen(folder).execute()
    #ActiviteitenVoortgezet(folder).execute()
    #ActiviteitenVervangen2(folder).execute()
    #ActiviteitenVoortgezet2(folder).execute()
    ActiviteitenActoren(folder).execute()


class TsvImport(object):
    filename = ''
    model = None
    primary_key = 'id'
    should_exist = False

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
                row[key] = parser.parse(value + ' CET')

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

                if not created:
                    d = DictDiffer(self.model.objects.filter(id=instance.id).values()[0], row)

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
                            same = getattr(instance, value).replace(microseconds=0) == row[value].replace(microseconds=0)
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


class SubtreeImport(TsvImport):
    subfolder = ''
    many_to_many = True
    should_exist = True

    def __init__(self, folder, filename=False):
        super(SubtreeImport, self).__init__(os.path.join(folder, self.subfolder), filename)

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


class ZakenRelatie(SubtreeImport):
    subfolder = 'Zaken'
    related_key = 'sid_zaak'
    related_model = Zaak


class ActiviteitenRelatie(SubtreeImport):
    subfolder = 'ActiviteitRelaties'
    related_key = 'sid_activiteit'
    related_model = Activiteit


class ZakenRelatieKamerstukDossier(ZakenRelatie):
    filename = 'KamerstukDossier.tsv'
    model = Kamerstukdossier
    key = 'kamerstukdossier'
    many_to_many = False

class ZakenActiviteiten(ZakenRelatie):
    filename = 'Activiteiten.tsv'
    model = Activiteit
    key = 'activiteiten'
    many_to_many = True


class ZakenBesluiten(ZakenRelatie):
    filename = 'Besluiten.tsv'
    model = Besluit
    key = 'besluiten'
    many_to_many = True


class ZakenDocumenten(ZakenRelatie):
    filename = 'Documenten.tsv'
    model = Document
    key = 'documenten'
    many_to_many = True


class ZakenVervanging(ZakenRelatie):
    filename = 'VervangenVanuit.tsv'
    model = Zaak
    key = 'vervanging'  # This one is in the right direction, related to ZakenOverig2
    many_to_many = True


class ZakenVervanging2(ZakenRelatie):
    filename = 'VervangenDoor.tsv'
    model = Zaak
    key = 'vervanger'
    many_to_many = True


class ZakenOverig(ZakenRelatie):
    filename = 'HoofdOverig.tsv'
    model = Zaak
    key = 'overig'  # This one is in the right direction, related to ZakenOverig2
    many_to_many = True


class ZakenOverig2(ZakenRelatie):
    filename = 'GerelateerdOverig.tsv'
    model = Zaak
    key = 'overig2'
    many_to_many = True


class ZakenZieOok(ZakenRelatie):
    filename = 'GerelateerdNaar.tsv'
    model = Zaak
    key = 'zieook'  # This one is in the right direction, related to ZakenOverig2
    many_to_many = True


class ZakenZieOok2(ZakenRelatie):
    filename = 'GerelateerdVanuit.tsv'
    model = Zaak
    key = 'zieook2'
    many_to_many = True


class ZakenStatussen(TsvImport):
    filename = os.path.join('Zaken', 'Statussen.tsv')
    model = Status

    def handle(self, row):
        row['zaak_id'] = row['sid_zaak']
        del row['sid_zaak']
        super(ZakenStatussen, self).handle(row)


class ZakenActoren(TsvImport):
    filename = os.path.join('Zaken', 'ZaakActoren.tsv')
    model = ZaakActor

    def handle(self, row):
        row['zaak_id'] = row['sid_zaak']
        del row['sid_zaak']
        super(ZakenActoren, self).handle(row)


class ActiviteitenZaken(ActiviteitenRelatie):
    filename = 'Zaken.tsv'
    model = Zaak
    key = 'zaken'
    many_to_many = True


class ActiviteitenDocumenten(ActiviteitenRelatie):
    filename = 'Documenten.tsv'
    model = Document
    key = 'documenten'
    many_to_many = True


class ActiviteitenVervangen(ActiviteitenRelatie):
    filename = 'VervangenDoor.tsv'
    model = Activiteit
    key = 'vervanging'  # This one is in the right direction, related to ZakenOverig2
    many_to_many = True


class ActiviteitenVervangen2(ActiviteitenRelatie):
    filename = 'VervangenVanuit.tsv'
    model = Activiteit
    key = 'vervanger'
    many_to_many = True


class ActiviteitenVoortgezet(ActiviteitenRelatie):
    filename = 'VoortgezetIn.tsv'
    model = Activiteit
    key = 'voortzetting'  # This one is in the right direction, related to ZakenOverig2
    many_to_many = True


class ActiviteitenVoortgezet2(ActiviteitenRelatie):
    filename = 'VoortgezetVanuit.tsv'
    model = Activiteit
    key = 'voortzetting_van'
    many_to_many = True


class ActiviteitenActoren(TsvImport):
    filename = os.path.join('ActiviteitRelaties', 'ActiviteitActoren.tsv')
    model = ActiviteitActor

    def handle(self, row):
        row['activiteit_id'] = row['sid_activiteit']
        del row['sid_activiteit']
        super(ActiviteitenActoren, self).handle(row)

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
