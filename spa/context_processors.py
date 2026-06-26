"""Make business settings + role flags available in every template."""
from django.conf import settings


def oasis(request):
    profile = getattr(request.user, 'profile', None) if request.user.is_authenticated else None
    is_owner = bool(getattr(request.user, 'is_superuser', False) or (profile and profile.is_owner))
    return {
        'OASIS': settings.OASIS,
        'current_profile': profile,
        'is_owner': is_owner,
    }
