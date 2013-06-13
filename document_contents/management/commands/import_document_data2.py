import os
import codecs
import subprocess
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

            filepath = os.path.join(args[0], filename)
            txt_filepath = os.path.join(args[0], 'txt', filename) + '.txt'

            if not os.path.exists(txt_filepath):
                subprocess.call(["pdftotext", '-q', filepath, txt_filepath])
            try:
                with codecs.open(txt_filepath, 'r', "utf-8") as file:
                    try:
                        data = file.read().encode('utf-8').strip()
                    except Exception as e:
                        print e
                        print filename
                        raise

                    try:
                        i, created = DocumentContent.objects.get_or_create(
                            document_id=filename,
                            content=data
                        )
                    except Exception as e:
                        print e
                        pprint(filename)
                        pprint(data[:140])
            except IOError as e:
                print filename
                pass



