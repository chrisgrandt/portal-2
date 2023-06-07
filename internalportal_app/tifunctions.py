from calendar import week
from cmath import nan
from email import header
from email.policy import default
from gettext import find
from heapq import merge
from inspect import getfile
from re import T
import string
import pandas as pd
import datetime as dt
from datetime import datetime
import numpy as np
from django.templatetags.static import static
from django.contrib.auth import authenticate, login as auth_login, REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required, user_passes_test
from azure.storage.blob import BlobServiceClient, BlobClient
from requests import request
from .models import *
from users_app.models import *

from io import StringIO
import json
import os

BASE_PATH = os.path.dirname(os.path.realpath(__file__))

STORAGEACCOUNTURL = "https://talintelstore.blob.core.windows.net"
STORAGEACCOUNTKEY = "LuXmBbMyb2npuPG5rux0NrZGBvby1jNCWE44h1yLoUPxZ7nKnPCGHwiP4K0F3VOQOtOCbsmcLDxD+dpdYJNPLA=="

my_file = "Hormel-all_current.csv"
CONTAINERNAME = "ti-data"
BLOBNAME = "csv/pipeline/"
BLOBSTART = "csv/pipeline/"
BLOBSTARTALTERNATE = "csv/pipelines/"

# from .models import project_metrics


def bms_check(CustomUser):
    
    return str(CustomUser.company) == "BMS"

def client_list(html):

    table = pd.read_html(html)
    client_table = table[0]
    client_list = client_table[['Client', 'Goal Alignment']].drop_duplicates().sort_values(by=['Client']).rename(columns={"Goal Alignment": "Alignment"})
        
    return client_list.to_dict('r')

def step_list(html,company,alignment = "Default"):
    df = pd.read_html(html)
    df = df[0]
    df.columns = [c.replace(' ', '_') for c in df.columns]
    df = df.loc[df['Company'] == company]
    df = df.loc[df['Goal_Alignment'] == alignment]
    step_list = list(df.Target_Step.unique())
    return step_list

def project_list(html, company, alignment="Default"):
    
    table = pd.read_html(html)
    assert len(table) == 1
    project_table = table[0]
    project_table = project_table.loc[project_table['Company'] == company]
    project_table = project_table.loc[project_table['Goal Alignment'] == alignment].drop_duplicates('Name')
    project_table.columns = project_table.columns.str.lower().str.replace(' ', '_')

    projects = project_table.to_dict('records')
      
    return projects

def weeks_between(date1, date2):
    first_date = date1.isocalendar()
    second_date = date2.isocalendar()
    first_week = first_date[1]

    if second_date[0] != first_date[0]:
        add_weeks = (second_date[0]-first_date[0]) * 52
        second_week = second_date[1] + add_weeks
    else:
        second_week = second_date[1]
    
    weeks = second_week - first_week
    return weeks

def data_creation(html, steps, sow_id, proj_id = 0):
    tables = pd.read_html(html)
    assert len(tables) == 1
 
    data = tables[0]
    
    for key in steps:
        for s in steps[key]:
            step_name = s
            data['Step'] = data['Step'].str.replace(step_name, key, case = False)
          
    data['Step start time'] = pd.to_datetime(data['Step start time'])
    data = data.sort_values("Step start time").drop_duplicates(['Step', 'Applicant'], keep='first').sort_index()
    
    return data

def create_table(table, project = 'All', start_date = dt.datetime(2019,1,1), end_date = dt.datetime.now()):
    if project != 'All':
        table = table.loc[table['Pipeline'] == project]
        
    table = table.loc[(table['Step start time'] > start_date) & (table['Step start time'] < end_date)]
    return table

def sow_metrics(table, steps, project_start = dt.datetime(2019,1,1), length='All', base = 1):
    
    metrics = {}
    target_list = []
    actual_list = []
    color_list = []
    goal_value = steps  
                       
    for step in steps:
        adjustment = steps[step][1]
        goal_value = steps[step][0]
        start = project_start
        end = dt.datetime.now()
        weeks = weeks_between(start,end)
        project_length = weeks
        adjusted_weeks = weeks - adjustment
        
        if length != 'All':         
            weeks = 1
            adjusted_weeks = 1
        
        if adjusted_weeks > 0 and project_length >= adjusted_weeks:
            base *= goal_value
            goal_value = round((base) * adjusted_weeks)
        else:
            goal_value = "N/A"
        
        step_count = len(table.loc[table['Step'] == step])


        if isinstance(goal_value, str) or goal_value == 0:
            color_code = "normal"
        elif step_count/goal_value >= 0.9:
            color_code = "good"
        elif step_count/goal_value < 0.75:
            color_code = "bad"
        elif step_count/goal_value >= 0.75 and step_count/goal_value < 0.90:
            color_code = "warning"
        else:
            color_code = "normal"

        target_list.append(goal_value)
        actual_list.append(step_count)
        color_list.append(color_code)
        my_lists = zip(actual_list, target_list, color_list)

        if length == 'week':
            metrics['week'] = list(my_lists)
        else:
            metrics['total'] = list(my_lists)
      
    return metrics

def person_weekly(html, person_id = 0):
    data = pd.read_html(html)
    table = data[0]
    table['Date'] = pd.to_datetime(table['Date']).dt.date
    table['Steps'] = pd.Categorical(table['Steps'], ['Bio Call Completed', 'Presented to Client', 'Candidate Accepted', 'Interview 1 Completed'])

    if person_id != 0:
        table = table[table['Consultant'] == person_id]
    
    table = table.groupby(['Consultant', 'Date', 'Steps']).size().to_frame()
    pivot = pd.pivot_table(table, index=['Consultant', 'Date'], columns=['Steps']).rename(columns={0: 'Candidate Delivery'}).fillna('0').astype(int)
    
    return pivot.to_html()

