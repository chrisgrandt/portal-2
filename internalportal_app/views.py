
from multiprocessing import context
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required, user_passes_test
from .tifunctions import *
from django.forms import modelform_factory
from django.forms.widgets import Select
from django import forms
from .models import Clients, statement_of_work, projects, project_metrics, Weblinks
from datetime import datetime
from .forms import WeblinksForm
import datetime as dt
from django.contrib import messages

# Create your views here.
@login_required(login_url='login')
@user_passes_test(lambda u: u.is_employee, login_url='clientportal')
def internalportal(request):

    links = Weblinks.objects.all().order_by("title")

    html = "https://talentintelligence.avature.net/PublicReports/LGTKSeOD9gI0zFQD4MYdWlqApI1GbbjB"

    person_name = "{}, {}".format(request.user.last_name, request.user.first_name)
    person_id = 0

    if not request.user.is_manager:
        my_users = ""    
        table = person_weekly(html, person_name)
    else:
        my_users = user_list(html, person_id)    
        table = person_weekly(html, person_id)

    user_name = request.user.first_name
         
    context = {
        "title_text": "Employee Portal",
        "welcome_text": "Hello, {}, where would you like to go today?".format(user_name),
        "table": table,
        "links": links,
    }
    return render(request, 'internalportal.html', context)

@login_required
@user_passes_test(lambda u: u.is_employee)
def person_metrics(request, project_view, person_id=0):
    

    if project_view == 'metrics':
    
        html = 'https://talentintelligence.avature.net/PublicReports/LGTKSeOD9gI0zFQD4MYdWlqApI1GbbjB'

        
        person_name = "{}, {}".format(request.user.last_name, request.user.first_name)
        welcome_text = "Individual Metrics (10 days)"
        title_text = "Person Metrics"

        if not request.user.is_manager:
            my_users = ""    
            table = person_weekly(html, person_name)
        else:
            my_users = user_list(html, person_id)    
            table = person_weekly(html, person_id)
        
    else:
        
        html = 'https://talentintelligence.avature.net/PublicLists/ycSLPRl0Jyh36aNOB5tyl7-nieq0YLg3'

        welcome_text = "Current Projects"
        title_text = "Project Capacity"
        my_users = ""
        table = person_capacity(html)

    context = {
        "table" : table,
        "title_text": title_text ,
        "welcome_text": welcome_text,
        "missing": my_users,
    }
       
    return render(request, 'personmetrics.html', context)

# Weblink CRUD
# Weblink create
@user_passes_test(lambda u: u.is_superuser or u.is_adminUser, login_url="/")
def addWeblink(request):
    if request.method=="POST":
        creation_form = WeblinksForm(request.POST)
  
        if creation_form.is_valid():
            creation_form.save()
            messages.success(request, ("Link Added!"))
        return redirect('viewweblinks')

    
    else:
        creation_form = WeblinksForm()

        context = {
            "title_text": "Weblinks",
            "welcome_text": "Create Weblinks",
            'creation_form': creation_form,
            
        }
        
    return render(request, 'createweblink.html', context)

# Weblink read
@user_passes_test(lambda u: u.is_superuser or u.is_adminUser, login_url="/")
def viewWeblinks(request):
    links = Weblinks.objects.all().order_by("title")
    
    return render(request, 'viewweblinks.html', {'links':links})

# Weblink Update
@user_passes_test(lambda u: u.is_superuser or u.is_adminUser, login_url="/")
def editWeblink(request, weblink_id):
    link_select = Weblinks.objects.get(pk= weblink_id)

    user_form = WeblinksForm(request.POST or None, instance = link_select)
    if user_form.is_valid():
        user_form.save()
        return redirect('viewweblinks')

    return render(request, 'editweblink.html', {'user_form':user_form})

# Weblink Delete
@user_passes_test(lambda u: u.is_superuser or u.is_adminUser, login_url="/")
def deleteWeblink(request, weblink_id):

    link_select = Weblinks.objects.get(pk = weblink_id)

    context ={'link_select' : link_select} 
  
    if request.method =="POST": 
        
        link_select.delete() 
         
        return redirect('viewweblinks')
  
    return render(request, "deleteweblink.html", context) 

