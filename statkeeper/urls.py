from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('match.views',
    url(r'^$', 'index', name='index'),
    url(r'^submit/$', 'submit', name='submit'),
    url(r'^user/(?P<username>\w+)/$', 'user', name='user'),
    url(r'^user/(?P<username>\w+)/versus/(?P<versus>\w+)/$', 'versus', name='versus'),
)

urlpatterns += patterns('',
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

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
        url(r'^admin/', include(admin.site.urls)),
    )
