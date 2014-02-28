from django.core.management.base import BaseCommand, CommandError

from django.contrib.auth.models import User
from match.models import Ranking, Match, Game, ParticipantRole, t

class Command(BaseCommand):
  help = 'Rebuilds all of the ratings from scratch.'

  def handle(self, *args, **options):
    # Clear out all of the current ratings
    #Ranking.objects.all().delete()

    for game in Game.objects.all():

      ratings_cache = {}

      for match in Match.objects.all().order_by('timestamp'):
        # Find all the participants for this match and split 'em out
        participants = list(match.participant_set.all())
        winners = [ p for p in participants if p.role == ParticipantRole.Win ]
        losers = [ p for p in participants if p.role == ParticipantRole.Loss ]
        drawers = [ p for p in participants if p.role == ParticipantRole.Draw ]
        if drawers:
          raise CommandError('Does not handle draws yet.')
        if not winners or not losers:
          raise CommandError('Ehh?  Missing participants on match id %d' % match.id)

        # Get the results
        wins, losses = match.parse_results()

        # Get the ids for the participants (in order)
        winner_ids = [ w.user_id for w in winners ]
        loser_ids = [ l.user_id for l in losers ]

        # Get the ratings for those ids (also in order)
        winner_ratings = [ ratings_cache.get(id, t.create_rating()) for id in winner_ids ]
        loser_ratings = [ ratings_cache.get(id, t.create_rating()) for id in loser_ids ]

        # Compute the ratings
        for i in xrange(losses):
          loser_ratings, winner_ratings = t.rate([loser_ratings, winner_ratings])
        for i in xrange(wins):
          winner_ratings, loser_ratings = t.rate([winner_ratings, loser_ratings])

        # Use the fact that things are ordered to update the caches
        for id, rating in zip(loser_ids, loser_ratings):
          ratings_cache[id] = rating
        for id, rating in zip(winner_ids, winner_ratings):
          ratings_cache[id] = rating

      users = User.objects.in_bulk(ratings_cache.keys())
      for id, user in users.iteritems():
        r, _ = Ranking.objects.get_or_create(user=user, game=game)
        r.from_rating(ratings_cache[id])
        r.save()
        print r
