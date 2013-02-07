
from django.db import models

STATUS = [
    ('Vrijgegeven', 'Vrijgegeven'),
    ('Besluit', 'Besluit'),
]

SOORT = [
    ("Amendement", "Amendement"),
    ("Begroting", "Begroting"),
    ("Brief commissie", "Brief commissie"),
    ("Brief Kamer", "Brief Kamer"),
    ("Brief regering", "Brief regering"),
    ("Brief van lid/fractie/commissie", "Brief van lid/fractie/commissie"),
    ("Initiatiefwetgeving", "Initiatiefwetgeving"),
    ("Interpellatie", "Interpellatie"),
    ("Mondelinge vragen", "Mondelinge vragen"),
    ("Motie", "Motie"),
    ("Overig", "Overig"),
    ("Rapport/brief Algemene Rekenkamer", "Rapport/brief Algemene Rekenkamer"),
    ("Rondvraagpunt procedurevergadering", "Rondvraagpunt procedurevergadering"),
    ("Schriftelijke vragen", "Schriftelijke vragen"),
    ("Verdrag", "Verdrag"),
    ("Verzoek bij regeling van werkzaamheden", "Verzoek bij regeling van werkzaamheden"),
    ("Verzoekschrift", "Verzoekschrift"),
    ("Voordrachten en benoemingen", "Voordrachten en benoemingen"),
    ("Wetgeving", "Wetgeving"),
]

KAMER = [
    ('Eerste Kamer en Tweede Kamer', 'Eerste Kamer en Tweede Kamer'),
    ('Tweede Kamer', 'Tweede Kamer'),
]


class Activiteit(models.Model):
    id = models.CharField(max_length=114, primary_key=True)
    nummer = models.CharField(max_length=10)
    onderwerp = models.TextField()
    soort = models.CharField(max_length=50, choices=SOORT)
    datumsoort = models.CharField(max_length=50)
    datum = models.DateTimeField(null=True, blank=True)  # Niet in tsv
    aanvangstijd = models.DateTimeField(null=True, blank=True)
    eindtijd = models.DateTimeField(null=True, blank=True)
    locatie = models.CharField(max_length=100, null=True, blank=True)
    besloten = models.BooleanField()  # Niet in access?!
    status = models.CharField(max_length=15, choices=STATUS)
    vergaderjaar = models.CharField(max_length=9, null=True, blank=True)
    kamer = models.CharField(max_length=30, choices=KAMER)
    noot = models.TextField(null=True, blank=True)
    aangemaaktop = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    gewijzigdop = models.DateTimeField(null=True, blank=True, auto_now=True)
    vrsnummer = models.IntegerField(blank=True, null=True)
    voortouwnaam = models.CharField(max_length=150, blank=True)
    voortouwafkorting = models.CharField(max_length=7, blank=True)
    voortouwkortenaam = models.CharField(max_length=50, blank=True)

    vervanging = models.ManyToManyField('self', symmetrical=False, related_name="vervanger")
    voortzetting = models.ManyToManyField('self', symmetrical=False, related_name="voortzetting_van")
    documenten = models.ManyToManyField('Document')
    reservering = models.ManyToManyField('Reservering')

    def __unicode__(self):
        return self.onderwerp

    class Meta:
        verbose_name_plural = u"Activiteiten"


class Agendapunt(models.Model):
    id = models.CharField(max_length=114, primary_key=True)
    nummer = models.CharField(max_length=10)
    activiteit = models.ForeignKey(Activiteit)
    onderwerp = models.TextField()
    aanvangstijd = models.DateTimeField(null=True, blank=True)
    eindtijd = models.DateTimeField(null=True, blank=True)
    volgorde = models.IntegerField(null=True, blank=True)
    rubriek = models.CharField(max_length=200, null=True, blank=True)
    noot = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS)
    aangemaaktop = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    gewijzigdop = models.DateTimeField(null=True, blank=True, auto_now=True)
    besluiten = models.ManyToManyField('Besluit')
    documenten = models.ManyToManyField('Document')

    def __unicode__(self):
        return self.onderwerp

    class Meta:
        verbose_name_plural = u"Agendapunten"


