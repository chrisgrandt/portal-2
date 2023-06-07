from django.shortcuts import render,redirect
from .forms import CustomCreationForm, CustomChangeForm, DashboardAdditionForm, DashboardAccessForm, CompanyAdditionForm, CandidatePresentationAdditionForm, PresentationAccessForm
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from .models import CustomUser, Dashboards, DashboardAccess, ClientCompanies, CandidatePresentation, PresentationAccess


@user_passes_test(lambda u: u.is_superuser or u.is_adminUser, login_url="/")
def adduser(request):
    if request.method=="POST":
        creation_form = CustomCreationForm(request.POST)
  
        if creation_form.is_valid():
            creation_form.save()
            print("success")
            messages.success(request, ("New User Created!"))
        return redirect('adduser')

    
    else:
        creation_form = CustomCreationForm()

        context = {
            "title_text": "User Creation",
            "welcome_text": "Create a New Portal User",
            'creation_form': creation_form,
        }
        
    return render(request, 'createuser.html', context)

@login_required
def logged_in(request):


    if request.user.is_employee:
        return redirect('internalportal')
    elif str(request.user.company) == "BMS":
        return redirect('stakeholderdelivery')
    elif str(request.user.company) == "Mastercard Foundation":
        return redirect('stakeholderdelivery')
    else:
        return redirect('stakeholderdelivery')

@user_passes_test(lambda u: u.is_superuser or u.is_adminUser, login_url="/")
def view_users(request):
    users = CustomUser.objects.all()
    return render(request, 'viewuser.html', {'users':users})

@user_passes_test(lambda u: u.is_superuser or u.is_adminUser, login_url="/")
def edit_user(request, user_id):

    user_select = CustomUser.objects.get(pk= user_id)

    user_form = CustomChangeForm(request.POST or None, instance = user_select)
    if user_form.is_valid():
        user_form.save()
        return redirect('view_users')

    return render(request, 'edituser.html', {'user_form':user_form})

@user_passes_test(lambda u: u.is_superuser or u.is_adminUser, login_url="/")
def viewDashboards(request):
    access = DashboardAccess.objects.all().order_by('related_dashboard')
    dashboards = Dashboards.objects.all().order_by('dashboard_name')
    return render(request, 'viewdashboards.html', {'dashboards':dashboards, 'access':access})

@user_passes_test(lambda u: u.is_superuser or u.is_adminUser, login_url="/")
def editDashboard(request, dashboard_id):
    dashboard_select = Dashboards.objects.get(pk= dashboard_id)

    user_form = DashboardAdditionForm(request.POST or None, instance = dashboard_select)
    if user_form.is_valid():
        user_form.save()
        return redirect('view_dashboards')

    return render(request, 'editdashboard.html', {'user_form':user_form})

@user_passes_test(lambda u: u.is_superuser or u.is_adminUser, login_url="/")
def addDashboard(request):
    if request.method=="POST":
        creation_form = DashboardAdditionForm(request.POST)
  
        if creation_form.is_valid():
            creation_form.save()
            print("success")
            messages.success(request, ("Dashboard Added!"))
        return redirect('index')

    
    else:
        creation_form = DashboardAdditionForm()

        context = {
            "title_text": "Dashboards",
            "welcome_text": "Add a Dashboard",
            "creation_form": creation_form,
            
        }
        
    return render(request, 'adddashboard.html', context)



@user_passes_test(lambda u: u.is_superuser or u.is_adminUser, login_url="/")
def adminView(request):
    return render(request, 'admindashboard.html')

@user_passes_test(lambda u: u.is_superuser or u.is_adminUser, login_url="/")
def deleteDashboardAccess(request, access_id):
   
  
    # fetch the object related to passed id 
    access_select = DashboardAccess.objects.get(pk = access_id)

    context ={'access_select' : access_select} 
  
    if request.method =="POST": 
        
        access_select.delete() 
         
        return redirect('view_dashboards')
  
    return render(request, "deleteaccess.html", context) 
    
def addDashboardAccess(request):
    if request.method=="POST":
        creation_form = DashboardAccessForm(request.POST)
  
        if creation_form.is_valid():
            creation_form.save()
            messages.success(request, ("Access Added!"))
        return redirect('view_dashboards')

    
    else:
        creation_form = DashboardAccessForm()

        context = {
            "title_text": "Dashboard Access",
            "welcome_text": "Assign Users to Dashboards",
            'creation_form': creation_form,
            
        }
        
    return render(request, 'createaccess.html', context)

@user_passes_test(lambda u: u.is_superuser or u.is_adminUser, login_url="/")
def deleteDashboard(request, dashboard_id):
   
  
    # fetch the object related to passed id 
    dashboard_select = Dashboards.objects.get(pk = dashboard_id)

    context ={'dashboard_select' : dashboard_select} 
  
    if request.method =="POST": 
        
        dashboard_select.delete() 
         
        return redirect('view_dashboards')
  
    return render(request, "deletedashboard.html", context) 

