from django.db import models


class Party(models.Model):
    name = models.CharField(max_length=100)
    replaced_by = models.ForeignKey('self', related_name='replaced', null=True, blank=True)


class Politician(models.Model):
    name = models.CharField(max_length=100)
