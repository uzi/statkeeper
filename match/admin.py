from django.contrib import admin
from models import Game, Match, Participant, Ranking

class ParticipantInline(admin.TabularInline):
  model = Participant
  extra = 0

class MatchAdmin(admin.ModelAdmin):
  inlines = [ ParticipantInline ]
  list_filter = ('game__name',)

class RankingAdmin(admin.ModelAdmin):
  list_filter = ('game__name',)

admin.site.register(Match, MatchAdmin)
admin.site.register(Game)
admin.site.register(Ranking, RankingAdmin)
