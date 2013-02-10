from django.db import models


class DocumentLabels(models.Model):
    document = models.OneToOneField('core.Document')
    label1 = models.CharField(max_length=100)
    label2 = models.CharField(max_length=100)
    label3 = models.CharField(max_length=100)
    label4 = models.CharField(max_length=100)
    label5 = models.CharField(max_length=100)