def person_capacity(html, person_id = 0):

    data = pd.read_html(html)
    table = data[0]
    
    table2 = table[['Additional Consultants', 'Project Type']].dropna()
    table = table[['Project Owner', 'Project Type']].dropna()
    table2.rename(columns={'Additional Consultants':'Consultants'}, inplace = True)
    
    table2[['Consultant1', 'Consultant2', 'Consultant3', 'Consultant4']]=table2['Consultants'].str.split(" ", expand = True)
    table2['Project Owner'] = table2['Consultant1'] + " " + table2['Consultant2']
    table_to_combine = table2[['Project Owner', 'Project Type']]

    table2['Project Owner'] = table2['Consultant3'] + " " + table2['Consultant4'].dropna()
    table = pd.concat([table, table_to_combine, table2]) 

    columns = table['Project Type'].unique().tolist()

    table = table.groupby(['Project Owner', 'Project Type']).size().to_frame()
    pivot = pd.pivot_table(table, index=['Project Owner'], columns=['Project Type']).fillna('0').astype(int)
    pivot.columns = pivot.columns.droplevel(0)
    pivot = pivot.reset_index().rename_axis(None, axis=1)
    pivot['Total'] = pivot.sum(axis=1)

    return pivot.to_html(index=False)   

def people_metrics(html, person_id=0):
    data = pd.read_html(html)
    table = data[0]

    if person_id != 0:
        table = table[table['Consultant']== person_id]

    weekly_data = pd.pivot_table(table, values=['Bio Call Completed'],index=['Consultant'], columns=['Bio Call Completed'], aggfunc=len)
    table = weekly_data.fillna('0')

    return table.to_html()

def user_list(html, person_id=0):
    users = "https://talentintelligence.avature.net/PublicLists/-K4j_JaGnz5E0Pk9BLfoaniI0G7HJbUl"
    users_data = pd.read_html(users)
    user_table = users_data[0]
    users_list = user_table['Full name'].to_list()
    
    bios_completed_data = pd.read_html(html)
    bios_completed_table = bios_completed_data[0]
    bio_user_list = bios_completed_table['Consultant'].to_list()

    no_bios_list = list(set(users_list)-set(bio_user_list))

    return no_bios_list

def target_actuals(data, date, tf):
    today = datetime.now()
    last_monday = today + dt.timedelta(days=-today.weekday(), weeks=-1)
    if data['Metric_Start']<= today and data['Metric_End']>= date:
        if data['Metric_Start'] > last_monday:
            Weekly_target = 0
        else:
            Weekly_target = data['Target_Count']/data['Step_Length']
        Overall_target = Weekly_target * data['Step_Weeks']        
    elif data['Metric_Start'] < today:
    
        Weekly_target = 0
        Overall_target = data['Target_Count']
    else:
        Weekly_target = 0
        Overall_target = 0
    
    if tf == 'Overall':
        return int(Overall_target)
    else:
        return int(Weekly_target)

def step_replace(data, internal, external):
    data.loc[data["Step"].str.contains(internal), "Step"] = external
    data

def new_metrics(company, projects, alignment):
    html = 'https://talentintelligence.avature.net/PublicLists/'
    html2 = 'https://talentintelligence.avature.net/PublicReports/'
    pipeline = projects
    today = datetime.now()
    last_monday = today + dt.timedelta(days=-today.weekday(), weeks=-1)
    last_sunday = last_monday + dt.timedelta(days=6)
    
    pipelines = pd.read_html(pipeline)
    pipelines = pipelines[0]
    pipelines = pipelines.loc[pipelines['Company']==company]
    pipelines = pipelines.loc[pipelines['Goal Alignment']==alignment]
    pipelines.columns = [c.replace(' ', '_') for c in pipelines.columns]
    
    pipelines['Date'] = pd.to_datetime(pipelines['Date'])
    pipelines['Metric_Start'] = pipelines.apply(lambda row: row.Date + dt.timedelta(weeks= row.Start_Week), axis =1)
    pipelines['Metric_End'] = pipelines.apply(lambda row: row.Date + dt.timedelta(weeks= row.End_Week), axis =1)
    pipelines['Step_Length'] = pipelines.apply(lambda row: row.End_Week - row.Start_Week , axis =1)
    pipelines['Step_Weeks'] = pipelines.apply(lambda row: weeks_between(row.Metric_Start, today), axis=1)
    pipelines['Overall'] = pipelines.apply(lambda x: target_actuals(x, today, 'Overall'), axis=1)
    pipelines['Weekly'] = pipelines.apply(lambda x: target_actuals(x, today, 'Weekly'), axis=1)
    pipelines['Target_Step'] = pipelines['Target_Step'].astype('category')
    
    step_list = list(pipelines.Target_Step.unique())
    project_list = list(pipelines.Name.unique())
    column_list = step_list.copy()
    column_list.insert(0,'Name')

    ext = pipelines['List_Extension'].iloc[0]

    cands = html2+ext
    
    candidates = pd.read_html(cands)
    candidates = candidates[0]

    if alignment == "Default":
        step_change = [("Presented", "Presented"), ("Interview", "F2F"), ("Socialization", "Phone"), ("Hired", "Hire"), ("Offer", "Hire"), ("Pipelined", "Hire")]
    elif "Candidate Accepted" in alignment:
        step_change = [("Presented", "Presented"), ("Accepted", "Accepted")]
    elif alignment ==  "Pipeline":
        step_change = [("Presented", "Presented"), ("Socialization", "Phone"), ("Pipelined", "Pipelined")]
    
    for step in step_change:
        step_replace(candidates, step[0], step[1])

    candidates = candidates.sort_values("Step start time").drop_duplicates(['Step', 'Applicant'], keep='first').sort_index().rename(columns={'Step': "Step"})
    candidates['Step start time'] = pd.to_datetime(candidates['Step start time'])
    weekly_candidates = candidates.loc[(candidates['Step start time'] > last_monday) & (candidates['Step start time'] < last_sunday)]
    candidates = candidates.groupby(['Pipeline', 'Step']).size().reset_index(name = 'Counts')
    weekly_candidates = weekly_candidates.groupby(['Pipeline', 'Step']).size().reset_index(name = 'Counts')
    
    my_dict = {}
    my_proj = {}

    for project in project_list:
        my_proj[project]= {}
        for step in step_list:
            my_proj[project][step]= [0]
        for row in candidates.itertuples():

            if row.Pipeline == project:
                if row.Step in step_list:
                    my_proj[project][row.Step] = [row.Counts] 
    
    for proj in my_proj:
        for step in step_list:
            my_proj[proj][step].append(0)
        for row in weekly_candidates.itertuples():
            if row.Pipeline == proj:
                if row.Step in step_list:
                    my_proj[proj][row.Step][-1]= row.Counts
    
    for proj in my_proj:
        for row in pipelines.itertuples():
            if row.Name == proj:
                if row.Target_Step in step_list:
                    my_proj[proj][row.Target_Step].append(row.Overall)
                    my_proj[proj][row.Target_Step].append(row.Weekly)
                for num in [0, 1]:
                    if my_proj[proj][row.Target_Step][num+2] != 0:
                        if my_proj[proj][row.Target_Step][num]/my_proj[proj][row.Target_Step][num+2] >= 0.9:
                            my_proj[proj][row.Target_Step].append("Good")
                        elif my_proj[proj][row.Target_Step][num]/my_proj[proj][row.Target_Step][num+2] < 0.75:
                            my_proj[proj][row.Target_Step].append("Bad")
                        elif (my_proj[proj][row.Target_Step][num]/my_proj[proj][row.Target_Step][num+2] < 0.9) and my_proj[proj][row.Target_Step][num]/my_proj[proj][row.Target_Step][num+2] >= 0.75:
                            my_proj[proj][row.Target_Step].append("Warning")
                    else:
                        my_proj[proj][row.Target_Step].append("Neutral")
      
    return my_proj

