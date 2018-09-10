from celery import shared_task
from submit import apis
from submit.models import SubmitModel


@shared_task
def ProcessSubmitFileTask(**kwargs):
    submitQueueElement = apis.SubmitQueueElement(submitObj=SubmitModel.objects.get(pk=kwargs['id']), overwrite=kwargs['overwrite'])
    print("[-] Started Process FoundStone Zip file.")
    retval = apis.ProcessFoundStoneZipXML(submitQueueElement)
    print("[-] Finished Process FoundStone Zip file.")
    return retval