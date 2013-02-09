from django.contrib import admin

from .models import Zaak, Activiteit, Agendapunt, Besluit, Document, Stemming, Kamerstukdossier, Status, ActiviteitActor, ZaakActor


class AgendapuntInline(admin.TabularInline):
    model = Agendapunt
    ordering = ['volgorde']
    extra = 0


class ActiviteitAdmin(admin.ModelAdmin):
    inlines = [
        AgendapuntInline,
    ]
    date_hierarchy = 'aanvangstijd'
    list_filter = ['kamer', 'vergaderjaar', 'soort', 'status', 'datumsoort']


class ZaakAdmin(admin.ModelAdmin):
    filter_vertical = ['zieook', 'overig', 'vervanging', 'besluiten', 'documenten', 'activiteiten']
    date_hierarchy = 'datumstart'
    list_filter = ['kamer', 'vergaderjaar', 'soort', 'status']


class DocumentAdmin(admin.ModelAdmin):
    list_filter = ['kamer', 'vergaderjaar', 'soort', 'contenttype']
    list_display = ('__unicode__', 'titel', 'volgnummer')
    date_hierarchy = 'datumregistratie'


class ActiviteitActorAdmin(admin.ModelAdmin):
    list_filter = ['partij', 'relatie', 'functie']


class StemmingAdmin(admin.ModelAdmin):
    list_filter = ['soort', 'vergissing', 'actorpartij']
    list_display = ['__unicode__', 'besluit', 'soort', 'fractiegrootte', 'fractiestemmen', 'actornaam', 'actorpartij', 'vergissing']


class StatusAdmin(admin.ModelAdmin):
    date_hierarchy = 'datum'
    list_filter = ['soort']
    list_display = ['__unicode__', 'zaak', 'besluit', 'soort', 'datum']


class ZaakActorAdmin(admin.ModelAdmin):
    list_filter = ['partij', 'relatie', 'functie']
    list_display = ['__unicode__', 'zaak', 'naam', 'partij', 'functie', 'relatie', ]


class BesluitAdmin(admin.ModelAdmin):
    list_filter = ['status', 'soort', 'stemmingssoort']
    list_display = ['__unicode__', 'besluittext', 'status', 'soort', 'stemmingssoort']


admin.site.register(Zaak, ZaakAdmin)
admin.site.register(Activiteit, ActiviteitAdmin)
admin.site.register(Besluit, BesluitAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Stemming, StemmingAdmin)
admin.site.register(Kamerstukdossier)
admin.site.register(Status, StatusAdmin)
admin.site.register(ActiviteitActor, ActiviteitActorAdmin)
admin.site.register(ZaakActor, ZaakActorAdmin)
