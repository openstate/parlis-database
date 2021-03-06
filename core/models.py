# -*- coding: utf-8 -*-
from django.db import models
from actors.models import Party, Politician

STATUS = [
    ('Vrijgegeven', 'Vrijgegeven'),
]

KAMER = [
    ('Eerste Kamer en Tweede Kamer', 'Eerste Kamer en Tweede Kamer'),
    ('Tweede Kamer', 'Tweede Kamer'),
    ('Verenigde Vergadering', 'Verenigde Vergadering'),
]


class Activiteit(models.Model):
    SOORT = [
        ("Aanbieding", "Aanbieding"),
        ("Afscheid", "Afscheid"),
        ("Algemeen overleg", "Algemeen overleg"),
        ("Beëdiging", "Beëdiging"),
        ("Begrotingsoverleg", "Begrotingsoverleg"),
        ("Bijzondere procedure", "Bijzondere procedure"),
        ("Constituerende vergadering", "Constituerende vergadering"),
        ("Gesprek", "Gesprek"),
        ("Hamerstukken", "Hamerstukken"),
        ("Herdenking", "Herdenking"),
        ("Hoorzitting / rondetafelgesprek", "Hoorzitting / rondetafelgesprek"),
        ("Inbreng feitelijke vragen", "Inbreng feitelijke vragen"),
        ("Inbreng schriftelijk overleg", "Inbreng schriftelijk overleg"),
        ("Inbreng verslag (wetsvoorstel)", "Inbreng verslag (wetsvoorstel)"),
        ("Interpellatiedebat", "Interpellatiedebat"),
        ("Notaoverleg", "Notaoverleg"),
        ("Petitie", "Petitie"),
        ("Plenair debat", "Plenair debat"),
        ("Procedurevergadering", "Procedurevergadering"),
        ("Regeling van werkzaamheden", "Regeling van werkzaamheden"),
        ("Schriftelijk commentaar algemeen", "Schriftelijk commentaar algemeen"),
        ("Schriftelijk commentaar gericht", "Schriftelijk commentaar gericht"),
        ("Stemmingen", "Stemmingen"),
        ("Technische briefing", "Technische briefing"),
        ("Verklaring", "Verklaring"),
        ("Vragenuur", "Vragenuur"),
        ("Werkbezoek", "Werkbezoek"),
        ("Wetgevingsoverleg ", "Wetgevingsoverleg "),
    ]

    STATUS = [
        ("Geannuleerd", "Geannuleerd"),
        ("Gepland", "Gepland"),
        ("Uitgevoerd", "Uitgevoerd"),
        ("Verplaatst", "Verplaatst"),
    ]

    DATUMSOORT = [
        ("Dag", "Dag"),
        ("Meerdaags", "Meerdaags"),
        ("Nog geen datum bekend", "Nog geen datum bekend"),
        ("Weeknummer", "Weeknummer"),
    ]

    id = models.CharField(max_length=36, primary_key=True)
    nummer = models.CharField(max_length=10)
    onderwerp = models.TextField()
    soort = models.CharField(max_length=50, choices=SOORT)
    datumsoort = models.CharField(max_length=50, choices=DATUMSOORT)
    datum = models.DateTimeField(null=True, blank=True)  # Niet in tsv, wel in Zaken_Activiteiten
    aanvangstijd = models.DateTimeField(null=True, blank=True)
    eindtijd = models.DateTimeField(null=True, blank=True)
    locatie = models.CharField(max_length=100, null=True, blank=True)
    besloten = models.BooleanField()  # Niet in access?!
    status = models.CharField(max_length=15, choices=STATUS)
    vergaderjaar = models.CharField(max_length=9)
    kamer = models.CharField(max_length=30, choices=KAMER)
    noot = models.TextField(null=True, blank=True)
    aangemaaktop = models.DateTimeField(auto_now_add=False)
    gewijzigdop = models.DateTimeField(auto_now=False)
    vrsnummer = models.IntegerField(blank=True, null=True)
    voortouwnaam = models.CharField(max_length=150)
    voortouwafkorting = models.CharField(max_length=20)
    voortouwkortenaam = models.CharField(max_length=50)

    vervanging = models.ManyToManyField('self', symmetrical=False, related_name="vervanger")
    voortzetting = models.ManyToManyField('self', symmetrical=False, related_name="voortzetting_van")
    documenten = models.ManyToManyField('Document', related_name='activiteiten')
    reserveringen = models.ManyToManyField('Reservering', related_name='activiteiten')

    def __unicode__(self):
        return self.onderwerp

    class Meta:
        verbose_name_plural = u"Activiteiten"


