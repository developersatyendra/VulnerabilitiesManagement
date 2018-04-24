from django.shortcuts import render
from django.views.generic import TemplateView
from dashboard.views import RenderSideBar


class ProjectsView(TemplateView):
    def get(self, request, *args, **kwargs):
        sidebarHtml = RenderSideBar(request)
        context = {'sidebar': sidebarHtml}
        return render(request, 'dashboard.html', context)

class ProjectDetailView(TemplateView):
    def get(self, request, *args, **kwargs):
        pass

