import codecs
import csv

from django.core.management.base import BaseCommand, CommandError

from simpleEV.models import DocumentLabels, DocumentLabels2
from core.models import Document


class Command(BaseCommand):
    args = '<file>'
    help = 'Imports csv data from parlisapi'

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Not the right amount of arguments')

        with codecs.open(args[0], 'r') as file:
            DocumentLabels.objects.all().delete()
            DocumentLabels2.objects.all().delete()

            reader = csv.DictReader(file)

            for row in reader:
                try:
                    document = Document.objects.get(id=row['id'])
                except Document.DoesNotExist:
                    continue

                if document:
                    DocumentLabels(
                        document=document,
                        label1=row['first'],
                        label2=row['second'],
                        label3=row['third'],
                        label4=row['fourth'],
                        label5=row['fifth'],
                    ).save()

                    lookup = ['first', 'second', 'third', 'fourth', 'fifth']

                    for i in range(0, 5):
                        DocumentLabels2(
                            document=document,
                            label=row[lookup[i]],
                            volgorde=i,
                        ).save()
