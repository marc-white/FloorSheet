from django import forms
from . import models

from datetimewidget.widgets import DateTimeWidget

class TeamColorChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return '{} ({})'.format(obj.team_name, obj.color)

class JQueryUIDatepickerWidget(forms.DateInput):
    def __init__(self, **kwargs):
        super(forms.DateInput, self).__init__(attrs={"size":10, "class": "dateinput"}, **kwargs)

    class Media:
        css = {"all":
                   (
                       "http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.6/themes/redmond/jquery-ui.css",
                       "scoresheet_generator/css/jquery-ui-timepicker-addon.css",
                    )
               }
        js = (
            "http://ajax.googleapis.com/ajax/libs/jquery/1.4.3/jquery.min.js",
            "http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.6/jquery-ui.min.js",
            "scoresheet_generator/js/jquery-ui-timepicker-addon.js",
        )


class ScoresheetGeneratorForm(forms.Form):

    # Define form fields
    comp = forms.ModelChoiceField(queryset=models.Division.objects.filter(
                                     active=True
                                  ),
                                  # initial=models.Competition.objects.first(),
                                  required=False,
                                  label='Competition')
    start_time = forms.DateTimeField(required=True,
                                     widget=DateTimeWidget(
                                         options={
                                             'format': 'yyyy-mm-dd hh:ii',
                                         }
                                     ))
    venue = forms.ModelChoiceField(queryset=models.Venue.objects.all(),
                                   # initial=models.Venue.objects.first(),
                                   required=False)
    match_id = forms.CharField(max_length=30, required=False, label='Match ID')

    home_team = TeamColorChoiceField(queryset=models.Team.objects.all(),
                                     required=True, initial=None)
    away_team = TeamColorChoiceField(queryset=models.Team.objects.all(),
                                     required=True, initial=None)
    duty_team = TeamColorChoiceField(queryset=models.Team.objects.all(),
                                     required=False, initial=None,
                                     help_text="Define if a team is "
                                               "assigned to duty")


