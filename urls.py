from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('statkeeper.match.views',
    url(r'^$', 'index', name='index'),
    url(r'^submit/$', 'submit', name='submit'),
    url(r'^user/(?P<username>\w+)/$', 'user', name='user'),
    url(r'^user/(?P<username>\w+)/versus/(?P<versus>\w+)/$', 'versus', name='versus'),
)

urlpatterns += patterns('',
    # Examples:
    # url(r'^$', 'statkeeper.views.home', name='home'),
    # url(r'^statkeeper/', include('statkeeper.foo.urls')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    #(r'^$', direct_to_template, { 'template': 'index.html' })

    (r'^login/$', 'django.contrib.auth.views.login', {
      'template_name': 'login.html'
    }),
    (r'^logout/$', 'django.contrib.auth.views.logout', {
      'next_page': '/'
    }),
    (r'^settings/$', 'django.contrib.auth.views.password_change', {
      'template_name': 'password_change_form.html',
      'post_change_redirect': '/'
    }),
)

if settings.LOCAL_MEDIA:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT, 'show_indexes': True
        })
    )
