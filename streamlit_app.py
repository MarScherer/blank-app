import streamlit as st
import pandas as pd
import json
import uuid
import requests 
from requests.auth import HTTPBasicAuth

#YjRhYWQxMGYtZjgxZS00OGRlLTg1NjYtODhjMmU2YjY0MDQ1
#https://staging.product-sustainability.com

st.title("☁️ PS API Upload")

## Inputs
APIKey = st.text_input("Enter Your API Key")
BaseURL = st.text_input("Enter Your Base URL")
GroupAvailable = False
excelfile = None
Variant = None
dict = {}

## Get GroupID
if APIKey != "" and BaseURL != "":
    try:
        header = {'Accept': 'application/json', 'Authorization':'apikey: '+ APIKey}
        GetGroupID = requests.get(BaseURL+"/api/v1/groups/default", headers=header).json()
        GroupID = GetGroupID["id"]
        GroupName = GetGroupID["name"]

        st.write("Using PS Orga: " + GroupName + " ✅")

        GroupAvailable = True

    except:
        st.write("Error Requesting Group, please check Input ❌")

## Get Projects from Group
if GroupAvailable:
    GetProjects = requests.get(BaseURL + "/api/v1/" + GroupID + "/projects?types=4&pageIndex=0&pageSize=20", headers=header).json()

    AllProjects = pd.json_normalize(GetProjects["items"])
    Projects = AllProjects[['id','name','createdBy','createdDateUtc']]
    #st.dataframe(Projects)

    ProjectList = Projects["name"].to_list()

    SelectedProject = st.selectbox("Select Project for Upload",ProjectList)
    SelectedProjectRow = Projects.loc[Projects["name"]==SelectedProject].reset_index(drop=True)
    SelectedProjectID = SelectedProjectRow.iloc[0]["id"]
    st.write("Selected Project: ", SelectedProject, " - ", SelectedProjectID)

## Upload Excel File and Type Variant Name
if GroupAvailable:
    excelfile = st.file_uploader("Upload Excel file", type="xlsx")    
    Variant = st.text_input("Enter Your Variant Name")

if excelfile is not None and Variant != "":
    excel = pd.read_excel(excelfile, sheet_name=0, header=8)
    st.dataframe(excel)

    if st.button("Upload PO"):
        st.write("Uploading")


## Functions
def GetUUID(name, dict):
        
    if name in dict:
        return{"dict": dict, "ID":dict[name]}
    else:
        newID = str(uuid.uuid4())
        dict.update({name:newID})
        return{"dict": dict, "ID":dict[name]}




        


