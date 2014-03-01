from django.conf import settings
from .models import Game

def app_data(request, *args, **kwargs):
    def to_dict(g):
        return {
            'name': g.name,
            'slug': g.slug,
        }

    games = [to_dict(g) for g in Game.objects.all()]
    return {
        'app_name': getattr(settings, 'APP_NAME', 'StatKeeper'),
        'game_types': games,
        'selected_game_type': request.session.get('selected_game_type', Game.objects.get(id=1))
    }