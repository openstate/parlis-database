from django.db import models


class DocumentLabels(models.Model):
    document = models.OneToOneField('core.Document', related_name='label')
    label1 = models.CharField(max_length=100)
    label2 = models.CharField(max_length=100)
    label3 = models.CharField(max_length=100)
    label4 = models.CharField(max_length=100)
    label5 = models.CharField(max_length=100)


class DocumentLabels2(models.Model):
    document = models.ForeignKey('core.Document', related_name='labels')
    label = models.CharField(max_length=100)
    volgorde = models.PositiveSmallIntegerField()