def separate_pipelines(csvfile, logged_user = "default",storageaccounturl = STORAGEACCOUNTURL, storageaccountkey = STORAGEACCOUNTKEY):
    blob_service_client_instance = BlobServiceClient(account_url=storageaccounturl, credential=storageaccountkey)
    BLOBNAME = BLOBSTART + csvfile
    blob_client_instance = blob_service_client_instance.get_blob_client(CONTAINERNAME, BLOBNAME, snapshot=None)
    blob = blob_client_instance.download_blob().content_as_text()
    df = pd.read_csv(StringIO(blob))

    if logged_user != "default":
        df = df[df["Project Contacts"].str.contains(logged_user, na=False)]

    if 'Status' in df.columns:
        df = df[df["Status"].astype(str).str.contains("Closed") == False]

    if 'Project Codename' and 'Is Confidential?' in df.columns:
        df = df[['Linked pipeline', 'Pipeline ID', 'Project Codename', 'Is Confidential?']].drop_duplicates()
    else: 
        df = df[['Linked pipeline', 'Pipeline ID']].drop_duplicates()

    df['Linked pipeline'] = df['Linked pipeline'].str.replace("\/", " ", regex=True)
    if 'Is Confidential?' in df.columns:        
       df.loc[df['Is Confidential?'] == "Confidential", 'Linked pipeline'] = df['Project Codename'].fillna('Confidential Role')

    my_dict = df.set_index('Linked pipeline').to_dict()['Pipeline ID']

    df = df['Linked pipeline'].unique()
    
    pipeline_list = df


    return my_dict

def present_candidates(pipelinename = "default", client = "default", storageaccounturl = STORAGEACCOUNTURL, storageaccountkey = STORAGEACCOUNTKEY):
    
    if client != "default":
        csvfile = get_file(client)
        BLOBNAME = BLOBSTART +  csvfile
    else:
        BLOBNAME = BLOBNAME

    step_categories = ["Bio Call Completed", "Presented to Client", "Interview 1 Requested", "Socialization Requested", "Socialization Scheduled", "Pipelined"]

    blob_service_client_instance = BlobServiceClient(account_url=storageaccounturl, credential=storageaccountkey)
    blob_client_instance = blob_service_client_instance.get_blob_client(CONTAINERNAME, BLOBNAME, snapshot=None)
    blob = blob_client_instance.download_blob().content_as_text()
    df = pd.read_csv(StringIO(blob))

    
    df['Linked pipeline step'] = pd.Categorical(df['Linked pipeline step'], categories=step_categories)
    df = df.sort_values(by="Linked pipeline step")
    df = df[df["Linked pipeline step"].str.contains("Declined")==False]
        
    if pipelinename != "default":
        df = df.loc[df['Linked pipeline']==pipelinename]

    df.loc[df['Resume URL'].isnull(), 'Last name'] = df['Last name'] + "^"
    df.loc[df['Resume URL'].isnull(), 'Resume URL'] = df['LI Profile URL']        
    df = df[['First name', 'Last name', 'Resume URL', 'Linked pipeline step']]        
    df['Candidate Name'] = df['First name'] + " " + df['Last name']
    df.loc[df['Resume URL'].str.contains('.doc'), 'Candidate Name']= df['Candidate Name']
    df = df[['Candidate Name', 'Resume URL', 'Linked pipeline step']]
    df = df.drop_duplicates(subset='Candidate Name')
    my_list = df.values.tolist()
    
    thisDict = df.set_index('Candidate Name').to_dict()['Resume URL']
    df = df.to_html(index=False)
    myitems = list(thisDict.keys())
    myvalues = list(thisDict.values())
    zippedLists = zip(myitems,myvalues)
    zippedLists = list(zippedLists)
   
   
    return my_list

