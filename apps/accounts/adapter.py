from allauth.account.adapter import DefaultAccountAdapter

class AccountAdapter(DefaultAccountAdapter):
    def get_client_ip(self, request):
        """
        Safely determine the client's IP address when behind a proxy.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # The first IP in the list is the client's IP
            return x_forwarded_for.split(',')[0].strip()
        return super().get_client_ip(request)
