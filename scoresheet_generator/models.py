# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

DIVISIONS = (
    ('m', 'Men'),
    ('w', 'Women'),
    ('1', 'Division 1'),
    ('2', 'Division 2'),
)


class Team(models.Model):

    class Meta:
        unique_together = ('team_name', 'division', )

    # Model fields
    team_name = models.CharField(max_length=100, blank=False,
                                 unique=False)
    division = models.CharField(max_length=2, blank=False,
                                choices=DIVISIONS)
    team_list = models.FileField(blank=True)

    def __unicode__(self):
        return '{} ({})'.format(self.team_name, self.division.upper())


class Competition(models.Model):

    assoc = models.CharField(max_length=150, blank=True,
                             help_text='Administering association')
    comp = models.CharField(max_length=200, blank=False,
                            help_text='Competition name')

    def __unicode__(self):
        return '{}{}'.format(
            self.comp,
            ' ({})'.format(self.assoc) if self.assoc else ''
        )


class Venue(models.Model):

    venue_name = models.CharField(max_length=200, blank=False)

    def __unicode__(self):
        return self.venue_name



