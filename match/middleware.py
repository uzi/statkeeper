from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import Http404


class RestrictAdminToStaffMiddleware(object):
    """
    A middleware that restricts administration access to only staff members.
    """

    def process_request(self, request):
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "Restrict admin to staff middleware requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE_CLASSES setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the RestrictStaffToAdminMiddleware class.")
        if not request.user.is_staff:
            if request.path.startswith(reverse('admin:index')):
                raise Http404
