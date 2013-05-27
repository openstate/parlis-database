import csv
import os
import re

from pprint import pprint

from dateutil import parser

from .dictdiffer import DictDiffer

from core.models import Zaak, Activiteit, Agendapunt, Besluit, Document, \
    Stemming, Kamerstukdossier, Status, ActiviteitActor, ZaakActor, Zaal, Reservering


def tsv_import(folder):

    #order is important
    klasses = [
#        Zaken,
#        Zalen,
#        Reserveringen,
#        ZakenVervanging,
#        ZakenOverig,
#        ZakenZieOok,
#        Activiteiten,
#        ActiviteitenVervangen,
#        ActiviteitenVoortgezet,
#        Besluiten,
#        Documenten,
#        Agendapunten,
#        Agendapunten2,
#        Stemmingen,
#        ZakenRelatieKamerstukDossier,
#        ZakenActiviteiten,
#        ZakenBesluiten,
#        ZakenDocumenten,
#        ZakenStatussen,
#        ZakenActoren,
#        ZakenVervanging2,
#        ZakenOverig2,
#        ZakenZieOok2,
#        ActiviteitenDocumenten,
#        ActiviteitenZaken,
#        ActiviteitenVervangen2,
#        ActiviteitenVoortgezet2,
#        ActiviteitenActoren,
#        BesluitenStatussen,
        DocumentenKamerstukDossier,
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
                instance, created = self.model.objects.get_or_create(pk=row[self.primary_key], defaults=row)
            except Exception as e:
                print e
                print row
            else:
                if self.should_exist and created:
                    print "Unexpected new data:"
                    print row

                #check for strange stuff
                if not created:
                    d = DictDiffer(row, self.model.objects.filter(pk=getattr(instance,self.primary_key)).values()[0])

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
                            row[value] = row[value] - row[value].utcoffset()
                            same = getattr(instance, value).replace(microsecond=0, tzinfo=None) == row[value].replace(microsecond=0, tzinfo=None)
                        except:
                            pass

                        if not same:
                            return {value: (row[value], getattr(instance, value))}

                    list = [x for x in map(make_list_value, d.changed()) if x]

                    if d.added() or d.removed() or list:
                        print row[self.primary_key]

                    if d.added():
                        print "Added (only in tsv):", d.added()

                        #actualy add the new info
                        for key in d.added():
                            setattr(instance, key, row[key])

                        instance.save()

                    if d.removed():
                        print "Removed (only in db):", d.removed()

                    if list:
                        print "Changed values (tsv, db):"
                        pprint(list)

                        if getattr(instance, 'gewijzigdop') == row['gewijzigdop']:
                            #actualy add new info if None
                            for key in d.changed():
                                if getattr(instance, key) is None:
                                    setattr(instance, key, row[key])
                            instance.save()
                        elif getattr(instance, 'gewijzigdop') < row['gewijzigdop']:
                            for key in d.changed():
                                setattr(instance, key, row[key])
                            instance.save()


        else:
            instance = self.model()

            for key in row:
                setattr(instance, key, row[key])

            instance.save()


class SubtreeImport(TsvImport):
    many_to_many = True
    should_exist = True
    related_key = None
    related_model = None

    def handle(self, row):
        related_id = row[self.related_key]
        del row[self.related_key]

        super(SubtreeImport, self).handle(row)

        try:
            related = self.related_model.objects.get(pk=related_id)
        except:
            print "Missing %s: %s" % (self.related_model._meta.verbose_name.title(), related_id)
        else:
            self.attach_to(related, row[self.primary_key])
            related.save()

    def attach_to(self, instance, id):
        if self.many_to_many:
            field = getattr(instance, self.key)
            field.add(id)
        else:
            setattr(instance, self.key + '_id', id)


class ZakenRelatie(SubtreeImport):
    related_key = 'sid_zaak'
    related_model = Zaak


class ActiviteitenRelatie(SubtreeImport):
    related_key = 'sid_activiteit'
    related_model = Activiteit


class BesluitenRelatie(SubtreeImport):
    related_key = 'sid_besluit'
    related_model = Besluit


class DocumentenRelatie(SubtreeImport):
    related_key = 'sid_document'
    related_model = Document


class KamerstukDossiersRelatie(SubtreeImport):
    related_key = 'sid_kamerstukdossier'
    related_model = Kamerstukdossier


class ReserveringenRelatie(SubtreeImport):
    related_key = 'sid_reservering'
    related_model = Reservering


class StemmingenRelatie(SubtreeImport):
    related_key = 'sid_stemming'
    related_model = Stemming


"""
Actual imports
each class matches a tsv file
"""


class ActiviteitenActoren(ActiviteitenRelatie):
    filename = 'Activiteiten_ActiviteitActoren.tsv'
    model = ActiviteitActor
    key = 'activiteit'
    many_to_many = False


class ActiviteitenAgendapunten(ActiviteitenRelatie):
    filename = 'Activiteiten_Agendapunten.tsv'
    model = Agendapunt
    key = 'activiteit'
    many_to_many = False


class ActiviteitenDocumenten(ActiviteitenRelatie):
    filename = 'Activiteiten_Documenten.tsv'
    model = Document
    key = 'documenten'
    many_to_many = True


class ActiviteitenReserveringen(ActiviteitenRelatie):
    filename = 'Activiteiten_Reserveringen.tsv'
    model = Reservering
    key = 'reserveringen'
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


class ActiviteitenZaken(ActiviteitenRelatie):
    filename = 'Activiteiten_Zaken.tsv'
    model = Zaak
    key = 'zaken'
    many_to_many = True


class Activiteiten(TsvImport):
    filename = 'Activiteiten.tsv'
    model = Activiteit


class BesluitenAgendapunten(BesluitenRelatie):
    filename = 'Besluiten_Agendapunt.tsv'
    model = Agendapunt
    key = 'besluiten'
    many_to_many = True


class BesluitenStatussen(TsvImport):
    filename = 'Besluiten_Statussen.tsv'
    model = Status
    key = 'besluit'
    many_to_many = False


class BesluitenStemmingen(TsvImport):
    filename = 'Besluiten_Stemmingen.tsv'
    model = Stemming
    key = 'besluit'
    many_to_many = False


class BesluitenZaken(BesluitenRelatie):
    filename = 'Besluiten_Zaken.tsv'
    model = Status
    key = 'besluiten'
    many_to_many = True


class Besluiten(TsvImport):
    filename = 'Besluiten.tsv'
    model = Besluit


class DocumentenKamerstukDossier(DocumentenRelatie):
    filename = 'Documenten_KamerstukDossier.tsv'
    model = Kamerstukdossier
    key = 'kamerstukdossier'
    many_to_many = False


class Documenten(TsvImport):
    filename = 'Documenten.tsv'
    model = Document


class ReserveringenZaal(ReserveringenRelatie):
    filename = 'Reserveringen_Zaal.tsv'
    model = Zaal
    primary_key = 'syscode'
    key = 'reservering'
    many_to_many = False

    def handle(self, row):
        row['sid_reservering'] = row['sid_reservering'][:-1]
        super(ReserveringenZaal, self).handle(row)


class Reserveringen(TsvImport):
    filename = 'Reserveringen.tsv'
    model = Reservering
    primary_key = 'syscode'


class StemmingenBesluit(StemmingenRelatie):
    filename = 'Besluiten_Stemmingen.tsv'
    model = Stemming
    key = 'besluit'
    many_to_many = False


class Stemmingen(TsvImport):
    filename = 'Stemmingen.tsv'
    model = Stemming


class ZakenActiviteiten(ZakenRelatie):
    filename = 'Zaken_Activiteiten.tsv'
    model = Activiteit
    key = 'activiteiten'
    many_to_many = True


class ZakenAgendapunten(ZakenRelatie):
    """Maybe not needed"""
    filename = 'Zaken_Agendapunten.tsv'
    model = Agendapunt
    key = 'zaak'
    many_to_many = False


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


class ZakenZieOok(ZakenRelatie):
    filename = 'Zaken_GerelateerdNaar.tsv'
    model = Zaak
    key = 'zieook'  # This one is in the right direction, related to ZakenOverig2
    many_to_many = True


class ZakenOverig2(ZakenRelatie):
    filename = 'Zaken_GerelateerdOverig.tsv'
    model = Zaak
    key = 'overig2'
    many_to_many = True


class ZakenZieOok2(ZakenRelatie):
    filename = 'Zaken_GerelateerdVanuit.tsv'
    model = Zaak
    key = 'zieook2'
    many_to_many = True


class ZakenOverig(ZakenRelatie):
    filename = 'Zaken_HoofdOverig.tsv'
    model = Zaak
    key = 'overig'  # This one is in the right direction, related to ZakenOverig2
    many_to_many = True


class ZakenKamerstukDossier(ZakenRelatie):
    filename = 'Zaken_KamerstukDossier.tsv'
    model = Kamerstukdossier
    key = 'kamerstukdossier'
    many_to_many = False
    should_exist = False


class ZakenStatussen(ZakenRelatie):
    filename = 'Zaken_Statussen.tsv'
    model = Status
    key = 'zaak'
    many_to_many = False


class ZakenVervanging2(ZakenRelatie):
    filename = 'Zaken_VervangenDoor.tsv'
    model = Zaak
    key = 'vervanger'
    many_to_many = True


class ZakenVervanging(ZakenRelatie):
    filename = 'Zaken_VervangenVanuit.tsv'
    model = Zaak
    key = 'vervanging'  # This one is in the right direction, related to ZakenOverig2
    many_to_many = True


class ZakenActoren(ZakenRelatie):
    filename = 'Zaken_ZaakActoren.tsv'
    model = ZaakActor
    key = 'zaak'
    many_to_many = False


class Zaken(TsvImport):
    filename = 'Zaken.tsv'
    model = Zaak


class ZalenReserveringen(TsvImport):
    filename = 'Zalen_Reserveringen.tsv'
    model = Reservering
    primary_key = 'syscode'

    def handle(self, row):
        if row['nummer'][-3:] != '.00':
            print "Losing data!"
        row['nummer'] = row['nummer'][:-3]
        row['zaalsyscode_id'] = row['sid_zaal'][:-1]
        del row['sid_zaal']
        super(Reserveringen, self).handle(row)


class Zalen(TsvImport):
    filename = 'Zalen.tsv'
    model = Zaal
    primary_key = 'syscode'
