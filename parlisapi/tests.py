# -*- coding: utf-8 -*-

from django.test import TestCase

from .import_data import Zaken
from core.models import Zaak


class ImportZaakTest(TestCase):
    def test_basic_addition(self):
        """
        Tests import of Zaken
        """
        data = (
'''Id      Nummer  Soort   Titel   CiteerTitel     Alias   Status  Onderwerp       DatumStart      Kamer   GrondslagVoorhang       Termijn Vergaderjaar    Volgnummer      HuidigeBehandelStatus   Afgedaan        GrootProject    AangemaaktOp    GewijzigdOp
1ed32a70-a271-4fc6-b2b5-20b51307c7d8    2007Z00132      Brief regering  Wijziging van de Wet op het primair onderwijs en de Wet op de expertisecentra onder meer in verband met aanpassing van de methode van jaarlijkse prijsbijstelling ten aanzien van de materiële voorzieningen                    Vrijgegeven     Rapporten van onderzoeken in het kader van evaluatie materiële bekostiging scholen primair onderwijs    2006-07-06T00:00:00     Tweede Kamer                    2005-2006       7               false           2008-08-25T17:33:40.83
  2008-08-25T17:33:41.143
241a8d18-212b-4dc7-bdee-6d9320d1fafb    2007Z00133      Brief regering  Wijziging van de Wet op het primair onderwijs en de Wet op de expertisecentra onder meer in verband met aanpassing van de methode van jaarlijkse prijsbijstelling ten aanzien van de materiële voorzieningen                    Vrijgegeven     De beleidsreactie op de evaluatie van de materiële bekostiging  2006-09-14T00:00:00     Tweede Kamer                    2005-2006       8               false           2008-08-25T17:33:41.177 2008-08-25T17:33:41.487
98a84484-2634-4308-8181-70830419acec    2007Z00038      Brief regering  Openbaar vervoer                        Vrijgegeven     Spreekverbod dat leiding Nijmeegse Radboud Universiteit zou hebben opgelegd aan medewerkers/studenten inzake kwetsbaarheid chip in OV-chipkaart en diverse toegangspassen       2008-07-02T00:00:00     Tweede Kamer                    20''')
        Zaken(data=(x for x in data.split('\n'))).execute()

        #self.assertEqual(Zaak.objects.count(), 3)
        self.assertTrue(Zaak.objects.exists(id='241a8d18-212b-4dc7-bdee-6d9320d1fafb'))
