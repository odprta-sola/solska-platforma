from allauth.account.adapter import DefaultAccountAdapter


class ClosedAccountAdapter(DefaultAccountAdapter):
    """Samoregistracije ni: račune ustvari pooblaščena oseba (uvoz, skrbnik)."""

    def is_open_for_signup(self, request):
        return False

    def send_password_reset_mail(self, user, email, context):
        """Ne pošlje ničesar: obnova prek skupnega predala ni individualna (pred B)."""
        return None
