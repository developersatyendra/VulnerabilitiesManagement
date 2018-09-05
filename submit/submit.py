from django.apps import AppConfig


class MyAppConfig(AppConfig):
    name = 'submit'
    verbose_name = "My Application"
    def ready(self):
        print("Hello submit is starting up")