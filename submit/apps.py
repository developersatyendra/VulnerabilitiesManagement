from django.apps import AppConfig
from django.apps.registry import apps
import threading


class SubmitConfig(AppConfig):
    name = 'submit'

    def ready(self):
        thread = threading.Thread(target=WaitForDjangoReady)
        thread.daemon = True
        thread.start()

def WaitForDjangoReady():
    while not apps.ready:
        pass
    print("Django is ready")
    from .submitprocessor import MgntThreadingSubmitProcess

    MgntThreadingSubmitProcess()