# Select a Client Screen
@login_required
@user_passes_test(lambda u: u.is_employee)
def client_presentation(request):
    #code to choose a client template clientselect.html
    clients = get_clients()
    
    context = {
            "title_text": "Client List",
            "welcome_text": "Select Clients",
            'clients': clients,
            
        }
    return render(request, "clientselect.html", context)

# Dashboard and mapping selection
@login_required
@user_passes_test(lambda u: u.is_employee)
def display_presentation_select(request, client):
    dashboards = get_dashboards(client)
    pipelines = get_pipelines(client)
    filename = get_file(client)
    has_pipelines = True
    has_dashboards = True
    clientname = client
    
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

# Display the dashboard
@login_required
def dashboard_display(request, client='default', dashboard = 'default'):

    dashboards = dashboard_select(dashboard).get().dashboard_reference

    context = {
        "dashboards": dashboards,
        "client": client
    }
    return render(request, "presentdashboard.html", context)
   
@login_required
def display_mapping_presentation(request, clientname, pipeline, projectname="default", candidatename="default"):
    #code to display specific pipeline template presentpipeline.html
    pipelinename = projectname
    clientname = clientname
    projectTypePlacement = -1
    pipelineIDPlacement = -2
    iFramePlacement = -3
    createPortalBio = -4

    zippedLists = mapping_presentations(pipeline, clientname)

    # print(zippedLists)

    if zippedLists:
        projectType = zippedLists[0][projectTypePlacement]
        pipelineID = zippedLists[0][pipelineIDPlacement]
        iFrame = zippedLists[0][iFramePlacement]
        portalBio = zippedLists[0][createPortalBio]
    else:
        projectType = "None"
        pipelineID = 0
        iFrame = None
        portalBio = "No"

    portal = "internal"
             
    context = {
        "zippedLists": zippedLists,
        "pipelinename": pipelinename,
        "candidatename": candidatename,
        "clientname": clientname,
        "portal": portal,
        "pipeline_id": pipelineID,
        "project_type": projectType,
        "iFrame": iFrame,
        "portalBio": portalBio
    }

    return render(request, 'stakeholdermapping.html', context)

@login_required
@user_passes_test(lambda u: u.is_employee)
def project_level_reporting(request):

    talent_intelligence = 11
    current_user = request.user.get_full_name()
    options = CustomUser.objects.filter(company=talent_intelligence).order_by('first_name').values('first_name', 'last_name')

    #If this breaks recreate project_level_alternate with current user post method replacing user.get
    if request.method == "POST":
        current_user = request.POST.get('employee')

    submitted = current_status('Submitted',current_user)
    interview = current_status('Socialized/Interview',current_user)
    offer = current_status('Offer',current_user)
    testing_proj = list_to_dict(proj_level_test(current_user))
    
    my_table = proj_level(current_user)

    context = {
        "proj_table": my_table,
        "submitted": submitted,
        "interview": interview,
        "offer": offer,
        "reporting": testing_proj,
        "options": options
    } 

    return render(request, 'proj_lev_reporting.html', context)

@login_required
def bio_creation(request, company, id):
    
    data_default = create_biography_section(id, company)[0]
    data_keydata = create_biography_section(id, company, "key")[0]
    data_mainbody = create_biography_section(id, company,"main")[0]

        
    image_url = data_default.get("Candidate picture URL")

    if len(image_url)== 0:
        image_url = "None"


    data_default.popitem()

    context = {
        "default" : data_default,
        "keydata" : data_keydata,
        "mainbody" : data_mainbody,
        "imageurl": image_url
    }

    return render(request, 'candidatebio.html', context)

@login_required
@user_passes_test(lambda u: u.is_employee)
def project_targets(request):
    date_list = separate_weeks()

    context = {
        "datelist": date_list,
        "exportname": "Project Target Tracker Design"
    }

    return render(request, 'projecttargettracker.html', context)

