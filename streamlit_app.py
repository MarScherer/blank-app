import streamlit as st
import pandas as pd
import json
import uuid
import requests 
from requests.auth import HTTPBasicAuth

#YjRhYWQxMGYtZjgxZS00OGRlLTg1NjYtODhjMmU2YjY0MDQ1
#https://staging.product-sustainability.com

st.title("☁️ PS API Upload")

## Functions
def CreateVariantWithPO():
    json = ""

    URL = BaseURL + "/api/v1/" + GroupID + "/projects/" + SelectedProjectID + "/variants"

    POjson = CreatePOJSON()
    BOMjson = CreateJSONBOM()
    AutoMappingMode = 1
    variantDescr = "Uploaded with Streamlit App"
    AnalysisID = 25

    json = "{\"autoMappingMode\": " + str(AutoMappingMode) + ",\"name\":\"" + Variant + "\", \"description\":\" " + variantDescr + "\",\"analysisFeatures\": " + str(AnalysisID) + ",  \"startCalculation\": true,\"lcaProjectDetails\": " + "{ \"parameters\": [],\"productionOrders\": [ " + POjson + "], \"billOfMaterials\" : [" + BOMjson + "]} }"

    PSResponse = requests.post(URL, headers=header, data=json)

    ResponseCode = PSResponse.status_code
    #st.write(ResponseCode)
    #st.write(PSResponse)

    if PSResponse.status_code < 300:
        st.write("Upload was successful ✅")
        st.link_button("Open Project", PSURL)
    else:
        st.title("No Succes ❌ Error Code: ",ResponseCode)
        #st.write(json)


def CreatePOJSON():
    POjson = ""
    strPOName = "TestPO"
    strProduct = excel.iloc[0]["Assembly"]
    strProductID = str(uuid.uuid4())
    dict.update({strProduct:strProductID})
    strUnit = excel.iloc[0]["Unit"]
    intQuantity  = 1

    POjson = "{\"name\" : \"" + strPOName + "\", \"productId\": \"" + strProductID + "\", \"productName\": \"" + strProduct + "\", \"productUnit\": \"" + strUnit + "\", \"quantity\": " + str(intQuantity) + "}"
    return POjson

def CreateJSONBOM():

    FirstBOM = True
    FirstItem = True

    excellen = len(excel.index)

    BOMjson = ""
    
    for dfrow in excel.iterrows():

        row = dfrow[0]

        SameAssembly = excel.isnull().iloc[row]["Assembly"]
        AssemblyName = excel.iloc[row]["Assembly"]
        AssemblyID = GetUUID(AssemblyName, dict)["ID"]
        AssemblyQty = str(excel.iloc[row]["Quantity"])
        AssemblyUnit = excel.iloc[row]["Unit"]
        AssemblyProcess = excel.iloc[row]["Process"]

        ComponentName = excel.iloc[row]["Component"]
        ComponentID = GetUUID(ComponentName, dict)["ID"]
        ComponentQty = str(excel.iloc[row]["Quantity.1"])
        ComponentUnit = excel.iloc[row]["Unit.1"]
        try:
            if not excel.isnull().iloc[row]["Classifications"]:
                ComponentAttributes = excel.iloc[row]["Classifications"]
            else:
                ComponentAttributes = ""
        except:
            ComponentAttributes = ""
        

        if not SameAssembly:

            FirstItem = True

            if FirstBOM:
                
                BOMjson = BOMjson + "{ \"productId\": \"" + AssemblyID + "\" , \"productName\": \"" + AssemblyName + "\" , \"productUnit\" : \"" + AssemblyUnit + "\" , \"quantity\": " + AssemblyQty + ", \"processName\" : \"" + AssemblyProcess + "\" , \"items\": ["
                FirstBOM = False

            else:
                BOMjson = BOMjson + ",{ \"productId\": \"" + AssemblyID + "\" , \"productName\": \"" + AssemblyName + "\" , \"productUnit\" : \"" + AssemblyUnit + "\" , \"quantity\": " + AssemblyQty + ", \"processName\" : \"" + AssemblyProcess + "\" , \"items\": ["

        if FirstItem:

            BOMjson = BOMjson + "{ \"id\": \"" + ComponentID
            FirstItem = False

        else:
            BOMjson = BOMjson + ",{ \"id\": \"" + ComponentID

        BOMjson = BOMjson + "\" , \"name\" : \"" + ComponentName + "\" , \"unit\" : \"" + ComponentUnit + "\" , \"classifications\":  [" + str(ComponentAttributes) + "], \"quantity\" : " + ComponentQty + "}"

        if row + 1 < excellen: 
            if not excel.isnull().iloc[row+1]["Assembly"]:
                BOMjson = BOMjson + "]}"

    BOMjson = BOMjson + "]}"

    return BOMjson

def GetUUID(name, dict):
        
    if name in dict:
        return{"dict": dict, "ID":dict[name]}
    else:
        newID = str(uuid.uuid4())
        dict.update({name:newID})
        return{"dict": dict, "ID":dict[name]}
    

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
        header = {'Accept': 'application/json', 'Authorization':'apikey: '+ APIKey, 'Content-Type':'application/json'}
        GetGroupID = requests.get(BaseURL+"/api/v1/groups/default", headers=header).json()
        GroupID = GetGroupID["id"]
        GroupName = GetGroupID["name"]
        RelativePath = GetGroupID["relativePath"]
        

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

    PSURL = BaseURL + RelativePath + "/lca/" + SelectedProjectID + "/overview"

## Upload Excel File and Type Variant Name
if GroupAvailable:
    excelfile = st.file_uploader("Upload Excel file", type="xlsx")    
    Variant = st.text_input("Enter Your Variant Name")

if excelfile is not None and Variant != "":
    excel = pd.read_excel(excelfile, sheet_name=0, header=8)
    #st.dataframe(excel)

    if st.button("Upload PO"):
        CreateVariantWithPO()