def display_candidate(candidatename = "default", client="Hormel", pipeline = "default"):

    if client != "default":
        csvfile = get_file(client)
        BLOBNAME = BLOBSTART +  csvfile
    else:
        BLOBNAME = BLOBNAME 

    blob_service_client_instance = BlobServiceClient(account_url=STORAGEACCOUNTURL, credential=STORAGEACCOUNTKEY)
    blob_client_instance = blob_service_client_instance.get_blob_client(CONTAINERNAME, BLOBNAME, snapshot=None)
    blob = blob_client_instance.download_blob().content_as_text()
    df = pd.read_csv(StringIO(blob))

    if pipeline == "default":
        
        df.loc[df['Resume URL'].isnull(), 'Last name'] = df['Last name'] + "^"
        df.loc[df['Resume URL'].isnull(), 'Resume URL'] = df['LI Profile URL']

        df = df[['First name', 'Last name', 'Resume URL']]
        df['Candidate Name'] = df['First name'] + " " + df['Last name']
        df.loc[df['Resume URL'].str.contains('.doc'), 'Candidate Name']= df['Candidate Name']
        df = df[['Candidate Name', 'Resume URL']]
        df = df.loc[df['Candidate Name']== candidatename]
        thisDict = df.set_index('Candidate Name').to_dict()['Resume URL']
        df = df.to_html(index=False)

        candidate_name = list(thisDict.keys())
        candidate_resume = list(thisDict.values())
        selected_candidate = zip(candidate_name, candidate_resume)
        selected_candidate = list(selected_candidate)
    else:
        df.loc[df['Resume URL'].isnull(), 'Last name'] = df['Last name'] + "^"
        df.loc[df['Resume URL'].isnull(), 'Resume URL'] = df['LI Profile URL']

        df = df.loc[df['Linked pipeline']==pipeline]
        df = df[['First name', 'Last name', 'Resume URL']]
        df['Candidate Name'] = df['First name'] + " " + df['Last name']
        df.loc[df['Resume URL'].str.contains('.doc'), 'Candidate Name']= df['Candidate Name']
        df = df[['Candidate Name', 'Resume URL']]
        df = df.loc[df['Candidate Name']== candidatename]

        thisDict = df.set_index('Candidate Name').to_dict()['Resume URL']
        df = df.to_html(index=False)

        candidate_name = list(thisDict.keys())
        candidate_resume = list(thisDict.values())
        selected_candidate = zip(candidate_name, candidate_resume)
        selected_candidate = list(selected_candidate)

    return selected_candidate

def get_clients():
    clients = ClientCompanies.objects.all().order_by('company_name')
    return clients

def get_dashboards(client, logged_user="default"):
    
    if logged_user != "default":
        user_id = CustomUser.objects.values_list('id', flat=True).get(username = logged_user)
    
    client = ClientCompanies.objects.filter(company_name = client)
    id = client.values_list('pk', flat=True)[:1]

    if logged_user == "default":
        dashboards = Dashboards.objects.filter(related_company = id)
    else:
        dashboard_id = DashboardAccess.objects.values_list('related_dashboard').filter(user_reference = user_id)
        dashboards = Dashboards.objects.filter(related_company = id)
        dashboards = Dashboards.objects.filter(id__in = dashboard_id)
        # dashboards = Dashboards.objects.filter(id = dashboard_id)

    if dashboards.count() != 0:
         dashboards = dashboards
    
    else:
        dashboards = ""
    
    return dashboards

def get_dataframe(BLOBNAME, usealternate= False,storageaccounturl = STORAGEACCOUNTURL, storageaccountkey = STORAGEACCOUNTKEY):  

    if usealternate:
        BLOBNAME = BLOBSTARTALTERNATE + BLOBNAME
    else:
        BLOBNAME = BLOBSTART + BLOBNAME

    blob_service_client_instance = BlobServiceClient(account_url=storageaccounturl, credential=storageaccountkey)
    blob_client_instance = blob_service_client_instance.get_blob_client(CONTAINERNAME, BLOBNAME, snapshot=None)
    blob = blob_client_instance.download_blob().content_as_text()
    df = pd.read_csv(StringIO(blob))

    return df

def get_file(client):
    client = ClientCompanies.objects.filter(company_name = client)
    id = client.values_list('pk', flat=True)[:1]
    pipelinefile = CandidatePresentation.objects.filter(company_name = id)

    if pipelinefile.count() != 0:
        pipelinefile = pipelinefile.get().file_name
        
    else:
        pipelinefile = ""

    return pipelinefile

def get_pipelines(client, logged_user = "default"):

    pipelinefilename = get_file(client)
    if pipelinefilename == "":
        pipelines = pipelinefilename
    else:
        pipelines = separate_pipelines(pipelinefilename, logged_user)

    return pipelines

def dashboard_select(dashboard):
    dashboards = Dashboards.objects.filter(dashboard_name = dashboard)[:1]
    return dashboards

