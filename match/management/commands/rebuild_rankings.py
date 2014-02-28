from django.core.management.base import BaseCommand, CommandError

from django.contrib.auth.models import User
from match.models import Ranking, Match, Game, ParticipantRole, t

class Command(BaseCommand):
  help = 'Rebuilds all of the rankings from scratch.'

  def handle(self, *args, **options):
    # Clear out all of the current rankings
    #Ranking.objects.all().delete()

    for g in Game.objects.all():

      rankings_cache = {}

      for m in Match.objects.all().order_by('timestamp'):
        # Find all the participants for this match and split 'em out
        participants = list(m.participant_set.all())
        winners = [ p for p in participants if p.role == ParticipantRole.Win ]
        losers = [ p for p in participants if p.role == ParticipantRole.Loss ]
        drawers = [ p for p in participants if p.role == ParticipantRole.Draw ]
        if drawers:
          raise CommandError('Does not handle draws yet.')
        if not winners or not losers:
          raise CommandError('Ehh?  Missing participants on match id %d' % m.id)

        # Get the results
        wins, losses = m.parse_results()

        # Get the ids for the participants (in order)
        winner_ids = [ w.user_id for w in winners ]
        loser_ids = [ l.user_id for l in losers ]

        # Get the rankings for those ids (also in order)
        winner_rankings = [ rankings_cache.get(id, t.create_rating()) for id in winner_ids ]
        loser_rankings = [ rankings_cache.get(id, t.create_rating()) for id in loser_ids ]

        # Compute the rankings
        for i in xrange(losses):
          loser_rankings, winner_rankings = t.rate([loser_rankings, winner_rankings])
        for i in xrange(wins):
          winner_rankings, loser_rankings = t.rate([winner_rankings, loser_rankings])

        # Use the fact that things are ordered to update the caches
        for id, ranking in zip(loser_ids, loser_rankings):
          rankings_cache[id] = ranking
        for id, ranking in zip(winner_ids, winner_rankings):
          rankings_cache[id] = ranking

      users = User.objects.in_bulk(rankings_cache.keys())
      for id, user in users.iteritems():
        r, _ = Ranking.objects.get_or_create(user=user, game=g)
        r.from_rating(rankings_cache[id])
        r.save()
        print r
