from django.db import models
from django.contrib.auth.models import User

import datetime

import trueskill

from enum import IntEnum

class Game(models.Model):
  name = models.CharField(max_length=80, unique=True)
  slug = models.SlugField(max_length=80, unique=True)
  require_results = models.BooleanField(default=False)
  can_draw = models.BooleanField(default=False)
  players_per_side = models.IntegerField(default=1)

  @property
  def total_participants(self):
    # We can cheat and use the number of rankings for a game to
    # see how many participants there are.
    return Ranking.objects.filter(game=self).count()

  @property
  def total_matches(self):
    return self.match_set.count()

  @property
  def latest_match(self):
    return self.match_set.latest()

  def get_absolute_url(self):
    return '/%s/' % self.slug

  def __unicode__(self):
    return 'id %d, %s "%s"' % (self.id, self.slug, self.name)

class MatchManager(models.Manager):

  def for_user(self, user, game):
    match_ids = list(Participant.objects.filter(user=user).values_list('match_id', flat=True))
    return super(MatchManager, self).get_queryset().filter(id__in=match_ids, game=game)

  def between_users(self, user, opponent, game):
    match_ids = list(Participant.objects.filter(user=user).values_list('match_id', flat=True))
    common_ids = list(Participant.objects.filter(user=opponent, match_id__in=match_ids).values_list('match_id', flat=True))
    return super(MatchManager, self).get_queryset().filter(id__in=common_ids, game=game)

class Match(models.Model):
  results = models.CharField(max_length=255, null=True, blank=True)
  timestamp = models.DateTimeField(default=datetime.datetime.now)
  submitter = models.ForeignKey(User, related_name='submitter')
  game = models.ForeignKey(Game)

  objects = MatchManager()

  def parse_results(self):
    if not self.results:
      return None, None

    wins, losses = self.results.split('-')
    wins = int(wins)
    losses = int(losses)
    return wins, losses

  def get_match_participants_for_role(self, role, participants=None,
                                      user_lookup=None):
    if participants is None:
      participants = self.participant_set.all()
    if user_lookup is None:
      user_lookup = {}

    items = []
    for participant in participants:
      if participant.role == role:
        u = user_lookup.get(participant.user_id)
        if u is None:
          u = User.objects.get(id=participant.user_id)
        items.append(u.username)

    if role == ParticipantRole.Win:
      self._match_winners = items
    elif role == ParticipantRole.Loss:
      self._match_losers = items
    return items

  @property
  def match_winners(self):
    if not hasattr(self, '_match_winners'):
      self._match_winners = self.get_match_participants_for_role(ParticipantRole.Win)
    return self._match_winners

  @property
  def match_losers(self):
    if not hasattr(self, '_match_losers'):
      self._match_losers = self.get_match_participants_for_role(ParticipantRole.Loss)
    return self._match_losers

  def __unicode__(self):
    when = self.timestamp.strftime('%m/%d/%Y')
    winners = '/'.join(self.match_winners)
    losers = '/'.join(self.match_losers)
    return 'id %d, %s beat %s on %s' % (self.id, winners, losers, when)

  class Meta:
    verbose_name_plural = 'matches'
    get_latest_by = 'timestamp'

class ParticipantRole(IntEnum):
  Unknown = 0
  Draw = 1
  Win = 2
  Loss = 3

class Participant(models.Model):
  user = models.ForeignKey(User)
  match = models.ForeignKey(Match)
  role = models.IntegerField(default=ParticipantRole.Unknown,
                             choices=ParticipantRole.choices(reverse=True))

  @property
  def role_str(self):
    return ParticipantRole.lookup(self.role)

  def __unicode__(self):
    return '%s had a %s on match id %d' % (self.user.username, self.role_str,
                                           self.match_id)

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
    self.exposure = t.expose(rating)

  def score(self):
    return int(self.exposure * 1000)

  def __unicode__(self):
    return '%s, trueskill.Rating(mu=%f, sigma=%f), exposure = %f' % (
        self.user.username, self.mu, self.sigma, self.exposure)
