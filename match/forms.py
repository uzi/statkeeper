from django import forms
from django.contrib.auth.models import User
from models import Game, Match

import re

RESULTS_RE = r'^\d+-\d+(,\d+-\d+)*$'
results_re = re.compile(RESULTS_RE)

class SubmitForm(forms.Form):
  queryset = User.objects.order_by('username')

  winner = forms.ModelChoiceField(queryset=queryset)
  loser = forms.ModelChoiceField(queryset=queryset)
  results = forms.CharField(max_length=255)

  def clean_results(self):
    results = self.cleaned_data.get('results')
    if not results:
      return ''
    results = results.strip()
    if not results_re.match(results):
      raise forms.ValidationError("Results do not match the format.")
    return results

  def clean(self):
      cleaned_data = super(SubmitForm, self).clean()
      winner = cleaned_data.get('winner')
      loser = cleaned_data.get('loser')

      if winner is None or loser is None:
          raise forms.ValidationError("Winner and loser must be filled in")

      if winner == loser:
          raise forms.ValidationError("Winner and loser can not be the same user")

      return cleaned_data

  def save(self, request):
    # Default to only do ping pong for now, but leave room for future
    # expansion.  Foosball anyone?
    try:
      game = Game.objects.get(slug='pingpong')
    except Game.DoesNotExist:
      game = Game.objects.create(slug='pingpong', name='Ping Pong',
                                 require_results=True)

    results = self.clean_results()
    if game.require_results and not results:
      raise ValueError('That game requires the results.')

    match = Match.objects.create(winner=self.cleaned_data['winner'],
                                 loser=self.cleaned_data['loser'],
                                 results=results,
                                 submitter=request.user,
                                 game=game)
    return match
