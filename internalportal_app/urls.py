from django.urls import path, include
from internalportal_app import views

urlpatterns = [
    path('', views.internalportal, name='internalportal'),
    path('person-metrics/<project_view>', views.person_metrics, name='personmetrics'),
    path('add-weblink', views.addWeblink, name = 'addweblink'), 
    path('edit-weblink/<weblink_id>', views.editWeblink, name = 'editweblink'),
    path('delete-weblink/<weblink_id>', views.deleteWeblink, name = 'deleteweblink'),
    path('view-weblinks', views.viewWeblinks, name = 'viewweblinks'),
    path('client-presentation/<client>', views.display_presentation_select, name='selectdborpipeline'), 
    path('client-presentation', views.client_presentation, name= 'clientpresentations'),    
    path('dashboard-presentation/<client>/<dashboard>/', views.dashboard_display, name='dashboarddisplay'),
    path('mapping-presentation/<clientname>/<pipeline>/<projectname>', views.display_mapping_presentation, name='displaymapping'), 
    path('project-level-reporting', views.project_level_reporting, name="projectlevel"),
    path('candidatebio/<company>/<id>', views.bio_creation, name='candidatebio'),
    path('target-tracker',view=views.project_targets,name='targettracker'),
    path('weekly-targets/<pipelinename>',view=views.weekly_project_targets,name='weeklytracker'),
    path('silver-medal-project',view=views.spreadsheet_special,name='silvermedal'),
    path('pipelinedashboard/<client>/<id>', view=views.pipeline_dashboards,name='pipelinedashboard'),
    path('avature-project', view=views.avature_project_Creation,name='avatureproject'), 

    
]