from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns('jira_oauth.views',
    url(r'^authorize/$', 'authorize', name='jira-oauth-authorize'),
    url(r'^access_token/$', 'access_token', name='jira-oauth-access-token'),
)