@login_required
@user_passes_test(lambda u: u.is_employee)
def weekly_project_targets(request, pipelinename=0):
    
    file_name = "Weekly Metrics-all.csv"

    pipelines = separate_pipelines(file_name)

    my_data = proj_metric_basics(file_name, pipelines[int(pipelinename)])[0]
    my_counts = metrics_count(file_name, pipelines[int(pipelinename)])
    last_week = metrics_count(file_name, pipelines[int(pipelinename)],1)
    two_weeks_ago = metrics_count(file_name, pipelines[int(pipelinename)],2)
    

    bio_total = my_counts['Bio Call Completed']
    presented_total = my_counts['Presented to Client']
    accepted_total = my_counts['Candidate Accepted']

    lw_bio_total = last_week['Bio Call Completed']
    lw_presented_total = last_week['Presented to Client']
    lw_accepted_total = last_week['Candidate Accepted']

    tw_bio_total = two_weeks_ago['Bio Call Completed']
    tw_presented_total = two_weeks_ago['Presented to Client']
    tw_accepted_total = two_weeks_ago['Candidate Accepted']

    proj_name = my_data['Linked pipeline']
    proj_bios = my_data['Bio Call Target']
    proj_presented = my_data['Presented Target']
    proj_accepted = my_data['SOW Accepted']
    proj_start = my_data['Date']
    proj_end = my_data['Target Close Date']
    weeks_remaining = my_data['Weeks Remaining']

    if weeks_remaining > 0:
        weekly_target_bios = (proj_bios-bio_total)/weeks_remaining
        weekly_target_presented = (proj_presented - presented_total)/weeks_remaining
        weekly_target_accepted = (proj_accepted - accepted_total)/weeks_remaining
    else:
        weekly_target_bios = (proj_bios-bio_total)
        weekly_target_presented = (proj_presented - presented_total)
        weekly_target_accepted = (proj_accepted - accepted_total)

    if weekly_target_bios <= 0:
        weekly_target_bios = "Target Met"
    if weekly_target_presented <= 0:
        weekly_target_presented = "Target Met"
    if weekly_target_accepted <=0:
        weekly_target_accepted = "Target Met"


    context ={

        "biototal": bio_total,
        "presentedtotal": presented_total,
        "acceptedtotal": accepted_total,
        "project": proj_name,
        "accepted": proj_accepted,
        "bios": proj_bios,
        "presented": proj_presented,
        "datestart": proj_start,
        "dateend": proj_end,
        "pipelines": pipelines,
        "weeksremaining": weeks_remaining,
        "weeklytargetbios": weekly_target_bios,
        "weeklytargetpresented": weekly_target_presented,
        "weeklytargetaccepted": weekly_target_accepted,
        "lwbiocount": lw_bio_total,
        "lwpresentedcount": lw_presented_total,
        "lwacceptedcount": lw_accepted_total,
        "twbiocount": tw_bio_total,
        "twpresentedcount": tw_presented_total,
        "twacceptedcount": tw_accepted_total

    }

    return render(request, 'weeklytargettracker.html', context)


@login_required
@user_passes_test(lambda u: u.is_employee)
def pipeline_dashboards(request, client, id):

    dash_file = get_file(client)
    dashboards = get_iframe(dash_file, id)   

    context = {
        "dashboards": dashboards,
        "client": client
    }

    return render(request, "presentdashboard.html", context)

@login_required
@user_passes_test(lambda u: u.is_employee)
def avature_project_Creation(request):
    iframe = '<iframe width="640px" height="480px" src="https://forms.office.com/Pages/ResponsePage.aspx?id=Lh2p_Z9NXkOilbSqBaGaPaMQbW0qQNxPu3KKM6rDwD5UNVZONVlYVFIyNUZORFFEQjhVWDBXUVlKOS4u&embed=true" frameborder="0" marginwidth="0" marginheight="0" style="border: none; max-width:100%; max-height:100vh" allowfullscreen webkitallowfullscreen mozallowfullscreen msallowfullscreen> </iframe>'
  

    context = {
        "dashboard": iframe
        
    }

    return render(request, "avature_creation.html", context)

#This is project silver medalist figure out a way to incorporate this for multiple rendering.
@login_required
@user_passes_test(lambda u: u.is_employee or bms_check)
def spreadsheet_special(request): 

    exempt_list = ["All cities", "All countries", "State or Province","Position title", "Date", "Last note", "All phone numbers", "All emails", "City", "Country"]
    bms_table = spreadsheet_view()
    headers = bms_table.pop(0)

    company = ClientCompanies.objects.get(company_name="BMS")
    
    context ={
        "projectdata": bms_table,
        "headers": headers,
        "exempt": exempt_list
    }

    return render(request, 'spreadsheetview.html', context)