class Besluit(models.Model):
    STEMMINGSSOORT = [
        ("Hoofdelijk", "Hoofdelijk"),
        ("Met handopsteken", "Met handopsteken"),
        ("StemmingsSoort", "StemmingsSoort"),
        ("Zonder stemming", "Zonder stemming"),
    ]

    id = models.CharField(max_length=114, primary_key=True)
    soort = models.CharField(max_length=765)
    status = models.CharField(max_length=20, choices=STATUS)
    stemmingssoort = models.CharField(max_length=20, null=True, blank=True, choices=STEMMINGSSOORT)
    voorsteltext = models.TextField(null=True, blank=True)
    besluittext = models.TextField()
    aangemaaktop = models.DateTimeField(auto_now_add=True)
    gewijzigdop = models.DateTimeField(auto_now=True)
    opmerking = models.TextField(null=True, blank=True)

    zaken = models.ManyToManyField('Zaak', through='Status')

    def __unicode__(self):
        if not self.besluittext:
            return "leeg"
        return self.besluittext

    class Meta:
        verbose_name_plural = u"Besluiten"


class Kamerstukdossier(models.Model):
    id = models.CharField(max_length=114, primary_key=True)
    titel = models.TextField(null=True, blank=True)
    citeertitel = models.CharField(max_length=400, null=True, blank=True)
    alias = models.CharField(max_length=400, null=True, blank=True)
    nummer = models.IntegerField()
    toevoeging = models.CharField(max_length=10, null=True, blank=True)
    hoogstevolgnummer = models.IntegerField(null=True, blank=True)
    afgesloten = models.IntegerField(null=True, blank=True)
    kamer = models.CharField(max_length=50, null=True, blank=True)
    aangemaaktop = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    gewijzigdop = models.DateTimeField(null=True, blank=True, auto_now=True)

    def __unicode__(self):
        if not self.titel:
            return "leeg"
        return self.titel


class Document(models.Model):
    KAMER = [
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
    ]

    id = models.CharField(max_length=114, primary_key=True)
    documentnummer = models.TextField()
    kamerstukdossier = models.ForeignKey(Kamerstukdossier, null=True, blank=True)  # Mist in tsv
    titel = models.TextField(null=True, blank=True)
    soort = models.CharField(max_length=400, null=True, blank=True)
    onderwerp = models.TextField()
    datum = models.DateTimeField()
    volgnummer = models.IntegerField(null=True, blank=True)
    vergaderjaar = models.CharField(max_length=10)
    kamer = models.IntegerField(choices=KAMER)
    aangemaaktop = models.DateTimeField(auto_now_add=True)
    gewijzigdop = models.DateTimeField(auto_now=True)
    citeertitel = models.CharField(max_length=400, null=True, blank=True)
    alias = models.CharField(max_length=400, null=True, blank=True)
    datumregistratie = models.DateTimeField(null=True, blank=True)
    datumontvangst = models.DateTimeField(null=True, blank=True)
    aanhangselnummer = models.IntegerField(null=True, blank=True)
    kenmerkafzender = models.CharField(max_length=20, null=True, blank=True)
    contenttype = models.CharField(max_length=20, null=True, blank=True)

    bijlagen = models.ManyToManyField('self', symmetrical=False, related_name="bijlage_van")
    vervanging = models.ManyToManyField('self', symmetrical=False, related_name="vervanger")

    def __unicode__(self):
        if not self.titel:
            return "leeg"
        return self.titel

    class Meta:
        verbose_name_plural = u"Documenten"


class Zaal(models.Model):
    syscode = models.IntegerField(primary_key=True)
    code = models.CharField(max_length=10)
    naam = models.CharField(max_length=100)
    objectcode = models.CharField(max_length=10)
    objectnaam = models.CharField(max_length=100)
    soort = models.CharField(max_length=100)
    aantaldeelnemers = models.IntegerField()
    publieksplekken = models.IntegerField()
    toelichting = models.TextField()
    vergaderingcode = models.CharField(max_length=10)
    vergaderingnaam = models.CharField(max_length=100)
    mogelijkheidcatering = models.IntegerField()

    def __unicode__(self):
        return self.naam

    class Meta:
        verbose_name_plural = u"Zalen"


