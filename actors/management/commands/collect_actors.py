from django.core.management.base import BaseCommand

from core.models import DocumentActor, ZaakActor, ActiviteitActor
from actors.models import Party, Politician


class Command(BaseCommand):
    help = 'collects parties'

    def handle(self, *args, **options):

        #TODO: merge politicians like (E.W. Dekker, Dekker, E.W. and Dekker)

        print "DocumtentActors"
        for actor in DocumentActor.objects.all():
            if actor.partij:
                party, created = Party.objects.get_or_create(name=actor.partij)
                actor.party = party

            if actor.naam:
                politician, created = Politician.objects.get_or_create(name=actor.naam)
                actor.politician = politician

            actor.save()

        print "ZaakActors"
        for actor in ZaakActor.objects.all():
            if actor.partij:
                party, created = Party.objects.get_or_create(name=actor.partij)
                actor.party = party

            if actor.naam and not actor.actorabreviatedname:
                politician, created = Politician.objects.get_or_create(name=actor.naam)
                actor.politician = politician

            actor.save()

        print "ActiviteitActors"
        for actor in ActiviteitActor.objects.all():
            if actor.partij:
                party, created = Party.objects.get_or_create(name=actor.partij)
                actor.party = party

            if actor.naam:
                politician, created = Politician.objects.get_or_create(name=actor.naam)
                actor.politician = politician

            actor.save()
