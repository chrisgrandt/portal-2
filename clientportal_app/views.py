from multiprocessing.sharedctypes import Value
from django.shortcuts import render
from django.http import HttpResponse
from users_app.models import  Dashboards, DashboardAccess
from django.contrib.auth.decorators import login_required, user_passes_test
from internalportal_app.tifunctions import *


# Create your views here.
@login_required
def clientportal(request):
    context = {
        "welcome_text":"Welcome to the Client Portal", 
        "title_text": "Client Portal"
    }
    return render(request, 'clientportal.html', context)

@login_required
def index(request):
    context = {
        "welcome_text":"Welcome to the Talent Intelligence Portal",
        "title_text":"Home Page"
    }
    return render(request, 'index.html', context)

@login_required
def help(request):
    context = {
        "welcome_text":"Welcome to the Help Page",
        "title_text":"Help Page"
    }
    return render(request, 'help.html', context)

@login_required
def tianalytics(request, dashboard = "default"):
    user_id = request.user.pk
    analytics = DashboardAccess.objects.filter(user_reference = user_id)
    dashboards= ""

    if dashboard == "default":
        default_dashboard = analytics[:1].get().related_dashboard
        dashboards = Dashboards.objects.filter(dashboard_name = default_dashboard)[:1].get().dashboard_reference
    else:
        dashboards = Dashboards.objects.filter(dashboard_name = dashboard)[:1].get().dashboard_reference
     
    context = {
        "title_text":"Dashboards",
        "welcome_text":"Welcome to the Future of Analytics",
        "dashboards": dashboards,
        "analytics" : analytics,
    }

    return render(request, 'presentdashboard.html', context)

@login_required
def dashboardselect(request, dashboard):
    return tianalytics(request, dashboard)

@login_required
@user_passes_test(lambda u: u.is_employee, login_url='clientportal')
def candidatepresentation(request, pipelinename = "default",candidatename = "default"):
    zippedLists = present_candidates(pipelinename)

    if candidatename == "default":
        resume = zippedLists[0][1]
        
    else:
        resume= candidatename[0][1]
        
    
    context = {
        "resume": resume,
        "zippedLists": zippedLists,
        "pipelinename": pipelinename,
        "candidatename": candidatename,
    }
    return render(request, 'candidate_presentation.html', context)

@login_required
@user_passes_test(lambda u: u.is_employee, login_url='clientportal')
def candidateselect(request, candidate, client="Hormel"):
    selected_candidate = display_candidate(candidate, client)

    return candidatepresentation(request, pipelinename="default", candidatename = selected_candidate)

@login_required
def display_stakeholder_presentation_select(request, client="BMS"):
    logged_user = request.user.username
    logged_user_company = request.user.company

    proj_level()

    if request.user.is_employee:
        client = client
        logged_user = "megan.lown@bms.com"
    else:
        client = logged_user_company

    dashboards = get_dashboards(client, logged_user)
    pipelines = get_pipelines(client, logged_user)
    filename = get_file(client)
    pipelines = list(pipelines)
    has_pipelines = True
    has_dashboards = True

    if request.user.is_employee:
        clientname = client
    else:
        clientname = logged_user_company

    pipelines = [sub.replace('/', " ") for sub in pipelines]
    
    if dashboards == "This Client Does not Have any dashboards":
        has_dashboards = False

    if pipelines == "No Pipelines for this Client":
        has_pipelines = False
        
    context = {
        "client": client,
        "dashboards":dashboards,
        "pipelines": pipelines,
        "filename": filename,
        "has_dashboards": has_dashboards,
        "has_pipelines": has_pipelines,
        "clientname": clientname
    }
    return render(request, "stakeholdermappingselect.html", context)

@login_required
def display_stakeholder_mapping_presentation(request, clientname, pipeline, candidatename="default"):
    #code to display specific pipeline template presentpipeline.html
    
    pipelinename = pipeline
    clientname = clientname
    my_insights = insights(pipelinename, clientname)

    gender_order = ["Male", "Female", "Unknown/Unspecified"]
    location_order = ["East", "West", "Other"]
    diversity_order = ["Yes", "No", "Unknown"]

    manual_location = my_insights[3]
    gender_insights = {x: my_insights[0][x] for x in gender_order if x in my_insights[0]}
    diversity_insights = {x: my_insights[1][x] for x in diversity_order if x in my_insights[1]}

    if manual_location:
        location_insights = my_insights[2]
    else:
        location_insights = {x: my_insights[2][x] for x in location_order if x in my_insights[2]}
    insights_text = insight_text(pipelinename, clientname)
 
    zippedLists = mapping_presentations(pipelinename, clientname)

    portal = "external"
             
    context = {
        "zippedLists": zippedLists,
        "pipelinename": pipelinename,
        "candidatename": candidatename,
        "clientname": clientname,
        "gender": gender_insights,
        "diversity": diversity_insights,
        "location": location_insights,
        "portal": portal,
        "insights_text": insights_text,
        "manual_loc": manual_location
    }
    
    return render(request, 'stakeholdermapping.html', context)

