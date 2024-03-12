from django.apps import AppConfig


class WalletConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wallet"


class YourAppConfig(AppConfig):
    name = 'wallet'

    def ready(self):
        import wallet.signals 