def mapping_presentations(pipelinename = "default", client = "default", storageaccounturl = STORAGEACCOUNTURL, storageaccountkey = STORAGEACCOUNTKEY):
    
    if client != "default":
        csvfile = get_file(client)
        BLOBNAME = csvfile
    else:
        BLOBNAME = BLOBNAME

    step_categories = [ 
    "Contacted", "Awaiting Client Presentation","Bio Call Scheduled","Bio Call Completed", "Bio Call Invite", "Presented to Client",
    "Interview 1 Requested", "Interview 1 Invite", "Interview 1 Completed", "Interview 1 Scheduled", 
    "Interview 2 Invite","Interview 2 Requested", "Interview 2 Completed", "Interview 2 Scheduled", 
    "Interview 3 Requested", "Interview 3 Invite", "Interview 3 Completed", "Interview 3 Scheduled", 
    "Interview 4 Scheduled", "Interview 4 Invite", "Interview 4 Completed", 
    "Socialization Requested", "Socialization Scheduled", "Socialization Completed",
    "Pipelined", "Assessment", 
    "Offer Pending", "Offer Accepted", "Hired", "Designated Successor", "Designated Successor - Uncontacted",
    "Client Declined", "Candidate Declined", "TI Declined", "No Response", 
    "Mapping Presented", "Reviewing Qualifications", "Pending Feedback after Presentation", "Candidate Accepted", "Pending Client Interview Feedback"]

    headers = ['First name', 'Last name', 'Resume URL', 'Linked pipeline step', 'Position title', 'Employer', 'Last note', 'Presentation Notes', 'Client Feedback', 'Bio Call Completed', 
    'Interview 1 Completed', 'Interview 2 Completed','Pipelined', 'Presented to Client', 'Socialization Completed', 'Candidate picture URL', 'Project Type', 'Work history', 'Start Date', 
    'Location', 'Person ID', 'iFrame', 'Pipeline ID','Last step update', 'Portal Bio'] 

    

    df = get_dataframe(BLOBNAME)
    df.sort_values(by='Last step update', ascending=False, inplace=True)

    if 'Mapping Presented' in df:
         headers = ['First name', 'Last name', 'Resume URL', 'Linked pipeline step', 'Position title', 'Employer', 'Last note', 'Presentation Notes', 'Client Feedback', 'Bio Call Completed', 
        'Interview 1 Completed', 'Interview 2 Completed','Pipelined', 'Presented to Client', 'Socialization Completed', 'Mapping Presented','Candidate picture URL', 'Project Type', 'Work history', 'Start Date', 
        'Location', 'Person ID', 'iFrame', 'Pipeline ID','Last step update', 'Portal Bio'] 

    df['Presented to Client']= df['Presented to Client'].fillna(df['Mapping Presented'])

    # check if returnId is needed for analytics
    df = df[df['Linked pipeline step'] != "Identified/New Candidate"]

    # check if bios should be included in the mappying

    final_headers = ['Candidate Name', 'Resume URL', 'Linked pipeline step', 'Position title', 'Employer', 'Last note', 'Presentation Notes', 'Client Feedback', 'Bio Call Completed', 'Interview 1 Completed', 'Interview 2 Completed','Pipelined', 'Presented to Client', 'Socialization Completed', 'Candidate picture URL', 'Start Date', 'Location', 'Person ID', 'Last step update', 'Portal Bio','iFrame', 'Pipeline ID','Project Type']

    df["Home states/provinces"].fillna('', inplace=True)
    df["Home states/provinces"] = df["Home states/provinces"].str.replace("\[home\]", "", regex=True)

    df["Home cities"].fillna(' ', inplace=True)
    df["Home cities"] = df["Home cities"].str.replace("\[home\]", "", regex=True)

    df["Home countries"].fillna(' ', inplace=True)
    df["Home countries"] = df["Home countries"].str.replace("\[home\]", "", regex=True)

    df['Location'] = df['Home cities'] + ', ' + df['Home states/provinces'] + ', ' + df['Home countries']
    df['Location'] = df['Location'].str.replace(' ,', '')
    df['Location']=df['Location'].str.replace('\[\]', "", regex=True)
    
    df = df.replace((np.nan, ''), (None, None))

    
    df['Linked pipeline step'] = pd.Categorical(df['Linked pipeline step'], categories=step_categories)
    df = df.sort_values(by="Linked pipeline step")
    # df = df[df["Linked pipeline step"].str.contains("Declined")==False]
        
    print(pipelinename)

    if pipelinename != "default":
        df = df.loc[df['Pipeline ID'].values.astype(str)==pipelinename]

    df.loc[df['Resume URL'].isnull(), 'Last name'] = df['Last name'] + "^"
    df.loc[df['Resume URL'].isnull(), 'Resume URL'] = df['LI Profile URL']   

    df["start"]= df["Work history"].str.find('Start date:')
    df["start"] = pd.to_numeric(df["start"],errors='coerce')
    df = df.dropna(subset=['start'])
    df['start'] = df['start'].astype(int)
    df["start plus"] = df["start"] + 20

    if df['Work history'].notnull().any():
        df["Start Date"] = df.apply(lambda x: x['Work history'][int(x['start'])+12:int(x['start plus'])], 1)
    else:
        df["Start Date"] = "Unknown"

    df = df[headers]  
    df['Portal Bio'].fillna("No", inplace=True)      
    df['Candidate Name'] = df['First name'] + " " + df['Last name']
    df.loc[df['Resume URL'].str.contains('.doc').fillna(False), 'Candidate Name']= df['Candidate Name']
    df = df[final_headers]
    df = df.drop_duplicates(subset='Candidate Name')
    df.sort_values(['Last step update', 'Employer'], ascending=[False, True], inplace=True)
    
    my_list = df.values.tolist()

   
    return my_list