@user_passes_test(lambda u: u.is_superuser or u.is_adminUser, login_url="/")
def deleteUser(request, user_id):

    user_select = CustomUser.objects.get(pk = user_id)

    context ={'user_select' : user_select} 
  
    if request.method =="POST": 
        
        user_select.delete() 
         
        return redirect('view_users')
  
    return render(request, "deleteuser.html", context) 

@user_passes_test(lambda u: u.is_superuser or u.is_adminUser, login_url="/")
def viewPresentations(request):
    access = PresentationAccess.objects.all().order_by('related_presentation')
    presentations = CandidatePresentation.objects.all().order_by('file_name')
    # Below needs updating when html is done
    return render(request, 'viewpresentations.html', {'presentations':presentations, 'access':access})

@user_passes_test(lambda u: u.is_superuser or u.is_adminUser, login_url="/")
def editPresentation(request, candidatepresentation_id):
    presentation_select = CandidatePresentation.objects.get(pk= candidatepresentation_id)

    user_form = CandidatePresentationAdditionForm(request.POST or None, instance = presentation_select)
    if user_form.is_valid():
        user_form.save()
    # Below needs updating when html is done    
        return redirect('view_presentations')

    return render(request, 'editpresentation.html', {'user_form':user_form})

@user_passes_test(lambda u: u.is_superuser or u.is_adminUser, login_url="/")
def addPresentation(request):
    if request.method=="POST":
        creation_form = CandidatePresentationAdditionForm(request.POST)
  
        if creation_form.is_valid():
            creation_form.save()
            print("success")
            messages.success(request, ("Presentation Added!"))
        return redirect('view_presentations')

    
    else:
        creation_form = CandidatePresentationAdditionForm()

        context = {
            "title_text": "Candidate Presentations",
            "welcome_text": "Add a Candidate Presentation",
            "creation_form": creation_form,
            
        }
    # Below needs updating when html is done       
    return render(request, 'addpresentation.html', context)

@user_passes_test(lambda u: u.is_superuser or u.is_adminUser, login_url="/")
def deletePresentation(request, presentation_id):
   
  
    # fetch the object related to passed id 
    presentation_select = CandidatePresentation.objects.get(pk = presentation_id)

    context ={'presentation_select' : presentation_select} 
  
    if request.method =="POST": 
        
        presentation_select.delete() 
         
        return redirect('view_presentations')
  
    return render(request, "deletepresentation.html", context) 

@user_passes_test(lambda u: u.is_superuser or u.is_adminUser, login_url="/")

def addcompany(request):
    if request.method=="POST":
        creation_form = CompanyAdditionForm(request.POST)
  
        if creation_form.is_valid():
            creation_form.save()
            print("success")
            messages.success(request, ("New Company Created!"))
        return redirect('addcompany')

    
    else:
        creation_form = CompanyAdditionForm()

        context = {
            "title_text": "Company Creation",
            "welcome_text": "Create a New Company",
            'creation_form': creation_form,
        }
        
    return render(request, 'createcompany.html', context)

@user_passes_test(lambda u: u.is_superuser or u.is_adminUser, login_url="/")
def deleteCompany(request, company_id):

    company_select = ClientCompanies.objects.get(pk = company_id)

    context ={'company_select' : company_select} 
  
    if request.method =="POST": 
        
        company_select.delete() 
         
        return redirect('view_companies')
  
    return render(request, "deletecompany.html", context) 

@user_passes_test(lambda u: u.is_superuser or u.is_adminUser, login_url="/")
def view_companies(request):
    companies = ClientCompanies.objects.all()
    return render(request, 'viewcompany.html', {'companies':companies})

@user_passes_test(lambda u: u.is_superuser or u.is_adminUser, login_url="/")
def edit_company(request, company_id):

    company_select = ClientCompanies.objects.get(pk= company_id)

    company_form = CompanyAdditionForm(request.POST or None, instance = company_select)
    if company_form.is_valid():
        company_form.save()
        return redirect('view_companies')

    return render(request, 'editcompany.html', {'user_form':company_form})

@user_passes_test(lambda u: u.is_superuser or u.is_adminUser, login_url="/")
def deletePresentationAccess(request, access_id):
   
  
    # fetch the object related to passed id 
    access_select = PresentationAccess.objects.get(pk = access_id)

    context ={'access_select' : access_select} 
  
    if request.method =="POST": 
        
        access_select.delete() 
         
        return redirect('view_presentations')
  
    return render(request, "deletepresentationaccess.html", context) 
    
def addPresentationAccess(request):
    if request.method=="POST":
        creation_form = PresentationAccessForm(request.POST)
  
        if creation_form.is_valid():
            creation_form.save()
            messages.success(request, ("Access Added!"))
        return redirect('view_presentations')

    
    else:
        creation_form = PresentationAccessForm()

        context = {
            "title_text": "Presentation Access",
            "welcome_text": "Assign Users to Presentations",
            'creation_form': creation_form,
            
        }
        
    return render(request, 'createpresentationaccess.html', context)