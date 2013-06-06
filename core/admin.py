from django.contrib import admin

from .models import Zaak, Activiteit, Agendapunt, Besluit, Document, Stemming, Kamerstukdossier, Status, ActiviteitActor, ZaakActor, Zaal, Reservering, \
    Documentactor, Documentversie
from simpleEV.models import DocumentLabels


class AgendapuntInline(admin.TabularInline):
    model = Agendapunt
    ordering = ['volgorde']
    extra = 0
    raw_id_fields = ['besluiten', 'documenten', 'zaken']


class ActiviteitActorsInline(admin.TabularInline):
    model = ActiviteitActor
    ordering = ['relatie', 'volgorde']
    extra = 0


class ActiviteitAdmin(admin.ModelAdmin):
    inlines = [
        AgendapuntInline,
        ActiviteitActorsInline,
    ]
    date_hierarchy = 'aanvangstijd'
    list_filter = ['kamer', 'vergaderjaar', 'soort', 'status', 'datumsoort']
    raw_id_fields = ['vervanging', 'documenten', 'voortzetting']


class ZaakActorsInline(admin.TabularInline):
    model = ZaakActor
    extra = 0


class ZaakAdmin(admin.ModelAdmin):
    inlines = [
        ZaakActorsInline,
    ]

    raw_id_fields = ['zieook', 'overig', 'vervanging', 'besluiten', 'documenten', 'activiteiten', 'kamerstukdossier']
    date_hierarchy = 'datumstart'
    list_filter = ['kamer', 'vergaderjaar', 'soort', 'status', 'afgedaan', 'grootproject']
    list_display = ['__unicode__', 'onderwerp', 'soort', 'status', 'kamerstukdossier', 'volgnummer', 'huidigebehandelstatus', 'afgedaan', 'grootproject']


class DocumentLabelsInline(admin.TabularInline):
    model = DocumentLabels
    extra = 0


class DocumentActorsInline(admin.TabularInline):
    model = Documentactor
    ordering = ['relatie']
    extra = 0


class DocumentVersiesInline(admin.TabularInline):
    model = Documentversie
    extra = 0
    ordering = ['versienummer']


class DocumentAdmin(admin.ModelAdmin):
    inlines = [
        DocumentLabelsInline,
        DocumentActorsInline,
        DocumentVersiesInline
    ]

    list_filter = ['kamer', 'vergaderjaar', 'soort', 'contenttype']
    list_display = ('documentnummer', 'kamerstukdossier', 'volgnummer', 'onderwerp', 'volgnummer', 'vergaderjaar', 'kamer', 'contenttype')
    date_hierarchy = 'datumregistratie'
    raw_id_fields = ['bijlagen', 'vervanging', 'kamerstukdossier']
    search_fields = ['id', 'documentnummer']



class ActiviteitActorAdmin(admin.ModelAdmin):
    list_filter = ['partij', 'relatie', 'functie']
    raw_id_fields = ['activiteit']
    search_fields = ['naam']


class StemmingAdmin(admin.ModelAdmin):
    list_filter = ['soort', 'vergissing', 'actorpartij']
    list_display = ['__unicode__', 'besluit', 'soort', 'fractiegrootte', 'fractiestemmen', 'actornaam', 'actorpartij', 'vergissing']
    raw_id_fields = ['besluit']


class StatusAdmin(admin.ModelAdmin):
    date_hierarchy = 'datum'
    list_filter = ['soort']
    list_display = ['__unicode__', 'zaak', 'besluit', 'soort', 'datum']
    raw_id_fields = ['zaak', 'besluit']


class ZaakActorAdmin(admin.ModelAdmin):
    list_filter = ['partij', 'relatie', 'functie']
    list_display = ['__unicode__', 'zaak', 'naam', 'partij', 'functie', 'relatie', ]
    raw_id_fields = ['zaak']
    search_fields = ['naam']


class BesluitAdmin(admin.ModelAdmin):
    list_filter = ['status', 'soort', 'stemmingssoort']
    list_display = ['__unicode__', 'besluittext', 'status', 'soort', 'stemmingssoort']


class ZaakInlineAdmin(admin.TabularInline):
    raw_id_fields = ['zieook', 'overig', 'vervanging', 'besluiten', 'documenten', 'activiteiten', 'kamerstukdossier']
    extra = 0
    model = Zaak


class DocumentInlineAdmin(admin.TabularInline):
    raw_id_fields = ['bijlagen', 'vervanging', 'kamerstukdossier']
    extra = 0
    model = Document


class KamerstukdossierAdmin(admin.ModelAdmin):
    inlines = [
        ZaakInlineAdmin,
        DocumentInlineAdmin
    ]
    list_filter = ['kamer', 'afgesloten']
    list_display = ['__unicode__', 'hoogstevolgnummer', 'titel', 'afgesloten', 'kamer']
    search_fields = ['nummer']

admin.site.register(Zaak, ZaakAdmin)
admin.site.register(Activiteit, ActiviteitAdmin)
admin.site.register(Besluit, BesluitAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Stemming, StemmingAdmin)
admin.site.register(Kamerstukdossier, KamerstukdossierAdmin)
admin.site.register(Status, StatusAdmin)
admin.site.register(ActiviteitActor, ActiviteitActorAdmin)
admin.site.register(ZaakActor, ZaakActorAdmin)
admin.site.register(Zaal)#, ZaalAdmin)
admin.site.register(Reservering)#, ReserveringAdmin)
admin.site.register(Documentactor)#, DocumentactorAdmin)
admin.site.register(Documentversie)#, DocumentversieAdmin)
