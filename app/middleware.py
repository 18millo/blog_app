from django.shortcuts import redirect
from django.urls import reverse
from django_otp.plugins.otp_totp.models import TOTPDevice


class TwoFactorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            has_2fa = TOTPDevice.objects.filter(
                user_id=request.user.pk, confirmed=True
            ).exists()
            if has_2fa and not request.user.is_verified():
                verify_path = reverse('verify_2fa')
                if request.path not in (verify_path, reverse('account_logout')):
                    return redirect(verify_path)
        return self.get_response(request)
