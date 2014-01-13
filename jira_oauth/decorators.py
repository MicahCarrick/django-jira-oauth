from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse

def jira_access_token_required(view_func):
    """
    Redirect users to the JIRA authorization URL passing along the current
    URL to redirect to after the OAuth dance is complete.
    """
    def _jira_access_token_required(request, *args, **kwargs):
        if not 'jira_access_token' in request.session:
            uri = reverse("jira-oauth-authorize")
            if '?' in uri:
                uri += '&'
            else:
                uri += '?'
            uri += "auth_redirect=" + request.get_full_path()
            return HttpResponseRedirect(uri)
        return view_func(request, *args, **kwargs)
    return _jira_access_token_required