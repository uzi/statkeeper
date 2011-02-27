from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template

from models import Match
from forms import SubmitForm

from decimal import Decimal as D

UNDEFINED_PERCENTAGE = '-.---'

def percentage_cmp(a, b):
  # We force undefined percentages to the bottom of the list.
  if a['percentage'] == UNDEFINED_PERCENTAGE:
    return -1
  elif b['percentage'] == UNDEFINED_PERCENTAGE:
    return 1
  return cmp(a['percentage'], b['percentage'])

def round_decimal(val, decimal_places=3):
  return val.quantize(D(10) ** -decimal_places)

def calculate_winning_percentage(wins, losses):
  try:
    percentage = D(wins) / (D(wins) + D(losses))
  except:
    return UNDEFINED_PERCENTAGE
  return round_decimal(percentage)

def index(request):
  matches = Match.objects.order_by('-timestamp')

  records = []
  for user in User.objects.all():
    name = user.username
    wins = user.winner.count()
    losses = user.loser.count()
    percentage = calculate_winning_percentage(wins, losses)

    entry = { 'name': name,
              'wins': wins,
              'losses': losses,
              'percentage': percentage }
    records.append(entry)

  records.sort(cmp=percentage_cmp, reverse=True)

  return direct_to_template(request, 'index.html', {
    'records': records, 'matches': matches
  })

def user(request, username):
  user = get_object_or_404(User, username=username)
  matches = Match.objects.for_user(user).order_by('-timestamp')

  records = []
  for opponent in User.objects.all():
    if user == opponent:
      continue

    name = opponent.username
    wins = user.winner.filter(loser=opponent).count()
    losses = user.loser.filter(winner=opponent).count()
    percentage = calculate_winning_percentage(wins, losses)

    entry = { 'name': name,
              'wins': wins,
              'losses': losses,
              'percentage': percentage }
    records.append(entry)

  records.sort(cmp=percentage_cmp, reverse=True)

  return direct_to_template(request, 'user.html', {
    'who': user, 'records': records, 'matches': matches
  })

def versus(request, username, versus):
  user = get_object_or_404(User, username=username)
  opponent = get_object_or_404(User, username=versus)
  matches = Match.objects.between_users(user, opponent).order_by('-timestamp')

  return direct_to_template(request, 'versus.html', {
    'who': user, 'opponent': opponent, 'matches': matches
  })

def submit(request):
  if request.method == 'POST':
    form = SubmitForm(request.POST)
    if form.is_valid():
      form.save(request)
      return HttpResponseRedirect('/')
  else:
    form = SubmitForm()
  return direct_to_template(request, 'submit.html', {
    'form': form
  })