# def insights(pipelinename = "default", client = "default", storageaccounturl = STORAGEACCOUNTURL, storageaccountkey = STORAGEACCOUNTKEY):
    

    if client != "default":
        csvfile = get_file(client)
        BLOBNAME = csvfile
    else:
        BLOBNAME = BLOBNAME

    # step_categories = ["Bio Call Completed", "Presented to Client", "Interview 1 Requested", "Socialization Requested", "Socialization Scheduled", "Pipelined"]
    headers = ["Person ID","Gender","Multi-Culturally Diverse?", "Linked pipeline", "Home states/provinces"]
    insight_headers = ["Insights Label 1",  "Insights Text 1", "Insights Label 2", "Insights Text 2"]
    west_states = ["California", "Portland", "Washington"]
    east_states = ["New York", "New Jersey", "Massachusetts", "Pennsylvania", "Maryland", "Delaware", "Maine", "Virginia"]

    df = get_dataframe(BLOBNAME)

    df = df.replace((np.nan, ''), (None, None))
        
    if pipelinename != "default":
        df = df.loc[df['Linked pipeline']==pipelinename]

    df["Home states/provinces"] = df["Home states/provinces"].str.replace("home", "")
    df["Home states/provinces"] = df["Home states/provinces"].str.strip('[]')

    df["Home cities"] = df["Home cities"].str.replace("home", "")
    df["Home cities"] = df["Home cities"].str.strip('[]')

    df["Home countries"].fillna('', inplace=True)
    df["Home countries"] = df["Home countries"].str.replace("home", "")
    df["Home countries"] = df["Home countries"].str.strip('[]')

    insights_df = df[insight_headers].fillna('').drop_duplicates(insight_headers)

    if 'Location 1' in df and df['Location 1'].iloc[0] is not None:
        direction_stats = {}
        location_headers = ['Location 1', 'Percent 1', 'Location 2', 'Percent 2', 'Location 3', 'Percent 3', 'Location 4', 'Percent 4']
        manual_loc = True
        df_loc = df[location_headers]
        df_loc.drop_duplicates(subset='Location 1')
        for i in range(1,5):
            direction_stats[df_loc['Location ' + str(i)].iloc[0]] = df_loc['Percent ' + str(i)].iloc[0]
    else:
        manual_loc = False

    text_insights = insights_df.to_dict()

    df = df[headers]
    df.fillna("", inplace=True)

    
    df["Direction"] = df["Home states/provinces"].apply(lambda x: "West" if any([s in x for s in west_states]) else "East" if any([s in x for s in east_states]) else "Other")

    df.loc[df['Gender'].isnull(), 'Gender'] = "Unknown"
    df.loc[df['Multi-Culturally Diverse?'].isnull(), 'Multi-Culturally Diverse?'] = "Unknown"
    df = df.drop_duplicates(subset='Person ID')
    
    gender_stats = (df['Gender'].value_counts(normalize=True)*100).sort_index(ascending=True).round(0).to_dict()
    diversity_stats = (df['Multi-Culturally Diverse?'].value_counts(normalize=True)*100).sort_index(ascending=True).round(0).to_dict()
    if not manual_loc:
        direction_stats = (df['Direction'].value_counts(normalize=True)*100).sort_index(ascending=True).round(0).to_dict()

    return gender_stats, diversity_stats, direction_stats, manual_loc

def proj_level(logged_user="default"):
    tifile = "Project Level Reporting-all.csv"

    df = get_dataframe(tifile)

    df.dropna(axis=0, subset=["Presented to Client"])

    headers = ["Linked pipeline", "Project Owner", "Additional Consultants", "Date", "Target Close Date","Deliverables Accepted", "Deliverables Placements", "Delivered Presented", "Delivered Accepted", "Delivered Placements"]
    headers_count = ["Linked pipeline", "Project Owner", "Additional Consultants", "Date", "Target Close Date","Deliverables Accepted", "Deliverables Placements", "Delivered Presented", "Delivered Accepted", "Delivered Placements", "Presented to Client", "Accepted", "Hired", "SOW Accepted", "SOW Placements"]
    
    df.sort_values('Linked pipeline step', ascending=True)

    df['users'] = df['Project Owner']+ " " +df['Additional Consultants'] + df['Business Development Relationship Owner']

    if logged_user != "default":
        df = df[df["users"].str.contains(logged_user, na=False)]

    df['Additional Consultants'] = df['Additional Consultants'].fillna('None')
    df['Target Close Date'] = "2100-1-1"
    df['Deliverables Accepted'] = 0
    df['Deliverables Placements'] = 0
    df['Delivered Presented'] = 0
    df['Delivered Accepted'] = 0
    df['Delivered Placements'] = 0
    df['Accepted'] = df['Candidate Accepted'].fillna(df['Socialization Completed']) + df['Socialization Completed'].fillna(df['Interview 1 Completed']) + df['Interview 1 Completed']
    df['Presented to Client'] = df['Presented to Client'].fillna(df['Socialization Completed'] + df['Interview 1 Completed'])
    df = df[headers_count]

    df = df.groupby(headers, as_index=False).count()

    df['Deliverables Accepted'] = df['SOW Accepted']
    df['Deliverables Placements'] = df['SOW Placements']
    df['Delivered Presented'] = df["Presented to Client"]
    df['Delivered Accepted'] = df['Accepted']
    df['Delivered Placements'] = df['Hired']

    df = df[headers]

    my_dict = df.to_dict('index')

    return my_dict

def dict_edit(new_list):
    d = {}
    for key, value in new_list:
        if key not in d:
            d[key] = []
        d[key].append(value)
    return d

def list_to_dict(new_list):
    keys = []
    values = []
    for items in new_list:
        keys.append(items[0])
        values.append(items[1:])

    d = dict(zip(keys,values))
    
    return d

