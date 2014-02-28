from models import Ranking, ParticipantRole, t

def compute_rankings_for_match(match):
  """Given a match, updates the rankings for all participants."""

  # Find all the participants for this match and split 'em out
  participants = list(match.participant_set.all())
  winners = [ p for p in participants if p.role == ParticipantRole.Win ]
  losers = [ p for p in participants if p.role == ParticipantRole.Loss ]
  drawers = [ p for p in participants if p.role == ParticipantRole.Draw ]
  if drawers:
    raise ValueError('Does not handle draws yet.')
  if not winners or not losers:
    raise ValueError('Ehh?  Missing participants on match id %d' % match.id)

  # Get the results
  wins, losses = match.parse_results()

  # Get the rankings for the participants (maintaining order)
  winner_rankings = [ Ranking.objects.get_or_create(user=u.user, game=match.game)[0] for u in winners ]
  loser_rankings = [ Ranking.objects.get_or_create(user=u.user, game=match.game)[0] for u in losers ]

  # Get the ratings from the rankings (still maintaining order)
  winner_ratings = [ w.to_rating() for w in winner_rankings ]
  loser_ratings = [ l.to_rating() for l in loser_rankings ]

  # Compute the rankings doing losses first to reduce their effect
  for i in xrange(losses):
    loser_ratings, winner_ratings = t.rate([loser_ratings, winner_ratings])
  for i in xrange(wins):
    winner_ratings, loser_ratings = t.rate([winner_ratings, loser_ratings])

  # Use the fact that things are ordered to update objects
  for ranking, rating in zip(loser_rankings, loser_ratings):
    ranking.from_rating(rating)
    ranking.save()
  for ranking, rating in zip(winner_rankings, winner_ratings):
    ranking.from_rating(rating)
    ranking.save()