class ActiviteitActor(models.Model):
    RELATIE = [
        ("Interpellant", "Interpellant"),
        ("Volgcommissie", "Volgcommissie"),
        ("Initiatiefnemer", "Initiatiefnemer"),
        ("Bewindspersoon c.a.", "Bewindspersoon c.a."),
        ("Relatie", "Relatie"),
        ("Afgemeld", "Afgemeld"),
        ("Deelnemer", "Deelnemer"),
    ]

    id = models.CharField(max_length=36, primary_key=True)
    activiteit = models.ForeignKey(Activiteit)
    naam = models.CharField(max_length=150)
    functie = models.CharField(max_length=150, null=True)
    partij = models.CharField(max_length=50, null=True)
    relatie = models.CharField(max_length=50, choices=RELATIE)
    spreektijd = models.CharField(max_length=50, null=True)
    volgorde = models.IntegerField()
    politician = models.ForeignKey(Politician, null=True, on_delete=models.SET_NULL)
    party = models.ForeignKey(Party, null=True, on_delete=models.SET_NULL)
    aangemaaktop = models.DateTimeField(auto_now_add=False)
    gewijzigdop = models.DateTimeField(auto_now=False)

    def __unicode__(self):
        return '%s van %s (%s)' % (self.naam, self.partij, self.functie)


class Agendapunt(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    nummer = models.CharField(max_length=10, unique=True)
    activiteit = models.ForeignKey(Activiteit, null=True, blank=True, related_name='agendapunten')
    onderwerp = models.TextField()
    aanvangstijd = models.DateTimeField(null=True, blank=True)
    eindtijd = models.DateTimeField(null=True, blank=True)
    volgorde = models.IntegerField(null=True, blank=True)
    rubriek = models.CharField(max_length=200, null=True, blank=True)
    noot = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS)
    aangemaaktop = models.DateTimeField(auto_now_add=False)
    gewijzigdop = models.DateTimeField(auto_now=False)

    besluiten = models.ManyToManyField('Besluit', related_name='agendapunten')
    documenten = models.ManyToManyField('Document', related_name='agendapunten')
    zaken = models.ManyToManyField('Zaak', related_name='agendapunten')

    def __unicode__(self):
        return self.onderwerp

    class Meta:
        verbose_name_plural = u"Agendapunten"


class Besluit(models.Model):
    STEMMINGSSOORT = [
        ("Hoofdelijk", "Hoofdelijk"),
        ("Met handopsteken", "Met handopsteken"),
        ("Zonder stemming", "Zonder stemming"),
    ]

    STATUS = [
        ('Besluit', 'Besluit'),
    ]

    id = models.CharField(max_length=36, primary_key=True)
    soort = models.CharField(max_length=765, null=True)
    status = models.CharField(max_length=20, choices=STATUS)
    stemmingssoort = models.CharField(max_length=20, null=True, blank=True, choices=STEMMINGSSOORT)
    voorsteltext = models.TextField(null=True, blank=True)
    besluittext = models.TextField(null=True)
    aangemaaktop = models.DateTimeField(auto_now_add=False)
    gewijzigdop = models.DateTimeField(auto_now=False)
    opmerking = models.TextField(null=True, blank=True)

    #zaken = models.ManyToManyField('Zaak', through='Status')  # Status.besluit not in tsv

    def __unicode__(self):
        return self.id

    class Meta:
        verbose_name_plural = u"Besluiten"


