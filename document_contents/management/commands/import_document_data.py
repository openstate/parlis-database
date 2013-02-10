import os
import codecs

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
                    DocumentContent(
                        document_id=filename[:-4],
                        content=file.read()
                    ).save()
                except:
                    print file.read()
