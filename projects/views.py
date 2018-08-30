from django.shortcuts import render
from django.views.generic import TemplateView
from dashboard.views import RenderSideBar
from .forms import ProjectForm


class ProjectsView(TemplateView):
    template = 'projects/projects.html'

    def get(self, request, *args, **kwargs):
        form = ProjectForm()
        formEdit = ProjectForm(id='edit')
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
            'form': form,
            'formEdit': formEdit,
        }
        return render(request, self.template, context)


class ProjectsDetailView(TemplateView):
    template = 'projects/project_detailed.html'

    def get(self, request, *args, **kwargs):
        form = ProjectForm()
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
            'form': form,
        }
        return render(request, self.template, context)


class ProjectsScanTaskView(TemplateView):
    template = 'projects/project_scantasks.html'

    def get(self, request, *args, **kwargs):
        form = ProjectForm()
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
            'form': form,
        }
        return render(request, self.template, context)
