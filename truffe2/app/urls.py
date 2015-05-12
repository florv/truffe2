from django.conf.urls import patterns, include, url
from django.conf import settings


urlpatterns = patterns('',
    url(r'', include('main.urls')),
    url(r'^users/', include('users.urls')),
    url(r'^units/', include('units.urls')),
    url(r'^communication/', include('communication.urls')),
    url(r'^notifications/', include('notifications.urls')),
    url(r'^logistics/', include('logistics.urls')),
    url(r'^generic/', include('generic.urls')),

    url(r'^impersonate/', include('impersonate.urls')),

    (r'^' + settings.MEDIA_URL[1:] + '(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),  # In prod, use apache !
    (r'^' + settings.STATIC_URL[1:] + '(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),  # In prod, use apache !
)
