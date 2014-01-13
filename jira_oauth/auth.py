from requests_oauthlib import OAuth1Session
from django import conf
from jira import JIRA

def get_authenticated_jira():
    """
    Return a jira.JIRA object authenticated with OAuth.
    """
    if not hasattr(settings, 'JIRA_CONSUMER_KEY'):
            raise ImproperlyConfigured("You must specify JIRA_CONSUMER_KEY "\
                                       "in your Django settings file.")
    if not hasattr(settings, 'JIRA_KEY_CERT'):
        raise ImproperlyConfigured("You must specify JIRA_KEY_CERT"\
                                   "in your Django settings file.")