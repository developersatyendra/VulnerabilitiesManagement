from django.apps import AppConfig
from django.apps.registry import apps
import threading
import sys
import time

class SubmitConfig(AppConfig):
    name = 'submit'

    # def ready(self):
        # if 'runserver' in sys.argv:
        #     thread = threading.Thread(target=WaitForDjangoReady)
        #     thread.daemon = True
        #     thread.start()


def WaitForDjangoReady():
    while not apps.ready:
        time.sleep(1)
    print("Django is ready")
    from .apis import MgntThreadingSubmitProcess

    MgntThreadingSubmitProcess()