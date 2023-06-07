from django.contrib import admin
from django.contrib.auth import get_user_model

from .forms import ClientCreationForm,ClientChangeForm, SOWChangeForm, SOWCreationForm, ProjectChangeForm, ProjectCreationForm, AvatureSteps, AvatureStepsChange, AddProjectMetrics, ChangeProjectMetrics, WeblinksForm
from .models import Clients, projects, statement_of_work, avature_steps, project_metrics,Weblinks

# def make_employee(modeladmin, request, queryset):
#     queryset.update(is_employee = True)
# make_employee.short_description = "Mark Selected as Employee"

# def make_admin(modeladmin, request, queryset):
#     queryset.update(is_adminUser = True)
# make_admin.short_description = "Mark Selected as Administrator"

class ClientUserAdmin(admin.ModelAdmin):
    add_form = ClientCreationForm
    form = ClientChangeForm
    model = Clients
    list_display = ['name','location','id']

class SOWUserAdmin(admin.ModelAdmin):
    add_form = SOWCreationForm
    form = SOWChangeForm
    model = statement_of_work
    list_display = ['name','client','id']

class ProjectUserAdmin(admin.ModelAdmin):
    add_form = ProjectCreationForm
    form = ProjectChangeForm
    model = projects
    list_display = ['name','sow','id']
    
class AvatureStepsAdmin(admin.ModelAdmin):
    add_form = AvatureSteps
    form = AvatureStepsChange
    model = avature_steps
    list_display = ['name']
    
class ProjectMetricsAdmin(admin.ModelAdmin):
    add_form = AddProjectMetrics
    form = ChangeProjectMetrics
    model = project_metrics
    list_display = ['external_step', 'step','start_date', 'metric_value', 'sow']

admin.site.register(Clients, ClientUserAdmin)
admin.site.register(statement_of_work, SOWUserAdmin)
admin.site.register(projects, ProjectUserAdmin)
admin.site.register(avature_steps, AvatureStepsAdmin)
admin.site.register(project_metrics, ProjectMetricsAdmin)
