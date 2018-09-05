from django.apps import AppConfig


class SubmitConfig(AppConfig):
    name = 'submit'
    def ready(self):
        print("Hello")
# from django.apps import AppConfig
#
#
# class MyAppConfig(AppConfig):
#     name = 'submit'
#     verbose_name = "My Application"
#     def ready(self):
#         print("Hello submit is starting up")