from django.shortcuts import render
from django.views.generic import TemplateView
from dashboard.views import RenderSideBar


class ReportsView(TemplateView):
    def get(self, request, *args, **kwargs):
        sidebarHtml = RenderSideBar(request)
        context = {'sidebar': sidebarHtml}
        return render(request, 'dashboard.html', context)


class ReportDetailView(TemplateView):
    def get(self, request, *args, **kwargs):
        pass

