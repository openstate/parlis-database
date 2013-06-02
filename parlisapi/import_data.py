import csv
import os
import re

from pprint import pprint

from dateutil import parser

from .dictdiffer import DictDiffer

from django.db.models import ManyToManyField
from django.db.models.fields import FieldDoesNotExist

from core.models import Zaak, Activiteit, Agendapunt, Besluit, Document, \
    Stemming, Kamerstukdossier, Status, ActiviteitActor, ZaakActor, Zaal, Reservering, \
    Documentactor, Documentversie


def tsv_import(folder):

    #order is important
    klasses = [
     #   Activiteiten,
     #   Besluiten,
     #   Kamerstukdossiers,
     #   Documenten,
     #   Zalen,  # Before Reserveringen
     #   Zaken,
     ##   Reserveringen, # skip this we need one with foreign keys to Zaal
     #   ZaalReserveringen,
     ##   Stemmingen,  # skip this we need one with foreign keys to Besluit
     #   BesluitStemmingen,


        # Relations on self
     #   ZakenVervanging,
     #   ZakenOverig,
     #   ZakenZieOok2,  # This needs to come before ZakenZieOok
     #   ZakenZieOok,  # Other way around has some extra data
     #   ZakenVervanging2,  # Other way around has some extra data
     #   ZakenOverig2,  # Other way around has some extra data
     #   ActiviteitenVervangen,
     #   ActiviteitenVoortgezet,
     #   ActiviteitenVervangen2,  # Other way around has some extra data
     #   ActiviteitenVoortgezet2,  # Other way around has some extra data
     #   DocumentenBronnen,  # has to be before DocumentenBijlagen
     #   DocumentenBijlagen,

        #ForeignKeys which can be null
     #   ZakenKamerstukDossier,
     #   KamerstukdossierZaken,
     #   KamerstukdossierDocumenten,  # Before DocumentenKamerstukDossier
     #   DocumentenKamerstukDossier,

        #many to many
        #ActiviteitenReserveringen,  # before ReserveringenActiviteiten
        #ReserveringenActiviteiten,
        #DocumentenActiviteiten,
        #ActiviteitenDocumenten,
        #DocumentenZaken,
        #ZakenDocumenten,
        #ZakenActiviteiten,
        #ActiviteitenZaken,
        #ZakenBesluiten,
        BesluitenZaken,

        #Agendapunt relations
     #   ActiviteitenAgendapunt,
     #   BesluitenAgendapunten,
     #   DocumentenAgendapunten,
     #   ZakenAgendapunten,  # this relation is not in accessdb

        #Statussen relations
     #   ZaakStatussen,
     #   BesluitStatussen,

        #New Tables
     #   DocumentActoren,
     #   DocumentVersies,
     #   ZaakActoren,
     #   ActiviteitActoren,




        StemmingenBesluit,
        Stemmingen,


        ReserveringenZaal,
        Reserveringen,
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
        print "Importing %s" % self.filename

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
                raise e
            else:
                if self.should_exist and created:
                    print "Unexpected new data:"
                    print row

                #check for strange stuff
                if False and not created:
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
    many_to_many = False
    should_exist = True
    related_tsv_key = None
    related_model = None
    key_in_self = False
    key_in_self = False

    def __init__(self, *args, **kwargs):
        super(SubtreeImport, self).__init__(*args, **kwargs)

        #set key_in_self from related_model verbose_name if not set
        if not self.key_in_self:
            self.key_in_self = self.related_model._meta.verbose_name

        #check key_in_self (strip '_id' in check)
        if not self.key_in_self in self.model._meta.get_all_field_names():
            raise FieldDoesNotExist(self.key_in_self)

        #set related_tsv_key from related_model verbose_name if not set
        if not self.related_tsv_key:
            self.related_tsv_key = 'sid_' + self.related_model._meta.verbose_name

        #determine many_to_many from field
        try:
            self.many_to_many = self.model._meta.get_field(self.key_in_self).__class__ == ManyToManyField
        except FieldDoesNotExist:
            # no field found so must be a related manager. Which we treat the same as many to many
            self.many_to_many = True

    def handle(self, row):
        related_id = row[self.related_tsv_key]
        del row[self.related_tsv_key]

        #check related_id
        related = None
        try:
            related = self.related_model.objects.get(pk=related_id)
        except:
            print "Missing %s: %s for relation with %s: %s" % (self.related_model._meta.verbose_name.title(), related_id, self.model._meta.verbose_name.title(), row[self.primary_key])

        #foreignkey to related
        if not self.many_to_many:
            row[self.key_in_self + '_id'] = related_id

        super(SubtreeImport, self).handle(row)

        #many to many or foreignkey from related
        if self.many_to_many and related:
            instance = self.model.objects.get(pk=row[self.primary_key])

            field = getattr(instance, self.key_in_self)
            field.add(related)


class ZakenRelatie(SubtreeImport):
    #related_tsv_key = 'sid_zaak'
    related_model = Zaak


class ZalenRelatie(SubtreeImport):
    #related_tsv_key = 'sid_zaal'
    related_model = Zaal


class ActiviteitenRelatie(SubtreeImport):
    #related_tsv_key = 'sid_activiteit'
    related_model = Activiteit


class BesluitenRelatie(SubtreeImport):
    #related_tsv_key = 'sid_besluit'
    related_model = Besluit


class DocumentenRelatie(SubtreeImport):
    #related_tsv_key = 'sid_document'
    related_model = Document


class KamerstukDossiersRelatie(SubtreeImport):
    #related_tsv_key = 'sid_kamerstukdossier'
    related_model = Kamerstukdossier


class ReserveringenRelatie(SubtreeImport):
    #related_tsv_key = 'sid_reservering'
    related_model = Reservering


class StemmingenRelatie(SubtreeImport):
    #related_tsv_key = 'sid_stemming'
    related_model = Stemming


"""
Actual imports
each class matches a tsv file
"""


class ActiviteitActoren(ActiviteitenRelatie):
    filename = 'Activiteiten_ActiviteitActoren.tsv'
    model = ActiviteitActor
    should_exist = False


class ActiviteitenAgendapunt(ActiviteitenRelatie):
    filename = 'Activiteiten_Agendapunten.tsv'
    model = Agendapunt
    should_exist = False


class ActiviteitenDocumenten(ActiviteitenRelatie):
    filename = 'Activiteiten_Documenten.tsv'
    model = Document
    key_in_self = 'activiteiten'


class ActiviteitenReserveringen(ActiviteitenRelatie):
    filename = 'Activiteiten_Reserveringen.tsv'
    model = Reservering
    key_in_self = 'activiteiten'
    primary_key = 'syscode'


class ActiviteitenVervangen(ActiviteitenRelatie):
    filename = 'Activiteiten_VervangenDoor.tsv'
    model = Activiteit
    key_in_self = 'vervanger'  # This one is in the right direction, related to ZakenOverig2


class ActiviteitenVervangen2(ActiviteitenRelatie):
    filename = 'Activiteiten_VervangenVanuit.tsv'
    model = Activiteit
    key_in_self = 'vervanging'


class ActiviteitenVoortgezet(ActiviteitenRelatie):
    filename = 'Activiteiten_VoortgezetIn.tsv'
    model = Activiteit
    key_in_self = 'voortzetting_van'  # This one is in the right direction, related to ZakenOverig2


class ActiviteitenVoortgezet2(ActiviteitenRelatie):
    filename = 'Activiteiten_VoortgezetVanuit.tsv'
    model = Activiteit
    key_in_self = 'voortzetting'


class ActiviteitenZaken(ActiviteitenRelatie):
    filename = 'Activiteiten_Zaken.tsv'
    model = Zaak
    key_in_self = 'activiteiten'


class Activiteiten(TsvImport):
    filename = 'Activiteiten.tsv'
    model = Activiteit


class BesluitenAgendapunten(BesluitenRelatie):
    filename = 'Besluiten_Agendapunt.tsv'
    model = Agendapunt
    key_in_self = 'besluiten'


class BesluitStatussen(BesluitenRelatie):
    filename = 'Besluiten_Statussen.tsv'
    model = Status
    should_exist = False


class BesluitStemmingen(BesluitenRelatie):
    filename = 'Besluiten_Stemmingen.tsv'
    model = Stemming


class BesluitenZaken(BesluitenRelatie):
    filename = 'Besluiten_Zaak.tsv'
    model = Zaak
    key_in_self = 'besluiten'


class Besluiten(TsvImport):
    filename = 'Besluiten.tsv'
    model = Besluit


class DocumentenActiviteiten(DocumentenRelatie):
    filename = 'Documenten_Activiteiten.tsv'
    model = Activiteit
    key_in_self = 'documenten'


class DocumentenAgendapunten(DocumentenRelatie):
    filename = 'Documenten_Agendapunten.tsv'
    model = Agendapunt
    key_in_self = 'documenten'


class DocumentenBijlagen(DocumentenRelatie):
    filename = 'Documenten_BijlageDocumenten.tsv'
    model = Document
    key_in_self = 'bijlagen_van'


class DocumentenBronnen(DocumentenRelatie):
    filename = 'Documenten_BronDocumenten.tsv'
    model = Document
    key_in_self = 'vervanger'


class DocumentActoren(DocumentenRelatie):
    filename = 'Documenten_DocumentActoren.tsv'
    model = Documentactor
    should_exist = False


class DocumentVersies(DocumentenRelatie):
    filename = 'Documenten_DocumentVersies.tsv'
    model = Documentversie
    should_exist = False


class DocumentenKamerstukDossier(DocumentenRelatie):
    filename = 'Documenten_KamerstukDossier.tsv'
    model = Kamerstukdossier
    key_in_self = 'documenten'


class DocumentenZaken(DocumentenRelatie):
    filename = 'Documenten_Zaken.tsv'
    model = Zaak
    key_in_self = 'documenten'


class Documenten(TsvImport):
    filename = 'Documenten.tsv'
    model = Document


class Kamerstukdossiers(TsvImport):
    filename = 'KamerstukDossiers.tsv'
    model = Kamerstukdossier


class KamerstukdossierDocumenten(KamerstukDossiersRelatie):
    filename = "KamerstukDossiers_Documenten.tsv"
    model = Document


class KamerstukdossierZaken(KamerstukDossiersRelatie):
    filename = "KamerstukDossiers_Zaken.tsv"
    model = Zaak


class ReserveringenActiviteiten(ReserveringenRelatie):
    filename = 'Reserveringen_Activiteiten.tsv'
    model = Activiteit
    key_in_self = 'reserveringen'

    def handle(self, row):
        # remove trailing )
        row['sid_reservering'] = row['sid_reservering'][:-1]
        super(ReserveringenActiviteiten, self).handle(row)


class ReserveringenZaal(ReserveringenRelatie):
    filename = 'Reserveringen_Zaal.tsv'
    model = Zaal
    primary_key = 'syscode'
    key_in_self = 'reserveringen'

    def handle(self, row):
        # remove trailing )
        row['sid_reservering'] = row['sid_reservering'][:-1]
        super(ReserveringenZaal, self).handle(row)


class Reserveringen(TsvImport):
    filename = 'Reserveringen.tsv'
    model = Reservering
    primary_key = 'syscode'


class StemmingenBesluit(BesluitenRelatie):
    filename = 'Stemmingen_Besluit.tsv'
    model = Besluit
    key_in_self = 'stemmingen'


class Stemmingen(TsvImport):
    filename = 'Stemmingen.tsv'
    model = Stemming


class ZakenActiviteiten(ZakenRelatie):
    filename = 'Zaken_Activiteiten.tsv'
    model = Activiteit
    key_in_self = 'zaken'

"""
Relation does not exist in Accessdb
class ZakenAgendapunt(ZakenRelatie):
    filename = 'Zaken_Agendapunten.tsv'
    model = Agendapunt
"""

class ZakenBesluiten(ZakenRelatie):
    filename = 'Zaken_Besluiten.tsv'
    model = Besluit
    key_in_self = 'zaken'


class ZakenDocumenten(ZakenRelatie):
    filename = 'Zaken_Documenten.tsv'
    model = Document
    key_in_self = 'zaken'


class ZakenZieOok(ZakenRelatie):
    filename = 'Zaken_GerelateerdNaar.tsv'
    model = Zaak
    key_in_self = 'zieook2'  # This one is in the right direction, related to ZakenOverig2


class ZakenOverig2(ZakenRelatie):
    filename = 'Zaken_GerelateerdOverig.tsv'
    model = Zaak
    key_in_self = 'overig'


class ZakenZieOok2(ZakenRelatie):
    filename = 'Zaken_GerelateerdVanuit.tsv'
    model = Zaak
    key_in_self = 'zieook'


class ZakenOverig(ZakenRelatie):
    filename = 'Zaken_HoofdOverig.tsv'
    model = Zaak
    key_in_self = 'overig2'  # This one is in the right direction, related to ZakenOverig2


class ZakenKamerstukDossier(ZakenRelatie):
    filename = 'Zaken_KamerstukDossier.tsv'
    model = Kamerstukdossier
    key_in_self = 'zaken'
    should_exist = False


class ZaakStatussen(ZakenRelatie):
    filename = 'Zaken_Statussen.tsv'
    model = Status
    should_exist = False


class ZakenVervanging2(ZakenRelatie):
    filename = 'Zaken_VervangenDoor.tsv'
    model = Zaak
    key_in_self = 'vervanging'


class ZakenVervanging(ZakenRelatie):
    filename = 'Zaken_VervangenVanuit.tsv'
    model = Zaak
    key_in_self = 'vervanger'  # This one is in the right direction, related to ZakenOverig2


class ZaakActoren(ZakenRelatie):
    filename = 'Zaken_ZaakActoren.tsv'
    model = ZaakActor
    should_exist = False


class Zaken(TsvImport):
    filename = 'Zaken.tsv'
    model = Zaak


class ZaalReserveringen(ZalenRelatie):
    """Should be the same as Zalen with zaalsyscode_id filled"""
    filename = 'Zalen_Reserveringen.tsv'
    model = Reservering
    primary_key = 'syscode'

    def handle(self, row):
        # remove trailing )
        row['sid_zaal'] = row['sid_zaal'][:-1]
        super(ZaalReserveringen, self).handle(row)


class Zalen(TsvImport):
    filename = 'Zalen.tsv'
    model = Zaal
    primary_key = 'syscode'
