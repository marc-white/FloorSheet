# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.files.storage import DefaultStorage
from django.core.exceptions import ValidationError

import writer
import csv
import codecs
import datetime

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

STAFF_ROLE_KEY = 'sSmM'
CAPTAIN_ROLE_KEY = 'cC'
GOALIE_ROLE_KEY = 'gG'

_DATE_ORDERS = [
    ["%d", "%m", "%y"],
    ["%d", "%m", "%Y"],
    ["%y", "%m", "%d"],
    ["%Y", "%m", "%d"],
]
_DATE_SEPS = ["-", "/", ]

DATE_FORMATS = []
for sep in _DATE_SEPS:
    for order in _DATE_ORDERS:
        DATE_FORMATS.append(sep.join(order))



def try_int_or_other(x, other=None):
    try:
        return int(x)
    except ValueError:
        return other


def parse_date(date_str):
    for fmt in DATE_FORMATS:
        try:
            return datetime.datetime.strptime(date_str, fmt)
        except:
            pass
    return None


class Team(models.Model):

    class Meta:
        unique_together = ('team_name', )

    # Model fields
    team_name = models.CharField(max_length=100, blank=False,
                                 unique=False)
    color = models.CharField(max_length=30, blank=True)
    team_list = models.FileField(blank=True)

    def __init__(self, *args, **kwargs):
        super(Team, self).__init__(*args, **kwargs)
        self._original_team_list = self.team_list.name

    def __unicode__(self):
        return '{}'.format(self.team_name, )

    def parse_team_list(self):
        """
        Parse the CSV team list
        :return:
        """
        if self.team_list.name == '':
            return {}

        # Open up a CSV reader
        storage = DefaultStorage()
        with storage.open(self.team_list.name, mode='r') as team_list:
            reader = csv.DictReader(codecs.EncodedFile(team_list, 'utf-8', 'utf-8-sig'),
                                    # team_list,
                                    fieldnames=(
                                        'role', 'number', 'name',
                                        'birthday',
                                    ))
            rows = [row for row in reader]

        data_dict = {}

        print(rows)

        data_dict['players'] = [row for row in rows
                                if not any([_ in row['role'] for _ in STAFF_ROLE_KEY])][:20]
        data_dict['players'].sort(key=lambda x: try_int_or_other(x['number'], 0))

        data_dict['staff'] = [row for row in rows
                              if any([_ in row['role'] for _ in STAFF_ROLE_KEY])][:5]
        data_dict['staff'].sort(key=lambda x: try_int_or_other(x['number'], 0))

        return data_dict

    def update_players(self):
        data_dict = self.parse_team_list()
        if len(data_dict) == 0:
            return
        for player in data_dict['players']:
            player_obj = Player(
                name=player['name'],
                number=try_int_or_other(player['number'], None),
                team=self,
                dob=parse_date(player['birthday']),
                is_captain=any([_ in player['role'] for _ in CAPTAIN_ROLE_KEY]),
                is_goalie=any([_ in player['role'] for _ in GOALIE_ROLE_KEY]),
                is_staff=False,
            )
            player_obj.save()
        for player in data_dict['staff']:
            player_obj = Player(
                name=player['name'],
                number=try_int_or_other(player['number'], None),
                team=self,
                is_captain=False,
                is_goalie=False,
                is_staff=True,
            )
            player_obj.save()

    def save(self, *args, **kwargs):
        super(Team, self).save(*args, **kwargs)
        if self.team_list.name != self._original_team_list and len(self.team_list.name) > 0:
            # Blow away existing Players for this team
            players = Player.objects.filter(team=self)
            players.delete()
            # Re-populate Players from the CSV team list
            self.update_players()


class Player(models.Model):

    class Meta:
        unique_together = ('team', 'number', )

    # Model fields
    name = models.CharField(max_length=300, blank=False, unique=False)
    number = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)],
        blank=True,
        null=True
    )
    dob = models.DateField(blank=True, null=True)
    is_captain = models.BooleanField(default=False)
    is_goalie = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    team = models.ForeignKey(Team)

    def __unicode__(self):
        return '#{}. {} ({})'.format(
            self.number,
            self.name,
            self.team.team_name,
        )

    def clean(self):
        if self.is_staff and (self.is_captain or self.is_goalie):
            raise ValidationError('Team staff cannot be a captain '
                                  'or goalkeeper.')


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



