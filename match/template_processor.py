from django.conf import settings
from .models import Game

def app_data(request, *args, **kwargs):
    def to_dict(g):
        return {
            'name': g.name,
            'slug': g.slug,
        }

    games = [to_dict(g) for g in Game.objects.all()]

    selected_game = None
    for g in games:
        if g['slug'] == request.resolver_match.kwargs.get('game_type'):
            selected_game = g

    return {
        'app_name': getattr(settings, 'APP_NAME', 'StatKeeper'),
        'game_types': games,
        'selected_game_type': selected_game
    }