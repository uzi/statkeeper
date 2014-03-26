import re

from django import forms
from django.contrib.auth.models import User
from django.forms.formsets import BaseFormSet
from django.forms.widgets import Select, TextInput

from models import Match, Participant, ParticipantRole

RESULTS_RE = r'^\d+-\d+$'
results_re = re.compile(RESULTS_RE)

class RequiredFormSet(BaseFormSet):
  def __init__(self, *args, **kwargs):
    super(RequiredFormSet, self).__init__(*args, **kwargs)
    for form in self.forms:
      form.empty_permitted = False

class ParticipantForm(forms.Form):
  queryset = User.objects.filter(is_active=True).order_by('username')

  winner = forms.ModelChoiceField(queryset=queryset, widget=Select(attrs={'class': 'form-control'}))
  loser = forms.ModelChoiceField(queryset=queryset, widget=Select(attrs={'class': 'form-control'}))

  def clean(self):
    cleaned_data = super(ParticipantForm, self).clean()
    winner = cleaned_data.get('winner')
    loser = cleaned_data.get('loser')

    if winner is None or loser is None:
      raise forms.ValidationError("Winner and loser must be filled in")

    return cleaned_data

  def save(self, match):
    if match is None:
      raise forms.ValidationError("Need a match to make the participants.")

    Participant.objects.create(user=self.cleaned_data['winner'],
                               match=match,
                               role=ParticipantRole.Win)
    Participant.objects.create(user=self.cleaned_data['loser'],
                               match=match,
                               role=ParticipantRole.Loss)

class SubmitForm(forms.Form):
  results = forms.CharField(max_length=255, widget=TextInput(attrs={'class': 'form-control'}))

  def clean_results(self):
    results = self.cleaned_data.get('results')
    if not results:
      return ''
    results = results.strip()
    if not results_re.match(results):
      raise forms.ValidationError("Results do not match the format.")
    return results

  def save(self, request, game):
    results = self.clean_results()
    if game.require_results and not results:
      raise ValueError('That game requires the results.')

    # Build the match and its participants
    match = Match.objects.create(results=results,
                                 submitter=request.user,
                                 game=game)

    return match
