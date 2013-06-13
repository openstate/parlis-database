from import_data import SubtreeImport, TsvImport

from core.models import Zaak, Activiteit, Agendapunt, Besluit, Document, \
    Stemming, Kamerstukdossier, Status, ActiviteitActor, ZaakActor, Zaal, Reservering, \
    DocumentActor, Documentversie


class ZakenRelatie(SubtreeImport):
    #related_tsv_key = 'sid_zaak'
    related_model = Zaak


class ZalenRelatie(SubtreeImport):
    related_model = Zaal


class ActiviteitenRelatie(SubtreeImport):
    related_model = Activiteit


class BesluitenRelatie(SubtreeImport):
    related_model = Besluit


class DocumentenRelatie(SubtreeImport):
    related_model = Document


class KamerstukDossiersRelatie(SubtreeImport):
    related_model = Kamerstukdossier


class ReserveringenRelatie(SubtreeImport):
    related_model = Reservering


class StemmingenRelatie(SubtreeImport):
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
    should_exist = False


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
    model = DocumentActor
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


class StemmingenBesluit(StemmingenRelatie):
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


#Relation does not exist in Accessdb
class ZakenAgendapunten(ZakenRelatie):
    filename = 'Zaken_Agendapunten.tsv'
    model = Agendapunt
    key_in_self = 'zaken'


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
    should_exist = False

    def handle(self, row):
        # remove trailing )
        row['sid_zaal'] = row['sid_zaal'][:-1]
        super(ZaalReserveringen, self).handle(row)


class Zalen(TsvImport):
    filename = 'Zalen.tsv'
    model = Zaal
    primary_key = 'syscode'


#order is important
klasses = [
    Activiteiten,
    Besluiten,
    Kamerstukdossiers,
    Documenten,
    Zalen,  # Before Reserveringen
    Zaken,
    Reserveringen,
    #Stemmingen,  # skip this we need one with foreign keys to Besluit
    BesluitStemmingen,


    # Relations on self
    ZakenVervanging,
    ZakenOverig,
    ZakenZieOok2,  # This needs to come before ZakenZieOok
    ZakenZieOok,  # Other way around has some extra data
    ZakenVervanging2,  # Other way around has some extra data
    ZakenOverig2,  # Other way around has some extra data
    ActiviteitenVervangen,
    ActiviteitenVoortgezet,
    ActiviteitenVervangen2,  # Other way around has some extra data
    ActiviteitenVoortgezet2,  # Other way around has some extra data
    DocumentenBronnen,  # has to be before DocumentenBijlagen
    DocumentenBijlagen,

    #ForeignKeys which can be null
    ZakenKamerstukDossier,
    KamerstukdossierZaken,
    KamerstukdossierDocumenten,  # Before DocumentenKamerstukDossier
    DocumentenKamerstukDossier,
    ZaalReserveringen,
    ReserveringenZaal,

    #many to many
    ActiviteitenReserveringen,  # before ReserveringenActiviteiten
    ReserveringenActiviteiten,
    DocumentenActiviteiten,
    ActiviteitenDocumenten,
    DocumentenZaken,
    ZakenDocumenten,
    ZakenActiviteiten,
    ActiviteitenZaken,
    ZakenBesluiten,
    BesluitenZaken,

    #Agendapunt relations
    ActiviteitenAgendapunt,
    BesluitenAgendapunten,
    DocumentenAgendapunten,
    ZakenAgendapunten,  # this relation is not in accessdb

    #Statussen relations
    ZaakStatussen,
    BesluitStatussen,

    #New Tables
    DocumentActoren,
    DocumentVersies,
    ZaakActoren,
    ActiviteitActoren,


    #not realy neccesary
    StemmingenBesluit,
    Stemmingen,
]
