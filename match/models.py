from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.signals import pre_init

import datetime

import trueskill

from enum import IntEnum

class Game(models.Model):
  name = models.CharField(max_length=80, unique=True)
  slug = models.SlugField(max_length=80, unique=True)
  require_results = models.BooleanField(default=False)

  def __unicode__(self):
    return 'id %d, %s "%s"' % (self.id, self.slug, self.name)

class MatchManager(models.Manager):

  def for_user(self, user):
    match_ids = list(Participant.objects.filter(user=user).values_list('match_id', flat=True))
    return super(MatchManager, self).get_query_set().filter(id__in=match_ids)

  def between_users(self, user, opponent):
    match_ids = list(Participant.objects.filter(user=user).values_list('match_id', flat=True))
    common_ids = list(Participant.objects.filter(user=opponent, match_id__in=match_ids).values_list('match_id', flat=True))
    return super(MatchManager, self).get_query_set().filter(id__in=common_ids)

class Match(models.Model):
  results = models.CharField(max_length=255, null=True, blank=True)
  timestamp = models.DateTimeField(default=datetime.datetime.now)
  submitter = models.ForeignKey(User, related_name='submitter')
  game = models.ForeignKey(Game)

  objects = MatchManager()

  # XXX winner and loser are for backwards compatibility to the old model
  #     and should go away because they're terribly inefficient
  @property
  def winner(self):
    return self.participant_set.filter(role=ParticipantRole.Win)[0].user

  @property
  def loser(self):
    return self.participant_set.filter(role=ParticipantRole.Loss)[0].user

  def parse_results(self):
    if not self.results:
      return None, None

    wins, losses = self.results.split('-')
    wins = int(wins)
    losses = int(losses)
    return wins, losses

  def __unicode__(self):
    when = self.timestamp.strftime('%m/%d/%Y')
    return 'id %d, %s beat %s on %s' % (self.id, self.winner.username,
                                        self.loser.username, when)

  class Meta:
    verbose_name_plural = 'matches'

class ParticipantRole(IntEnum):
  Unknown = 0
  Draw = 1
  Win = 2
  Loss = 3

class Participant(models.Model):
  user = models.ForeignKey(User)
  match = models.ForeignKey(Match)
  role = models.IntegerField(default=ParticipantRole.Unknown)

  @property
  def role_str(self):
    return ParticipantRole.lookup(self.role)

  def __unicode__(self):
    return '%s had a %s on match id %d' % (self.user.username, self.role_str,
                                           self.match_id)

def make_participants():
  for m in Match.objects.all():
    Participant.objects.create(user=m.winner, match=m, role=ParticipantRole.Win)
    Participant.objects.create(user=m.loser, match=m, role=ParticipantRole.Loss)

# Initialize a TrueSkill environment... we can tweak this if desired
t = trueskill.TrueSkill()

class Ranking(models.Model):
  user = models.ForeignKey(User)
  game = models.ForeignKey(Game)
  mu = models.FloatField(default=t.mu)
  sigma = models.FloatField(default=t.sigma)
  exposure = models.FloatField(default=0.0)

  def to_rating(self):
    return t.create_rating(self.mu, self.sigma)

  def from_rating(self, rating):
    self.mu = rating.mu
    self.sigma = rating.sigma
    self.exposure = rating.exposure

  def __unicode__(self):
    return '%s, trueskill.Rating(mu=%f, sigma=%f), exposure = %f' % (
        self.user.username, self.mu, self.sigma, self.exposure)
