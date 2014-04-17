from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^login/$', 'django.contrib.auth.views.login', {
        'template_name': 'match/login.html'
    }),
    (r'^logout/$', 'django.contrib.auth.views.logout', {
        'next_page': '/'
    }),
    (r'^settings/$', 'django.contrib.auth.views.password_change', {
        'post_change_redirect': '/',
        'template_name': 'match/password_change_form.html'
    }),
    (r'^favicon\.ico$', RedirectView.as_view(url=settings.MEDIA_URL + '/static/match/images/favicon.ico')),
)

urlpatterns += patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('match.views',
    url(r'^$', 'landing', name='landing'),
    url(r'^(?P<game_type>[a-zA-Z0-9_-]+)/$', 'index', name='index'),
    url(r'^(?P<game_type>[a-zA-Z0-9_-]+)/submit/$', 'submit', name='submit'),
    url(r'^(?P<game_type>[a-zA-Z0-9_-]+)/grid/$', 'grid', name='grid'),
    url(r'^(?P<game_type>[a-zA-Z0-9_-]+)/user/(?P<username>[a-zA-Z0-9_-]+)/$', 'user', name='user'),
    url(r'^(?P<game_type>[a-zA-Z0-9_-]+)/user/(?P<username>[a-zA-Z0-9_-]+)/versus/(?P<versus>[a-zA-Z0-9_-]+)/$', 'versus', name='versus'),
)

# Uncomment this to serve static files for testing. NO NOT USE IN PRODUCTION.
#urlpatterns += patterns('',
#    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
#        {'document_root': settings.STATIC_ROOT}),
#)
