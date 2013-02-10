from django.db import models


class DocumentContent(models.Model):
    document = models.OneToOneField('core.Document', related_name='content')
    content = models.TextField()

    def __unicode__(self):
        return self.document.__unicode__()
