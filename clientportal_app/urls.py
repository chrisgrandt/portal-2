from django.urls import path, include
from clientportal_app import views
from internalportal_app.views import display_mapping_presentation


urlpatterns = [
    path('', views.clientportal, name='clientportal'),
    path('help', views.help, name='help'),
    path('analytics', views.tianalytics, name='tianalytics'),
    path('analytics/<dashboard>', views.dashboardselect, name='dashboardselect'),
    path('presentation', views.candidatepresentation, name='candidatepresentation'),
    path('presentation/<candidate>', views.candidateselect, name='candidateselect'),
    path('stakeholder-delivery', views.display_stakeholder_presentation_select, name='stakeholderdelivery'),
    path('stakeholder/<clientname>/<pipeline>/<projectname>', display_mapping_presentation, name='displaystakeholdermapping'),
]