class Kamerstukdossier(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    titel = models.TextField(null=True, blank=True)
    citeertitel = models.CharField(max_length=200, null=True, blank=True)
    alias = models.CharField(max_length=200, null=True, blank=True)
    nummer = models.IntegerField()
    toevoeging = models.CharField(max_length=10, null=True, blank=True)
    hoogstevolgnummer = models.IntegerField()
    afgesloten = models.NullBooleanField()
    kamer = models.CharField(max_length=30, choices=KAMER)
    aangemaaktop = models.DateTimeField(auto_now_add=False)
    gewijzigdop = models.DateTimeField(auto_now=False)

    def __unicode__(self):
        return "%s %s" % (self.nummer, self.toevoeging if self.toevoeging else '')


class Document(models.Model):
    KAMER = [
        ('2', 'Tweede Kamer'),
        ('3', 'Eerste Kamer en Tweede Kamer'),
        ('4', '4 Verenigde Vergadering?'),
    ]

    id = models.CharField(max_length=36, primary_key=True)
    documentnummer = models.CharField(max_length=10, unique=True)
    kamerstukdossier = models.ForeignKey(Kamerstukdossier, null=True, blank=True, related_name='documenten')
    titel = models.TextField(null=True, blank=True)
    soort = models.CharField(max_length=100, null=True)
    onderwerp = models.TextField()
    datum = models.DateTimeField()
    volgnummer = models.IntegerField()
    vergaderjaar = models.CharField(max_length=10)
    kamer = models.IntegerField(choices=KAMER)
    aangemaaktop = models.DateTimeField(auto_now_add=False)
    gewijzigdop = models.DateTimeField(auto_now=False)
    citeertitel = models.CharField(max_length=200, null=True, blank=True)
    alias = models.CharField(max_length=200, null=True, blank=True)
    datumregistratie = models.DateTimeField()
    datumontvangst = models.DateTimeField(null=True, blank=True)
    aanhangselnummer = models.IntegerField(null=True, blank=True)
    kenmerkafzender = models.CharField(max_length=20, null=True, blank=True)
    contenttype = models.CharField(max_length=30, null=True, blank=True)

    bijlagen = models.ManyToManyField('self', symmetrical=False, related_name="bijlagen_van")
    vervanging = models.ManyToManyField('self', symmetrical=False, related_name="vervanger")

    def __unicode__(self):
        return self.documentnummer

    class Meta:
        verbose_name_plural = u"Documenten"


class Documentversie(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    document = models.ForeignKey(Document, related_name='documentversies')
    status = models.CharField(max_length=50, choices=STATUS)
    versienummer = models.IntegerField()
    bestandsgrootte = models.IntegerField()
    extensie = models.CharField(max_length=100)
    datum = models.DateTimeField()
    aangemaaktop = models.DateTimeField(auto_now_add=False)
    gewijzigdop = models.DateTimeField(auto_now=False)

    class Meta:
        verbose_name_plural = u'Documentversies'
        ordering = ['versienummer']


class DocumentActor(models.Model):
    RELATIE = [
        ("Afzender", "Afzender"),
        ("Eerste ondertekenaar", "Eerste ondertekenaar"),
        ("Geaddresseerde", "Geaddresseerde"),
        ("Mede afzender", "Mede afzender"),
        ("Mede namens", "Mede namens"),
        ("Mede ondertekenaar", "Mede ondertekenaar"),
        ("Namens", "Namens"),
    ]

    id = models.CharField(max_length=36, primary_key=True)
    document = models.ForeignKey(Document, related_name='documentactoren')
    naam = models.CharField(max_length=100)
    functie = models.CharField(max_length=100, null=True, blank=True)
    partij = models.CharField(max_length=100, null=True, blank=True)
    relatie = models.CharField(max_length=100, choices=RELATIE)
    aangemaaktop = models.DateTimeField(auto_now_add=False)
    gewijzigdop = models.DateTimeField(auto_now=False)
    politician = models.ForeignKey(Politician, null=True, on_delete=models.SET_NULL)
    party = models.ForeignKey(Party, null=True, on_delete=models.SET_NULL)


    class Meta:
        verbose_name_plural = u'DocumentActoren'


class Zaal(models.Model):
    syscode = models.IntegerField(primary_key=True)
    code = models.CharField(max_length=10, null=True, blank=True)
    naam = models.CharField(max_length=100)
    objectcode = models.CharField(max_length=10, null=True, blank=True)
    objectnaam = models.CharField(max_length=100, null=True, blank=True)
    soort = models.CharField(max_length=100, null=True, blank=True)
    aantaldeelnemers = models.IntegerField(null=True, blank=True)
    publieksplekken = models.IntegerField(null=True, blank=True)
    toelichting = models.TextField(null=True, blank=True)
    vergaderingcode = models.CharField(max_length=10, null=True, blank=True)
    vergaderingnaam = models.CharField(max_length=100, null=True, blank=True)
    mogelijkheidcatering = models.NullBooleanField()
    aangemaaktop = models.DateTimeField(auto_now_add=False)
    gewijzigdop = models.DateTimeField(auto_now=False)

    def __unicode__(self):
        return self.naam

    class Meta:
        verbose_name_plural = u"Zalen"


class Reservering(models.Model):
    syscode = models.IntegerField(primary_key=True)
    nummer = models.DecimalField(max_digits=10, decimal_places=2, unique=True)
    standaardcode = models.CharField(max_length=100, null=True, blank=True)
    standaardnaam = models.CharField(max_length=100, null=True, blank=True)
    vergadersoortcode = models.CharField(max_length=100, null=True, blank=True)
    vergadersoortnaam = models.CharField(max_length=100, null=True, blank=True)
    startdatumtijd = models.DateTimeField(null=True, blank=True)
    einddatumtijd = models.DateTimeField(null=True, blank=True)
    omschrijving = models.CharField(max_length=100, null=True, blank=True)
    meldercode = models.CharField(max_length=100, null=True, blank=True)
    meldernaam = models.CharField(max_length=100, null=True, blank=True)
    griffiercode = models.CharField(max_length=100, null=True, blank=True)
    griffiernaam = models.CharField(max_length=100, null=True, blank=True)
    voortouwcommissiecode = models.CharField(max_length=100, null=True, blank=True)
    voortouwcommissienaam = models.CharField(max_length=100, null=True, blank=True)
    initiatorcode = models.CharField(max_length=100, null=True, blank=True)
    initiatornaam = models.CharField(max_length=100, null=True, blank=True)
    toelichtingen = models.CharField(max_length=100, null=True, blank=True)
    aanmakercode = models.CharField(max_length=100, null=True, blank=True)
    aanmakernaam = models.CharField(max_length=100, null=True, blank=True)
    aantalpersonen = models.IntegerField(null=True, blank=True)
    aanvragercode = models.CharField(max_length=100, null=True, blank=True)
    aanvragernaam = models.CharField(max_length=100, null=True, blank=True)
    datumgemeld = models.DateTimeField(null=True, blank=True)
    statuscode = models.CharField(max_length=100, null=True, blank=True)
    statusnaam = models.CharField(max_length=100, null=True, blank=True)
    activiteitsoortcode = models.CharField(max_length=100, null=True, blank=True)
    activiteitsoortnaam = models.CharField(max_length=100, null=True, blank=True)
    toelichting = models.CharField(max_length=100, null=True, blank=True)
    catering = models.IntegerField(null=True, blank=True)
    activiteitnummer = models.CharField(max_length=10)
    aangemaaktop = models.DateTimeField(auto_now_add=False)
    gewijzigdop = models.DateTimeField(auto_now=False)
    zaal = models.ForeignKey(Zaal, null=True, related_name='reserveringen')

    def __unicode__(self):
        return "Reservering voor zaal: %s" % self.zaal


class Zaak(models.Model):
    SOORT = [
        ("Amendement", "Amendement"),
        ("Begroting", "Begroting"),
        ("Brief commissie", "Brief commissie"),
        ("Brief Kamer", "Brief Kamer"),
        ("Brief regering", "Brief regering"),
        ("Brief van lid/fractie/commissie", "Brief van lid/fractie/commissie"),
        ("EU-voorstel", "EU-voorstel"),
        ("Initiatiefnota", "Initiatiefnota"),
        ("Initiatiefwetgeving", "Initiatiefwetgeving"),
        ("Interpellatie", "Interpellatie"),
        ("Mondelinge vragen", "Mondelinge vragen"),
        ("Motie", "Motie"),
        ("Nationale ombudsman", "Nationale ombudsman"),
        ("Nota naar aanleiding van het (nader) verslag", "Nota naar aanleiding van het (nader) verslag"),
        ("Nota van wijziging", "Nota van wijziging"),
        ("Overig", "Overig"),
        ("Parlementair onderzoeksrapport", "Parlementair onderzoeksrapport"),
        ("PKB/Structuurvisie", "PKB/Structuurvisie"),
        ("Rapport/brief Algemene Rekenkamer", "Rapport/brief Algemene Rekenkamer"),
        ("Rondvraagpunt procedurevergadering", "Rondvraagpunt procedurevergadering"),
        ("Schriftelijke vragen", "Schriftelijke vragen"),
        ("Verdrag", "Verdrag"),
        ("Verzoek bij regeling van werkzaamheden", "Verzoek bij regeling van werkzaamheden"),
        ("Verzoekschrift", "Verzoekschrift"),
        ("Voordrachten en benoemingen", "Voordrachten en benoemingen"),
        ("Wetgeving", "Wetgeving"),
        ("Wijziging RvO", "Wijziging RvO"),
        ("Wijzigingen voorgesteld door de regering", "Wijzigingen voorgesteld door de regering"),
    ]

    id = models.CharField(max_length=36, primary_key=True)
    nummer = models.CharField(max_length=10, unique=True)
    soort = models.CharField(max_length=50, choices=SOORT)
    titel = models.TextField(null=True, blank=True)
    citeertitel = models.CharField(max_length=400, null=True, blank=True)
    alias = models.CharField(max_length=400, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS)
    onderwerp = models.TextField()
    datumstart = models.DateTimeField()
    kamer = models.CharField(max_length=30, choices=KAMER)
    grondslagvoorhang = models.CharField(max_length=700, null=True, blank=True)
    termijn = models.DateTimeField(null=True, blank=True)
    vergaderjaar = models.CharField(max_length=9)
    kamerstukdossier = models.ForeignKey(Kamerstukdossier, null=True, blank=True, related_name='zaken')
    volgnummer = models.IntegerField()
    huidigebehandelstatus = models.CharField(max_length=1, null=True, blank=True)
    afgedaan = models.BooleanField()
    grootproject = models.NullBooleanField()
    aangemaaktop = models.DateTimeField(auto_now_add=False)
    gewijzigdop = models.DateTimeField(auto_now=False)
    agendapuntzakenvolgorde = models.IntegerField(null=True, blank=True)

    zieook = models.ManyToManyField('self', symmetrical=False, related_name="zieook2")
    overig = models.ManyToManyField('self', symmetrical=False, related_name="overig2")  # symmetrisch?
    vervanging = models.ManyToManyField('self', symmetrical=False, related_name="vervanger")
    besluiten = models.ManyToManyField(Besluit, related_name='zaken')
    activiteiten = models.ManyToManyField(Activiteit, related_name='zaken')
    documenten = models.ManyToManyField(Document, related_name='zaken')

    def __unicode__(self):
        return self.citeertitel if self.citeertitel else self.id

    class Meta:
        verbose_name_plural = u"Zaken"


class ZaakActor(models.Model):
    RELATIE = [
        ("Rapporteur", "Rapporteur"),
        ("Gericht aan", "Gericht aan"),
        ("Medeindiener", "Medeindiener"),
        ("Volgcommissie", "Volgcommissie"),
        ("Voortouwcommissie", "Voortouwcommissie"),
        ("Relatie", "Relatie"),
        ("Indiener", "Indiener"),
    ]

    id = models.CharField(max_length=36, primary_key=True)
    zaak = models.ForeignKey(Zaak)
    naam = models.CharField(max_length=150)
    functie = models.CharField(max_length=150, null=True)
    partij = models.CharField(max_length=50, null=True)
    relatie = models.CharField(max_length=50, choices=RELATIE)
    aangemaaktop = models.DateTimeField(auto_now_add=False)
    gewijzigdop = models.DateTimeField(auto_now=False)
    actorabreviatedname = models.CharField(max_length=20, null=True)
    politician = models.ForeignKey(Politician, null=True, on_delete=models.SET_NULL)
    party = models.ForeignKey(Party, null=True, on_delete=models.SET_NULL)

    def __unicode__(self):
        return '%s van %s (%s)' % (self.naam, self.partij, self.relatie)

    class Meta:
        verbose_name_plural = u"Zaak Actoren"


class Status(models.Model):
    SOORT = [
        ("Aangenomen", "Aangenomen"),
        ("Aangehouden", "Aangehouden"),
        ("Goedgekeurd", "Goedgekeurd"),
        ("Ingetrokken", "Ingetrokken"),
        ("Overgenomen", "Overgenomen"),
        ("Controversieel", "Controversieel"),
        ("Komt in gesprek", "Komt in gesprek"),
        ("Decharge verleend", "Decharge verleend"),
        ("Komt in stemmingen", "Komt in stemmingen"),
        ("Komt in werkbezoek", "Komt in werkbezoek"),
        ("Afgedaan door Kamer", "Afgedaan door Kamer"),
        ("Komt in notaoverleg", "Komt in notaoverleg"),
        ("Geschorst / verdaagd", "Geschorst / verdaagd"),
        ("Komt in plenair debat", "Komt in plenair debat"),
        ("Extern advies gevraagd", "Extern advies gevraagd"),
        ("Stenogram doorgezonden", "Stenogram doorgezonden"),
        ("Afgedaan door commissie", "Afgedaan door commissie"),
        ("Komt in algemeen overleg", "Komt in algemeen overleg"),
        ("Komt in begrotingsoverleg", "Komt in begrotingsoverleg"),
        ("Komt in wetgevingsoverleg", "Komt in wetgevingsoverleg"),
        ("Niet (meer) controversieel", "Niet (meer) controversieel"),
        ("Zonder stemming aangenomen", "Zonder stemming aangenomen"),
        ("Komt in technische briefing", "Komt in technische briefing"),
        ("Komt in procedurevergadering", "Komt in procedurevergadering"),
        ("Voor kennisgeving aangenomen", "Voor kennisgeving aangenomen"),
        ("Commissiebrief nog niet beantwoord", "Commissiebrief nog niet beantwoord"),
        ("Komt in regeling van werkzaamheden", "Komt in regeling van werkzaamheden"),
        ("Aangemeld voor plenaire behandeling", "Aangemeld voor plenaire behandeling"),
        ("Wordt gerelateerd aan plenair debat", "Wordt gerelateerd aan plenair debat"),
        ("Komt in hoorzitting/rondetafelgesprek", "Komt in hoorzitting/rondetafelgesprek"),
        ("Afgevoerd van de stand der werkzaamheden", "Afgevoerd van de stand der werkzaamheden"),
        ("Wordt gerelateerd aan commissieactiviteit", "Wordt gerelateerd aan commissieactiviteit"),
        ("Proces afgebroken: relateren met andere zaak", "Proces afgebroken: relateren met andere zaak"),
        ("Niet controversieel verklaard door de commissie", "Niet controversieel verklaard door de commissie"),
        ("Besloten overeenkomstig het voorstel van de commissie", "Besloten overeenkomstig het voorstel van de commissie"),
        ("Voorstel aan Kamer gedaan om controversieel te verklaren", "Voorstel aan Kamer gedaan om controversieel te verklaren"),
        ("Voorstel aan Kamer gedaan tot aanwijzing als groot project", "Voorstel aan Kamer gedaan tot aanwijzing als groot project"),
        ("Soort", "Soort"),
        ("Voorstel aan de Kamer gedaan tot beëindiging als groot project", "Voorstel aan de Kamer gedaan tot beëindiging als groot project"),
        ("Vervallen", "Vervallen"),
        ("Verworpen", "Verworpen"),
    ]

    id = models.CharField(max_length=36, primary_key=True)
    zaak = models.ForeignKey(Zaak, related_name="status2", null=True, blank=True)
    besluit = models.ForeignKey(Besluit, related_name='status2', null=True, blank=True)
    soort = models.CharField(max_length=100)
    datum = models.DateTimeField()
    aangemaaktop = models.DateTimeField(auto_now_add=False)
    gewijzigdop = models.DateTimeField(auto_now=False)

    def __unicode__(self):
        return self.id

    class Meta:
        verbose_name_plural = u"Statussen"


class Stemming(models.Model):
    SOORT = [
        ("Niet deelgenomen", "Niet deelgenomen"),
        ("Tegen", "Tegen"),
        ("Voor", "Voor"),
    ]

    id = models.CharField(max_length=36, primary_key=True)
    besluit = models.ForeignKey(Besluit, related_name='stemmingen')
    soort = models.CharField(max_length=20, choices=SOORT)
    fractiegrootte = models.IntegerField()
    fractiestemmen = models.IntegerField(null=True, blank=True)  # niet in tsv
    actornaam = models.CharField(max_length=50)
    actorpartij = models.CharField(max_length=20)
    vergissing = models.NullBooleanField()
    aangemaaktop = models.DateTimeField(auto_now_add=False)
    gewijzigdop = models.DateTimeField(auto_now=False)
    sid_actorlid = models.CharField(max_length=70, null=True, blank=True)
    sid_actorfractie = models.CharField(max_length=70)

    def __unicode__(self):
        return self.id

    class Meta:
        verbose_name_plural = u"Stemmingen"
