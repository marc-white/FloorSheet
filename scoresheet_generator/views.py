# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import datetime
import subprocess

from django.shortcuts import render
from . import forms, writer
from django.forms import formset_factory
from django.contrib.staticfiles import finders
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import redirect
from django.conf import settings

from pdfrw import PdfWriter, IndirectPdfDict, PdfReader, PdfObject, PdfDict

from django.conf import settings

# Create your views here.


def generate(request):
    template_path = finders.find('scoresheet_generator/pdf/'
                                 'IFF-Match-Record-2010-Form-MVP3'
                                 '.pdf')
    ss_formset = formset_factory(forms.ScoresheetGeneratorForm, extra=5)

    if request.method == 'POST':
        ss_formset = ss_formset(request.POST)
        if ss_formset.is_valid():
            pdfs = []
            for form in ss_formset:
                if form.is_valid() and form.has_changed():
                    template = writer.create_scoresheet(
                        template_path,
                        comp=form.cleaned_data.get('comp'),
                        start_time=form.cleaned_data.get('start_time'),
                        match_id=form.cleaned_data.get('match_id'),
                        home_team=form.cleaned_data.get('home_team'),
                        away_team=form.cleaned_data.get('away_team'),
                        duty_team=form.cleaned_data.get('duty_team'),
                    )
                    p = os.path.join(
                        settings.MEDIA_ROOT,
                        '{}{}_{}-v-{}.pdf'.format(
                            form.cleaned_data.get('start_time').strftime(
                                '%Y-%m-%d_%H%M'),
                            '_{}'.format(form.cleaned_data.get('match_id')) if
                            form.cleaned_data.get('match_id') else
                            '',
                            form.cleaned_data.get('home_team').team_name[:4],
                            form.cleaned_data.get('away_team').team_name[:4],
                        ))
                    PdfWriter().write(p, template)
                    pdfs.append(p)

            # Make and serve a zip of these
            zip_name = 'sheets_made_at_' + datetime.datetime.now().strftime('%Y-%m-%d-%H%M') + '.zip'
            zip_path = os.path.join(settings.MEDIA_ROOT, zip_name)
            subprocess.check_call(['zip', '-j', zip_path] + pdfs)
            return redirect('/'.join(zip_path.split(os.sep)[-2:]))

    return render(request, 'scoresheet_generator/generator.html',
                  {
                      'ss_formset': ss_formset,
                  })

