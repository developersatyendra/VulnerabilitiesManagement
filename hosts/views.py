from django.shortcuts import render
from django.views.generic import TemplateView
from dashboard.views import RenderSideBar


class HostsView(TemplateView):
    def get(self, request, *args, **kwargs):
        sidebarHtml = RenderSideBar(request)
        context = {'sidebar': sidebarHtml}
        return render(request, 'dashboard.html', context)


class HostDetailView(TemplateView):
    def get(self, request, *args, **kwargs):
        pass

