
from django.core.management.base import BaseCommand, CommandError

from parlisapi.import_data import tsv_import


class Command(BaseCommand):
    args = '<folder>'
    help = 'Imports tsv data from parlisapi'

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Not the right amount of arguments')

        tsv_import(args[0])
