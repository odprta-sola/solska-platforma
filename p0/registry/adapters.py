from allauth.account.adapter import DefaultAccountAdapter


class ClosedAccountAdapter(DefaultAccountAdapter):
    """Samoregistracije ni: račune ustvari pooblaščena oseba (uvoz, skrbnik)."""

    def is_open_for_signup(self, request):
        return False
