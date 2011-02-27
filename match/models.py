from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q

import datetime

class Game(models.Model):
  name = models.CharField(max_length=80, unique=True)
  slug = models.SlugField(max_length=80, unique=True)
  require_results = models.BooleanField(default=False)

  def __unicode__(self):
    return '%d: %s "%s"' % (self.id, self.slug, self.name)

class MatchManager(models.Manager):

  def for_user(self, user):
    criteria = Q(winner=user) | Q(loser=user)
    return super(MatchManager, self).get_query_set().filter(criteria)

  def between_users(self, user, opponent):
    criteria = (Q(winner=user) & Q(loser=opponent)) | \
               (Q(winner=opponent) & Q(loser=user))
    return super(MatchManager, self).get_query_set().filter(criteria)

class Match(models.Model):
  winner = models.ForeignKey(User, related_name='winner')
  loser = models.ForeignKey(User, related_name='loser')
  results = models.CharField(max_length=255, null=True, blank=True)
  timestamp = models.DateTimeField(default=datetime.datetime.now)
  submitter = models.ForeignKey(User, related_name='submitter')
  game = models.ForeignKey(Game, related_name='game')

  objects = MatchManager()

  def __unicode__(self):
    when = self.timestamp.strftime('%m/%d/%Y')
    return 'Match %d: %s beat %s on %s' % (self.id, self.winner.username,
                                           self.loser.username, when)

  class Meta:
    verbose_name_plural = 'matches'
