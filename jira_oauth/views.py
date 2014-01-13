from django.conf import settings
from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from oauthlib.oauth1 import SIGNATURE_RSA
from requests_oauthlib import OAuth1Session

import logging
logger = logging.getLogger(__name__)

def require_settings(setting_keys):
    """
    Raise a ImproperlyConfigured if any of the specified Django settings have
    not been configured.
    """
    for setting_key in setting_keys:
        require_setting(setting_key)

def require_setting(setting_key):
    """
    Raise a ImproperlyConfigured if the specified Django settings has not been
    configured.
    """
    if not hasattr(settings, setting_key):
            raise ImproperlyConfigured("You must specify {} in your Django " \
                                       "settings file.".format(setting_key))

def authorize(request):
    """
    Initiate the JIRA OAuth 1 dance by getting an OAuth request token and
    redirecting the end-user to JIRA for authorization.
    """
    require_settings((
        'JIRA_CONSUMER_KEY',
        'JIRA_PRIVATE_RSA_KEY',
        'JIRA_REQUEST_TOKEN_URL',
        'JIRA_AUTHORIZE_URL'
    ))

    # store a redirect url in the 'next' variable if it was passed in on the URL
    if 'auth_redirect' in request.GET:
        request.session['jira_auth_redirect'] = request.GET['auth_redirect']

    # Get request token
    oauth = OAuth1Session(settings.JIRA_CONSUMER_KEY, 
                          signature_type='auth_header', 
                          signature_method=SIGNATURE_RSA, 
                          rsa_key=settings.JIRA_PRIVATE_RSA_KEY)
    request_token = oauth.fetch_request_token(settings.JIRA_REQUEST_TOKEN_URL)

    # Redirect the user for authorization
    if request.is_secure():
        scheme = 'https'
    else:
        scheme = 'http'

    redirect_url = "{}?oauth_token={}&oauth_callback={}://{}{}".format(
        settings.JIRA_AUTHORIZE_URL, 
        request_token['oauth_token'],
        scheme, 
        request.get_host(), 
        reverse('jira-oauth-access-token')
    )

    return redirect(redirect_url)

def access_token(request):
    """
    Handle the callback from the OAuth authorization by requesting an access
    token and storing it in the user's session.
    """
    require_settings((
        'JIRA_CONSUMER_KEY',
        'JIRA_PRIVATE_RSA_KEY',
        'JIRA_ACCESS_TOKEN_URL'
    ))

    # Get access token. The original request token is passed back from JIRA as
    # 'oauth_token' as a GET parameter.
    oauth = OAuth1Session(settings.JIRA_CONSUMER_KEY, 
                          signature_type='auth_header', 
                          signature_method=SIGNATURE_RSA, 
                          rsa_key=settings.JIRA_PRIVATE_RSA_KEY,
                          resource_owner_key=request.GET['oauth_token'])
    
    try:
        token = oauth.fetch_access_token(settings.JIRA_ACCESS_TOKEN_URL)
    except ValueError as e:
        # since we're using OAuth1Session instead of OAuth1 we won't have the
        # detailed exceptions. A ValueError is thrown if the response does not
        # have the expected token. The JIRA specific error messages are not
        # parsed out.
        if 'jira_auth_redirect' in request.session:
            redirect_to = request.session['jira_auth_redirect']
            del request.session['jira_auth_redirect']
            return redirect(redirect_to)
        elif hasattr(settings, 'JIRA_AUTH_REDIRECT'):
            return redirect(settings.JIRA_AUTH_REDIRECT)
        else:
            raise ImproperlyConfigured("You must specify JIRA_AUTH_REDIRECT " \
                                       "in your Django settings file or pass " \
                                       "'auth_redirect' as a GET parameter " \
                                       "to the 'authorize' view.")
        
    # Store access token in session
    if getattr(settings, 'JIRA_SAVE_TOKEN_TO_SESSION', True):
        request.session['jira_access_token'] = token['oauth_token']
        request.session['jira_access_token_secret'] = token['oauth_token_secret']

    # Store access token in database
    #if getattr(settings, 'JIRA_SAVE_TOKEN_TO_DB', False):
    #   jira_auth = JiraAuth.objects.get(user=request.user)
    #   jira_auth.access_token = token['oauth_token']
    #   jira_auth.access_token_secret = token['oauth_token_secret']
    #   jira_auth.save()

    if 'jira_auth_redirect' in request.session:
        redirect_to = request.session['jira_auth_redirect']
        del request.session['jira_auth_redirect']
        return redirect(redirect_to)
    elif hasattr(settings, 'JIRA_AUTH_REDIRECT'):
        return redirect(settings.JIRA_AUTH_REDIRECT)
    else:
        raise ImproperlyConfigured("You must specify JIRA_AUTH_REDIRECT " \
                                   "in your Django settings file or pass " \
                                   "'auth_redirect' as a GET parameter " \
                                   "to the 'authorize' view.")
