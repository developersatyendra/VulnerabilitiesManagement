from celery import shared_task
from reports.ultil import *
from reports.models import ReportModel


@shared_task
def ProcessGenerateReportTask(**kwargs):
    reportObj = kwargs.get('report', None)
    print('[+] Task Started {}'.format(reportObj.name))
    if reportObj:
        reportObj.status = ReportModel.STATE_PROCESSING
        reportObj.save()
        if reportObj.format == ReportModel.FORMAT_PDF:
            # if mode is project
            if reportObj.mode == ReportModel.MODE_PROJECT:
                retval = PDFProjectReport(reportObj)
                if retval['status'] == -1:
                    reportObj.status = ReportModel.STATE_ERROR
                else:
                    reportObj.status = ReportModel.STATE_PROCESSED
                reportObj.save()
                return {'status': 0, 'message': 'Project report {} is successfully generated'.format(reportObj.name)}
            # if mode is scan task
            elif reportObj.mode == ReportModel.MODE_SCANTASK:
                retval = PDFScanReport(reportObj)
                if retval['status'] == -1:
                    reportObj.status = ReportModel.STATE_ERROR
                else:
                    reportObj.status = ReportModel.STATE_PROCESSED
                reportObj.save()
                return {'status': 0, 'message': 'Scan report {} is successfully generated'.format(reportObj.name)}
            # if mode is host
            elif reportObj.mode == ReportModel.MODE_HOST:
                retval = PDFHostReport(reportObj)
                if retval['status'] == -1:
                    reportObj.status = ReportModel.STATE_ERROR
                else:
                    reportObj.status = ReportModel.STATE_PROCESSED
                reportObj.save()
                return {'status': 0, 'message': 'Host report {} is successfully generated'.format(reportObj.name)}
            else:
                return {'status': -1, 'message': 'Undefined choice'}
        else:
            return {'status': -1, 'message': 'Undefined format'}
    else:
        return {'status': -1, 'message': 'Report Object Not Found'}