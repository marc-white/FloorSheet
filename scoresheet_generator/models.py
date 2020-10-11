# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

DIVISIONS = (
    ('m', 'Men'),
    ('w', 'Women'),
    ('1', 'Division 1'),
    ('2', 'Division 2'),
)

ROLES = (
    ('C', 'Captain'),
    ('G', 'Goalkeeper'),
    ('S', 'Team staff'),
)


class Team(models.Model):

    class Meta:
        unique_together = ('team_name', )

    # Model fields
    team_name = models.CharField(max_length=100, blank=False,
                                 unique=False)
    team_list = models.FileField(blank=True)

    def __unicode__(self):
        return '{}'.format(self.team_name, )


class Player(models.Model):

    class Meta:
        unique_together = ('team', 'number', )

    # Model fields
    name = models.CharField(max_length=300, blank=False, unique=False)
    number = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)],
        blank=True
    )
    role = models.CharField(max_length=1, choices=ROLES, blank=True)
    team = models.ForeignKey(Team)

    def __unicode__(self):
        return '#{}. {} ({})'.format(
            self.number,
            self.name,
            self.team.team_name,
        )


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


class Division(models.Model):
    class Meta:
        unique_together = ('comp', 'div')

    comp = models.ForeignKey(Competition)
    div = models.CharField(max_length=1, choices=DIVISIONS)
    teams = models.ManyToManyField(Team, blank=True)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return '{} {}'.format(
            self.comp, self.get_div_display(),
        )


class Venue(models.Model):

    venue_name = models.CharField(max_length=200, blank=False)

    def __unicode__(self):
        return self.venue_name