def current_status(step_name="default", logged_user = "default"):
    tifile = "Project Level Reporting-all.csv"
    
    df = get_dataframe(tifile)

    df['users'] = df['Project Owner']+ " " +df['Additional Consultants'].fillna('') + " " + df['Business Development Relationship Owner'].fillna('') + " " + df['Solutions Account Director'].fillna('')

    if logged_user != "default":
        df = df[df["users"].str.contains(logged_user, na=False)]

    df['Current Step'] = df['Linked pipeline step']

    daysInStep = "Days in current pipeline step"

    df.loc[df['Linked pipeline step'].str.contains('Present|Candidate Accepted', case=False),'Linked pipeline step'] = 'Submitted'
    df.loc[df['Linked pipeline step'].str.contains('Socialization', case=False),'Linked pipeline step'] = 'Socialized/Interview'
    df.loc[df['Linked pipeline step'].str.contains('Interview', case=False),'Linked pipeline step'] = 'Socialized/Interview'
    df.loc[df['Linked pipeline step'].str.contains('Offer|Hire|Designated', case=False),'Linked pipeline step'] = 'Offer'

    df.loc[df['Linked pipeline step'].str.contains('Submitted', case=True),'Submitted'] = df['Full name']

    df.loc[df['Linked pipeline step'].str.contains('Socialized/Interview', case=True),'Socialized/Interview'] = df['Full name']
    
    df.loc[df['Linked pipeline step'].str.contains('Offer|Hire|Designated', case=True),'Offer'] = df['Full name']

    headers = ['Linked pipeline', step_name, daysInStep, 'Current Step']
    headers_minus = ['Linked pipeline', step_name]

    df = df[headers]
    df[daysInStep] = df[daysInStep].map(str)

    if step_name == 'Offer':
        df[step_name] = df[step_name] + ' (' + df['Current Step'] + ')'
    else:
        df[step_name] = df[step_name] + ' ('  +df[daysInStep] + ') ' + " - "+ df['Current Step']

    

    df = df[headers_minus]

    df = df.groupby(headers_minus, as_index=False).count()

    my_submitted = df.values.tolist()

    my_dict = dict_edit(my_submitted)

    return my_dict

def proj_level_test(logged_user="default"):
    tifile = "Project Level Reporting-all.csv"

    df = get_dataframe(tifile)

    # df.dropna(axis=0, subset=["Presented to Client"])

    # headers = ["Linked pipeline", "Project Owner", "Additional Consultants", "Date", "Target Close Date","Deliverables Accepted", "Deliverables Placements", "Delivered Presented", "Delivered Accepted", "Delivered Placements","Submitted","Days in submitted","Socialized/Interview","Days in interviewing"]
    headers = ["Linked pipeline", "Project Owner", "Additional Consultants", "Date", "Target Close Date","Deliverables Accepted", "Deliverables Placements", "Delivered Presented", "Delivered Accepted", "Delivered Placements", "Pipeline ID"]
    headers_count = ["Linked pipeline", "Project Owner", "Additional Consultants", "Date", "Target Close Date","Deliverables Accepted", "Deliverables Placements", "Delivered Presented", "Delivered Accepted", "Delivered Placements", "Presented to Client", "Accepted", "Hired", "Offer Accepted", "Offer Extended", "Offer Rejected","SOW Accepted", "SOW Placements", "Pipeline ID"]

   
    df.sort_values('Linked pipeline step', ascending=True)

    df['users'] = df['Project Owner']+ " " +df['Additional Consultants'].fillna('') + " " + df['Business Development Relationship Owner'].fillna('')+ " " + df['Solutions Account Director'].fillna('')

    if logged_user != "default":
        df = df[df["users"].str.contains(logged_user, na=False)]


    df['Interview 1 Completed'] = df['Interview 1 Requested'].fillna(df['Interview 1 Scheduled'].fillna(df['Interview 1 Completed']))

    df['Socialization Completed'] = df['Socialization Requested'].fillna(df['Socialization Scheduled'].fillna(df['Socialization Completed']))

    df['Hired'] = df['Hired'].fillna(df['Offer Rejected']).fillna(df['Offer Accepted']).fillna(df['Offer Extended'])
    
    df['Additional Consultants'] = df['Additional Consultants'].fillna('None')
    df['Target Close Date'].fillna('Unknown',inplace=True)
    df['Deliverables Accepted'] = df['SOW Accepted']
    df['Deliverables Placements'] = df['SOW Placements']
    df['Delivered Presented'] = 0
    df['Delivered Accepted'] = 0
    df['Delivered Placements'] = 0
    df['Accepted'] = df['Candidate Accepted'].fillna(df['Socialization Completed'].fillna(df['Interview 1 Completed'].fillna(df['Pipelined'])))

    if 'Designated Successor' in df:
        headers_count = ["Linked pipeline", "Project Owner", "Additional Consultants", "Date", "Target Close Date","Deliverables Accepted", "Deliverables Placements", "Delivered Presented", "Delivered Accepted", "Delivered Placements", "Presented to Client", "Accepted", "Hired", "Designated Successor","SOW Accepted", "SOW Placements", "Pipeline ID"]
        df['Hired'] = df['Hired'].fillna(df['Designated Successor'])
    
    if 'Designated Successor - Uncontacted' in df:
        headers_count = ["Linked pipeline", "Project Owner", "Additional Consultants", "Date", "Target Close Date","Deliverables Accepted", "Deliverables Placements", "Delivered Presented", "Delivered Accepted", "Delivered Placements", "Presented to Client", "Accepted", "Hired", "Designated Successor","SOW Accepted", "SOW Placements", "Pipeline ID"]
        df['Hired'] = df['Hired'].fillna(df['Designated Successor - Uncontacted'])

    
    df = df[headers_count]

    df = df.groupby(headers, as_index=False).count()

    df['Delivered Presented'] = df["Presented to Client"]
    df['Delivered Accepted'] = df['Accepted']
    df['Delivered Placements'] = df['Hired']
    
    df = df[headers]

    my_submitted = df.values.tolist()

    return my_submitted

def insight_text(pipelinename = "default", client = "default"):
    
    if client != "default":
        csvfile = get_file(client)
        BLOBNAME = csvfile
    else:
        BLOBNAME = BLOBNAME

    insight_headers = ["Insights Label 1",  "Insights Text 1", "Insights Label 2", "Insights Text 2"]

    df = get_dataframe(BLOBNAME)

    df = df.replace((np.nan, ''), (None, None))
        
    if pipelinename != "default":
        df = df.loc[df['Linked pipeline']==pipelinename]

    insights_df = df[insight_headers].fillna('').drop_duplicates(insight_headers)

    insights_text = insights_df.values.tolist()

    return  insights_text
    
