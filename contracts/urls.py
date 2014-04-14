from django.conf.urls import patterns, url

from contracts import views

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^advert/(?P<contract_id>\d+)/$', views.detail),
    url(r'^advert/create/$', views.create, name='create'),
    url(r'^advert/(?P<contract_id>\d+)/update$', views.update, name='update')
)