# Module that creates the scoresheet

import csv
import os
import pdfrw
import subprocess

from django.conf import settings
from django.core.files.storage import DefaultStorage

from fdfgen import forge_fdf

ANNOT_KEY = '/Annots'
ANNOT_FIELD_KEY = '/T'
ANNOT_VAL_KEY = '/V'
ANNOT_RECT_KEY = '/Rect'
SUBTYPE_KEY = '/Subtype'
WIDGET_SUBTYPE_KEY = '/Widget'

STAFF_ROLE_KEY = 'sSmM'
CAPTAIN_ROLE_KEY = 'cC'
GOALIE_ROLE_KEY = 'gG'

def try_int_or_zero(x):
    try:
        return int(x)
    except ValueError:
        return 0


def parse_team_list(team_obj):
    """
    Parse a team CSV list into a dict to be written to PDF
    """
    # No-op if no team list available
    if team_obj.team_list.name == '':
        return {}

    # Open up a CSV reader
    storage = DefaultStorage()
    with storage.open(team_obj.team_list.name, mode='r') as team_list:
        reader = csv.DictReader(team_list,
                                fieldnames=(
                                    'role', 'number', 'name', 'birthday',
                                ))
        rows = [row for row in reader]

    data_dict = {}

    # Build and write back a player list and staff list
    players = [row for row in rows
               if not any([_ in row['role'] for _ in STAFF_ROLE_KEY])][:20]
    players.sort(key=lambda x: try_int_or_zero(x['number']))
    for i, row in enumerate(players):
        no = '{:02d}'.format(i+1)
        data_dict['PlayerGC{}'.format(no)] = ''.join([
            _ for _ in row['role'] if _ in STAFF_ROLE_KEY+CAPTAIN_ROLE_KEY+GOALIE_ROLE_KEY
        ])
        data_dict['PlayerNo{}'.format(no)] = row['number']
        data_dict['PlayerName{}'.format(no)] = row['name']
        data_dict['PlayerDOB{}'.format(no)] = row['birthday']

    staff = [row for row in rows
               if any([_ in row['role'] for _ in STAFF_ROLE_KEY])][:5]
    staff.sort(key=lambda x: x['number'])
    for i, row in enumerate(staff):
        no = '{:1d}'.format(i+1)
        data_dict['Off{}'.format(no)] = row['name']

    return data_dict


def create_scoresheet(template, *args, **kwargs):
    """
    Start filling out a floorball scoresheet, based on a passed info

    Returns
    -------
    pdfrw.PdfFileReader
        A PdfFileReader instance. This can be written to disk by sending
        it to a PdfFileWriter instance.
    """

    # Build a data-dict from the input kwargs
    data_dict = {}

    # Single input things
    if kwargs.get('assoc'):
        pass
    if kwargs.get('comp'):
        data_dict['Competition'] = kwargs['comp'].comp
        data_dict['Association'] = kwargs['comp'].assoc
    if kwargs.get('venue'):
        data_dict['Venue'] = kwargs['venue']
    if kwargs.get('match_id'):
        data_dict['MatchNo'] = kwargs['match_id']
    if kwargs.get('start_time'):
        data_dict['Date'] = kwargs['start_time'].strftime('%d %b %Y')
        data_dict['StartTime'] = kwargs['start_time'].strftime('%H:%M')
    if kwargs.get('duty_team'):
        data_dict['MatchSecName'] = '[{}]'.format(
            kwargs['duty_team'].__unicode__(),
        )
    print('- create_scoresheet: Added basic team info')

    for team in ['home', 'away']:
        team_field_code = team.capitalize()
        team_obj = kwargs.get('{}_team'.format(team))
        if team_obj is None:
            continue

        # Write in the team name
        data_dict['{}TeamName'.format(team_field_code)] = team_obj.team_name

        # Add in the player/staff list
        data_dict.update(
            {'{}{}'.format(team_field_code, k): v
             for k, v in parse_team_list(team_obj).items()}
        )
    print('- create_scoresheet: Added team lists')
    print('- create_scoresheet: Final data_dict is...\n{}\n'.format(data_dict))

    # return data_dict

    # Open up the template form
    template_pdf = pdfrw.PdfReader(template)
    template_pdf.Root.AcroForm.update(
        pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))
    annotations = template_pdf.pages[0][ANNOT_KEY]
    for annotation in annotations:
        if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
            if annotation[ANNOT_FIELD_KEY]:
                key = annotation[ANNOT_FIELD_KEY][1:-1]
                if key in data_dict.keys():
                    print('- create_scoresheet: Adding key {}'.format(key))
                    annotation.update(
                        pdfrw.PdfDict(V='{}'.format(data_dict[key]))
                    )

    return template_pdf
