import csv
import os
import re

from pprint import pprint

from decimal import Decimal

from dateutil import parser

from .dictdiffer import DictDiffer

from django.db.models import ManyToManyField
from django.db.models.fields import FieldDoesNotExist
from django.forms.models import model_to_dict



def tsv_import(folder):
    from parlis_definition import klasses

    for klass in klasses:
        klass(folder).execute()


class TsvImport(object):
    data = False
    folder = ''
    filename = ''
    model = None
    primary_key = 'id'
    should_exist = False

    def __init__(self, folder='', data=False):
        print "Importing %s" % self.filename

        if data:
            self.data = data

        self.folder = folder

    def getData(self, file):
        '''transform tsv data for processing

            #sample data
            >>> data = "Id\tField\n1234\tTekst With return\ris bad"

            #execute
            >>> getData(None, data)
            "id\tfield\n1234\tTekst With return\\nis bad"

        '''

        # lowercase fieldnames
        yield file.next().lower()

        #replace \r, needed for some long teksts which still contain \r
        for line in file:
            yield line.replace('\r', '\\n')

    def execute(self):
        if self.data:
            self.read(self.data)
        else:
            with open(os.path.join(self.folder, self.filename)) as IN:
                self.read(IN)

    def read(self, data):
        reader = csv.DictReader(self.getData(data), dialect=csv.excel_tab, restkey='rest')

        for row in reader:
            if 'rest' in row:
                print row['rest']
            self.handle(row)

    def handle(self, row):

        TIMESTAMP = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?$')

        #replace empty string with none
        for key, value in row.iteritems():

            if not isinstance(value, str):
                continue

            value = value.decode('utf-8 ')
            row[key] = value

            if value == '':
                row[key] = None
            if value == 'false':
                row[key] = False
            if value == 'true':
                row[key] = True
            if TIMESTAMP.search(value):
                row[key] = parser.parse(value + ' CET')

        try:
            instance, created = self.model.objects.get_or_create(pk=row[self.primary_key], defaults=row)
        except Exception as e:
            print e
            print row
            raise e
        else:
            if self.should_exist and created:
                print "Unexpected new data:"
                print row
            #elif not self.should_exist and not created:
            #    print "Unexpected old data:"
            #    print row

            #check for strange stuff
            if not created:
                self.check_changes(row, instance)

    def check_changes(self, row, instance):
        d = DictDiffer(row, model_to_dict(instance))

        def compare(x, y):
            # Do some conversions explicit to reduce false positives
            same = False

            try:
                same = x.pk == y.pk
            except:
                pass

            try:
                same = re.sub(r'\s+', ' ', x.strip()) == re.sub(r'\s+', ' ', y)
            except:
                pass

            try:
                same = int(x) == y
            except:
                pass

            try:
                same = Decimal(x) == y
            except:
                pass

            try:
                if y == None:
                    same = x.strip() == ''
            except:
                pass

            try:
                x = x - x.utcoffset()
                same = y.replace(microsecond=0, tzinfo=None) == x.replace(microsecond=0, tzinfo=None)
            except:
                pass

            return same

        def make_list_value(value):

            if value == 'datum':
                return value

            row_v = row[value]
            i_v = getattr(instance, value)

            if not compare(row_v, i_v):
                return {value: (row_v, i_v)}

        list = [x for x in map(make_list_value, d.changed()) if x]

        if d.added() or (list and getattr(instance, 'gewijzigdop') <= row['gewijzigdop']): #or d.removed()
            print row[self.primary_key]

        if d.added():
            print "Added (only in tsv):", d.added()

            #actualy add the new info
            for key in d.added():
                setattr(instance, key, row[key])

            instance.save()

        #if d.removed():
        #    print "Removed (only in db):", d.removed()

        if list and getattr(instance, 'gewijzigdop') <= row['gewijzigdop']:
            print "Changed values (tsv, db):"
            pprint(list)

            if getattr(instance, 'gewijzigdop') == row['gewijzigdop']:
                #actualy add new info if None
                for key in d.changed():
                    if getattr(instance, key) is None:
                        setattr(instance, key, row[key])
                instance.save()
            elif getattr(instance, 'gewijzigdop') < row['gewijzigdop']:
                for key in d.changed():
                    setattr(instance, key, row[key])
                instance.save()


class SubtreeImport(TsvImport):
    many_to_many = False
    should_exist = True
    related_tsv_key = None
    related_model = None
    key_in_self = False
    key_in_self = False

    def __init__(self, *args, **kwargs):
        super(SubtreeImport, self).__init__(*args, **kwargs)

        #set key_in_self from related_model verbose_name if not set
        if not self.key_in_self:
            self.key_in_self = self.related_model._meta.verbose_name

        #check key_in_self (strip '_id' in check)
        if not self.key_in_self in self.model._meta.get_all_field_names():
            raise FieldDoesNotExist(self.key_in_self)

        #set related_tsv_key from related_model verbose_name if not set
        if not self.related_tsv_key:
            self.related_tsv_key = 'sid_' + self.related_model._meta.verbose_name

        #determine many_to_many from field
        try:
            self.many_to_many = self.model._meta.get_field(self.key_in_self).__class__ == ManyToManyField
        except FieldDoesNotExist:
            # no field found so must be a related manager. Which we treat the same as many to many
            self.many_to_many = True

    def handle(self, row):
        related_id = row[self.related_tsv_key]
        del row[self.related_tsv_key]

        #check related_id
        related = None
        try:
            related = self.related_model.objects.get(pk=related_id)
        except:
            print "Missing %s: %s for relation with %s: %s" % (self.related_model._meta.verbose_name.title(), related_id, self.model._meta.verbose_name.title(), row[self.primary_key])

        #foreignkey to related
        if not self.many_to_many:
            row[self.key_in_self] = related

        super(SubtreeImport, self).handle(row)

        #many to many or foreignkey from related
        if self.many_to_many and related:
            instance = self.model.objects.get(pk=row[self.primary_key])

            field = getattr(instance, self.key_in_self)
            field.add(related)