class Reservering(models.Model):
    syscode = models.IntegerField(primary_key=True)
    nummer = models.CharField(max_length=100)
    standaardcode = models.CharField(max_length=100)
    standaardnaam = models.CharField(max_length=100)
    vergadersoortcode = models.CharField(max_length=100)
    vergadersoortnaam = models.CharField(max_length=100)
    startdatumtijd = models.DateTimeField()
    einddatumtijd = models.DateTimeField()
    omschrijving = models.CharField(max_length=100)
    meldercode = models.CharField(max_length=100)
    meldernaam = models.CharField(max_length=100)
    griffiercode = models.CharField(max_length=100)
    griffiernaam = models.CharField(max_length=100)
    voortouwcommissiecode = models.CharField(max_length=100)
    voortouwcommissienaam = models.CharField(max_length=100)
    initiatorcode = models.CharField(max_length=100)
    initiatornaam = models.CharField(max_length=100)
    toelichtingen = models.CharField(max_length=100)
    aanmakercode = models.CharField(max_length=100)
    aanmakernaam = models.CharField(max_length=100)
    aantalpersonen = models.IntegerField()
    aanvragercode = models.CharField(max_length=100)
    aanvragernaam = models.CharField(max_length=100)
    datumgemeld = models.DateTimeField()
    statuscode = models.CharField(max_length=100)
    statusnaam = models.CharField(max_length=100)
    activiteitsoortcode = models.CharField(max_length=100)
    activiteitsoortnaam = models.CharField(max_length=100)
    toelichting = models.CharField(max_length=100)
    catering = models.IntegerField()
    activiteitnummer = models.CharField(max_length=10)
    zaalsyscode = models.ForeignKey(Zaal)

    def __unicode__(self):
        return "Reservering voor zaal", self.zaal


class Zaak(models.Model):
    id = models.CharField(max_length=114, primary_key=True)
    nummer = models.CharField(max_length=10)
    soort = models.CharField(max_length=50, choices=SOORT)
    titel = models.TextField(null=True, blank=True)
    citeertitel = models.CharField(max_length=400, null=True, blank=True)
    alias = models.CharField(max_length=400, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS)
    onderwerp = models.TextField()
    datumstart = models.DateTimeField()
    kamer = models.CharField(max_length=50, choices=KAMER)
    grondslagvoorhang = models.TextField(null=True, blank=True)
    termijn = models.DateTimeField(null=True, blank=True)
    vergaderjaar = models.CharField(max_length=9)
    kamerstukdossier = models.ForeignKey(Kamerstukdossier, null=True, blank=True)  # Niet in tsv
    volgnummer = models.IntegerField()
    huidigebehandelstatus = models.CharField(max_length=1, null=True, blank=True)
    afgedaan = models.BooleanField()
    grootproject = models.BooleanField()
    aangemaaktop = models.DateTimeField(auto_now_add=True)
    gewijzigdop = models.DateTimeField(auto_now=True)

    zieook = models.ManyToManyField('self')
    overig = models.ManyToManyField('self')  # symmetrisch?
    vervanging = models.ManyToManyField('self', symmetrical=False, related_name="vervanger")
    besluiten = models.ManyToManyField(Besluit)
    activiteiten = models.ManyToManyField(Activiteit)

    def __unicode__(self):
        return self.onderwerp

    class Meta:
        verbose_name_plural = u"Zaken"


class Zaakbesluitrelaties(models.Model):
    zaak = models.ForeignKey('Zaak')  # Field name made lowercase.
    besluit = models.ForeignKey('Besluit')  # Field name made lowercase.

    class Meta:
        db_table = u'accessdb_zaak_besluiten'


class Status(models.Model):
    id = models.CharField(max_length=114, primary_key=True)
    zaak = models.ForeignKey(Zaak, related_name="status2")
    besluit = models.ForeignKey(Besluit, related_name='status2', null=True, blank=True)
    soort = models.TextField(null=True, blank=True)
    datum = models.DateTimeField()
    aangemaaktop = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    gewijzigdop = models.DateTimeField(null=True, blank=True, auto_now=True)

    def __unicode__(self):
        return self.soort

    class Meta:
        verbose_name_plural = u"Statussen"


class Stemming(models.Model):
    id = models.CharField(max_length=114, primary_key=True)
    besluit = models.ForeignKey('Besluit')
    soort = models.TextField(blank=True)
    fractiegrootte = models.IntegerField(null=True, blank=True)
    fractiestemmen = models.IntegerField(null=True, blank=True)
    actornaam = models.CharField(max_length=50, blank=True)
    actorpartij = models.CharField(max_length=50, blank=True)
    vergissing = models.IntegerField(null=True, blank=True)
    aangemaaktop = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    gewijzigdop = models.DateTimeField(null=True, blank=True, auto_now=True)
    sid_actorlid = models.CharField(max_length=70, null=True, blank=True)
    sid_actorfractie = models.CharField(max_length=70, blank=True)

    class Meta:
        verbose_name_plural = u"Stemmingen"
