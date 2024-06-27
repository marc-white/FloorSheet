# Module that creates the scoresheet

# import csv
# import os
import pdfrw
# import subprocess

from django.conf import settings
# from django.core.files.storage import DefaultStorage

# from fdfgen import forge_fdf

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
    Parse a team player list into a dict to be written to PDF
    """
    players = team_obj.player_set.filter(
        is_staff=False
    ).order_by(
        'number', 'name'
    )
    staff = team_obj.player_set.filter(
        is_staff=True
    ).order_by(
        'number', 'name'
    )
    # No-op if no players on team
    if players.count() == 0 and staff.count() == 0:
        return {}

    # Build and write back a player list and staff list
    data_dict = {}
    for i, player in enumerate(players[:20]):
        no = '{:02d}'.format(i + 1)
        data_dict['PlayerGC{}'.format(no)] = ''
        if player.is_captain: data_dict['PlayerGC{}'.format(no)] += 'C'
        if player.is_goalie: data_dict['PlayerGC{}'.format(no)] += 'G'
        if player.number is not None:
            data_dict['PlayerNo{}'.format(no)] = str(player.number) or ''
        else:
            data_dict['PlayerNo{}'.format(no)] = ''
        data_dict['PlayerName{}'.format(no)] = player.name
        data_dict[
            'PlayerDOB{}'.format(no)
        ] = player.dob.strftime('%d/%m/%y') if player.dob else ''

    for i, player in enumerate(staff):
        no = '{:1d}'.format(i + 1)
        data_dict['Off{}'.format(no)] = player['name']

    return data_dict


def create_scoresheet_data(*args, **kwargs):
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

    print(kwargs)

    # Single input things
    if kwargs.get('assoc'):
        pass
    if kwargs.get('comp'):
        data_dict['Competition'] = "{} {}".format(
            kwargs['comp'].comp.comp,
            kwargs['comp'].get_div_display(),
        )
        data_dict['Association'] = kwargs['comp'].comp.assoc
    if kwargs.get('venue'):
        data_dict['Venue'] = kwargs['venue']
    if kwargs.get('match_id'):
        data_dict['MatchNo'] = kwargs['match_id']
    if kwargs.get('start_time'):
        data_dict['Date'] = kwargs['start_time'].strftime('%d %b %Y')
        data_dict['StartTime'] = kwargs['start_time'].strftime('%H:%M')
    if kwargs.get('duty_team'):
        data_dict['MatchSecName'] = '[{}{}]'.format(
            kwargs['duty_team'].__str__(),
            " ({})".format(
                kwargs['duty_team'].color.capitalize()) if kwargs['duty_team'].color else "",
        )
    # print('- create_scoresheet: Added basic team info')

    for team in ['home', 'away']:
        team_field_code = team.capitalize()
        team_obj = kwargs.get('{}_team'.format(team))
        if team_obj is None:
            continue

        # Write in the team name
        data_dict[
            '{}TeamName'.format(team_field_code)
        ] = "{}{}".format(
            team_obj.team_name,
            " ({})".format(team_obj.color.capitalize()) if team_obj.color else "",
        )

        # Add in the player/staff list
        data_dict.update(
            {'{}{}'.format(team_field_code, k): v
             for k, v in list(parse_team_list(team_obj).items())}
        )
    # print('- create_scoresheet: Added team lists')
    # print('- create_scoresheet: Final data_dict is...\n{}\n'.format(data_dict))

    return data_dict

def create_scoresheet_pdf(template, *args, **kwargs):
    data_dict = create_scoresheet_data(*args, **kwargs)

    # Open up the template form
    template_pdf = pdfrw.PdfReader(template)
    template_pdf.Root.AcroForm.update(
        pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))
    annotations = template_pdf.pages[0][ANNOT_KEY]
    for annotation in annotations:
        if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
            if annotation[ANNOT_FIELD_KEY]:
                key = annotation[ANNOT_FIELD_KEY][1:-1]
                if key in list(data_dict.keys()):
                    # print('- create_scoresheet: Adding key {}'.format(key))
                    annotation.update(
                        pdfrw.PdfDict(V='{}'.format(data_dict[key]))
                    )

    return template_pdf
