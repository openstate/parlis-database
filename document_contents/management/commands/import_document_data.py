import os
import codecs
from pprint import pprint

from django.core.management.base import BaseCommand, CommandError

from document_contents.models import DocumentContent


class Command(BaseCommand):
    args = '<folder>'
    help = 'Imports document content'

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Not the right amount of arguments')

        for filename in os.listdir(args[0]):
            with codecs.open(os.path.join(args[0], filename), 'r', "utf-8") as file:
                try:
                    data = file.read().decode('utf-8').strip()
                except Exception as e:
                    print e
                    print filename
                    raise

                try:
                    DocumentContent(
                        document_id=filename[:-4],
                        content=data
                    ).save()
                except Exception as e:
                    print e
                    pprint(filename[:-4])
                    pprint(data[:140])