def separate_weeks():
    start_date = dt.date(2022,8,15)
    start_date =  start_date - dt.timedelta(days=start_date.weekday())
    end_date = dt.date(2022,12,12)
    end_date = end_date - dt.timedelta(days=end_date.weekday())

    no_of_weeks = ((end_date-start_date)/dt.timedelta(days=7))

    list_dates = []
    weekly = start_date

    while weekly <= end_date:
        list_dates.append(weekly.strftime('%b-%d'))
        weekly += dt.timedelta(days=7)

    return list_dates

def spreadsheet_view():
    bmsFile = "BMS Accepted Candidates-all.csv"
    df = get_dataframe(bmsFile, True)

    no_way_home_list = ["All states/provinces", "All cities", "All countries", "All phone numbers", "All emails"]
    for my_word in no_way_home_list:
        df[my_word]= df[my_word].str.replace("home", "")
        df[my_word]= df[my_word].str.replace('\[\]', "")

    df.rename(columns={'Full name':'Name','All states/provinces':'State or Province','Linked pipeline':'Pipeline','Project Contacts':'Project-Contacts', 'Project Owner':'Project-owner', 'Date Presented':'Date_Presented', 'High Potential': 'High-potential', 'All cities': 'City', 'All countries':'Country'}, inplace=True)
    
    df.drop(['Last update', 'Person ID', 'First name', 'Last name', "Presented to Client"], axis=1, inplace=True)
    df.fillna('', inplace=True)
    
    return [df.columns.to_list()] + df.values.tolist()

def date_targets(start_date, end_date, weeks_prior=0):
    pass

def metrics_count(myFile, pipeline=0, previous_week=0):

    relevant_cols = ["Bio Call Completed", "Presented to Client", "Candidate Accepted"]
    BLOBNAME =  myFile
    df = get_dataframe(BLOBNAME)
    
    df['Interview 1 Completed'] = df['Interview 1 Requested'].fillna(df['Interview 1 Scheduled'].fillna(df['Interview 1 Completed']))
    df['Socialization Completed'] = df['Socialization Requested'].fillna(df['Socialization Scheduled'].fillna(df['Socialization Completed']))
    df['Candidate Accepted'] = df['Candidate Accepted'].fillna(df['Socialization Completed'].fillna(df['Interview 1 Completed'].fillna(df['Pipelined'])))

    if pipeline != "default":
        df = df.loc[df['Linked pipeline'] == pipeline]

    this_week = dt.date.today().isocalendar()[1]
    relevant_week = this_week - previous_week
    df= df[relevant_cols].apply(pd.to_datetime)
    for col in relevant_cols:
        df[col] = df[col].dt.isocalendar().week

  
    if previous_week > 0:
  
        return df[df == relevant_week].count().to_dict()
    else:
        return df.count().to_dict()

def proj_metric_basics(myFile, pipeline=0):

    BLOBNAME = myFile
    df = get_dataframe(BLOBNAME)

    if pipeline != "default":
        df = df.loc[df['Linked pipeline'] == pipeline]

    basic_fields = ['Date', 'Target Close Date', 'Linked pipeline', 'Bio Call Target', 'Presented Target', 'SOW Accepted']
    df = df[basic_fields]
    df.drop_duplicates(inplace=True)
    df['Target Close Date'] = pd.to_datetime(df['Target Close Date'])
    df['Date'] = pd.to_datetime(df['Date']).dt.date

    today = dt.date.today().isocalendar()[1] 
    close_week = df['Target Close Date'].dt.isocalendar().week

    if close_week.values[0]-today <= 0:
        df['Weeks Remaining'] = 0
    else:    
        df['Weeks Remaining'] = close_week - today

    df['Target Close Date'] = df['Target Close Date'].dt.date

    return df.to_dict(orient="records")

def get_iframe(myfile, pipeline = 4495):

    df = get_dataframe(myfile)
    df = df.drop_duplicates('Pipeline ID').fillna(0)   
    df['Pipeline ID'] = df['Pipeline ID'].astype(int)

    df = df.loc[df['Pipeline ID'] == int(pipeline)]
    
    df = df[['Pipeline ID', 'iFrame']].fillna(0)
    df['iFrame'] = df['iFrame'].astype(str)

    iFrame = df['iFrame'].values[0]

    return iFrame

def create_biography_section(id, company, type = "default"):

    bio_file = get_file(company)
    df = get_dataframe(bio_file).fillna('')

    df.rename(columns={"Willing to relocate?":"Willing to Relocate"}, inplace=True) 

    df = df.loc[df['Person ID'] == int(id)]
    

    df['Name'] = df['First name'] + " " + df['Last name']
    df['Location'] = df['Home cities'] + ", " + df['Home states/provinces'] + " " + df['Home countries']
    df['Degree'] = df['Willing to Relocate']
    df["Location"] = df["Location"].str.replace("\[home\]", "")

    default_fields = ['Name', 'Position title', 'Employer', 'Location', 'Candidate picture URL']


    if type == "main":
        main_body_list = df['Main Body Fields'].values[0].split(",")
        main_body_list = [x.strip(' ') for x in main_body_list]
        df = df[main_body_list].to_dict('r')
        return df
 
    if type == "key":
        key_data_list = df['Key Data Fields'].values[0].split(",")
        key_data_list = [x.strip(' ') for x in key_data_list]
        df = df[key_data_list].to_dict('records')
        return df

    if type == "default":
        df = df[default_fields].to_dict('records')
        return df












