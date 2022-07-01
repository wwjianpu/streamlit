from cv2 import DFT_SCALE
import pandas as pd
from datetime import datetime
from rsa import verify
import secrets
from locale import str
import streamlit as st
import requests, json

if 'refresh_token' not in st.session_state: st.session_state['refresh_token'] = False
if 'access_token_response' not in st.session_state: st.session_state['access_token_response'] = ''
if 'token' not in st.session_state: st.session_state['token'] = ''
if 'pdf_file' not in st.session_state: st.session_state['pdf_file'] = None
if 'docId' not in st.session_state: st.session_state['docId'] = ''

st.header('Get Token')
with st.container():
    token_url = st.text_input('token url', '')

    c1, c2, c3 = st.columns(3)
    with c1:
        scope = st.text_input('scope', '')
    with c2:
        client_id = st.text_input('client_id', '')
    with c3:
        client_secret = st.text_input('client_secret', '', type="password")

    if token_url == "": 
        if "token_url" in st.secrets['apiurl']: token_url = st.secrets['apiurl']['token_url']
    if scope == "":
        if "scope" in st.secrets['apiurl']: scope = st.secrets['apiurl']['scope']
    if client_id == "":
        if "client_id" in st.secrets['apiurl']: client_id = st.secrets['apiurl']['client_id']
    if client_secret == "":
        if "client_secret" in st.secrets['apiurl']: client_secret = st.secrets['apiurl']['client_secret']

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button('get token'):
            if st.session_state['token'] == '' or st.session_state['refresh_token']:

                data = {'grant_type': 'client_credentials', 
                    'scope': scope,
                    'client_id': client_id,
                    'client_secret': client_secret}
                    
                access_token_response = requests.post(token_url, data=data, verify=False, allow_redirects=False )

                # print (access_token_response.headers)
                # print (access_token_response.text)
                
                st.session_state['access_token_response'] = json.loads(access_token_response.text)
                if "error" in st.session_state['access_token_response']:
                    st.error(st.session_state['access_token_response']['error_description'])
                else:
                    st.session_state['token'] = st.session_state['access_token_response']['access_token']
            else:
                st.warning('token already available. Aborted!')

    with col2:
        st.checkbox("refresh token", value=False, key="refresh_token")

st.header('API 2')
with st.container():
    api_url = st.text_input('api2 url', '')
    if api_url == "":
        if "api_url" in st.secrets['apiurl']:
            api_url = st.secrets['apiurl']['api_url']

    woundsData = {
        'uid': ['76212', '76213'],
        'etiology': ['Pressure Injury', 'Surgical'],
        'loc': ['Sacrum/Buttock', 'Left Lower leg'],
        'onsetDate': ['2022-05-20', '2022-01-16']
    }
    
    dfw = pd.DataFrame(woundsData)
    dfwInfos = pd.DataFrame()


    woundChoice = ['All']
    woundChoice.extend(dfw.uid)

    c1, c2, c3 = st.columns(3)
    with c1:
        patHospCode = st.text_input('Pat Hosp Code', 'QMH')
        caseNum = st.text_input('Case No.', 'HN15000186X')
        docType = st.text_input('docType', 'woundAxRpt')
    with c2:
        docDateType = st.selectbox('Date range type', ('ADR', 'PFW', 'SDR'))
        if (docDateType=='SDR'):
            docStartDate = st.date_input('start date')
            docEndDate = st.date_input('end date')
        else:
            docStartDate = ''
            docEndDate = ''
    with c3:
        # woundInfos = st.multiselect('select wound', ['All', 'wound 1', 'wound2'])
        woundSelected = st.multiselect('select wound', woundChoice)

    if 'All' in woundSelected:
        dfwInfos = dfw
    else:
        for id in woundSelected:
            dfwInfos = dfwInfos.append(dfw[dfw.uid == id])

    woundInfos = json.loads(dfwInfos.to_json(orient="records"))

    data = {
        'patHospCode': patHospCode,
        'caseNum': caseNum,
        'docType': docType,
        'docDateType': docDateType,
        'woundInfos': woundInfos
    }
    date_format='%Y-%m-%d'
    if (docDateType=='SDR'):
        data['docStartDate'] = docStartDate.strftime(date_format)
        data['docEndDate'] = docEndDate.strftime(date_format)

    
    # data = json.dumps(data)

    api_call_headers = {'Authorization': 'Bearer ' + st.session_state['token']}

    if st.button('API2', disabled=(api_url=='')):
        
        print("BODY: ", data)

        # headers = req.headers
        # data, json = req.body
        # parms = req.query
        # files (file-tuple )= {'parmName': ('filename', file-like-object, minetype) }

        # res = requests.get(url=api_url, headers=api_call_headers, verify=False, params=params)
        # user data parm for Node
        # use json parm type for AWS
        get_doc_id_res = requests.post(url=api_url, headers=api_call_headers, verify=False, json=data)
        
        
        print("POST", api_url, get_doc_id_res.status_code, get_doc_id_res.text)
        # print(get_doc_id_res.headers)
        st.session_state['get_doc_id_res'] = json.loads(get_doc_id_res.text)

        if "error" in st.session_state['get_doc_id_res']:
            # st.error(st.session_state['get_doc_id_res']['message'])
            st.error('failed')
        else:
            if get_doc_id_res.status_code == 201:
                st.session_state['patientPseudoId'] = st.session_state['get_doc_id_res']['patientPseudoId']
                st.session_state['docId'] = st.session_state['get_doc_id_res']['docId']

        st.write(get_doc_id_res.status_code, get_doc_id_res.text)
    
st.header('API 3')
with st.container():
    api3_url = st.text_input('api3 url', '')
    if api3_url == "":
        if "api3_url" in st.secrets['apiurl']:
            api3_url = st.secrets['apiurl']['api3_url']
    
    docId = st.text_input('manual assign docId')
    if docId == "":
        if st.session_state['docId'] == "":
            st.warning('doc Id not available. Aborted!')
        else:
            docId = st.session_state['docId']


    pdf_file = st.file_uploader('select pdf file', 'pdf')
    if pdf_file is not None:
        st.session_state['pdf_file'] = pdf_file
        
    if st.button('API3', disabled=(api3_url=='' or pdf_file is None or docId=='')):
        bytes_data = st.session_state['pdf_file'].getvalue()
        api_call_headers = {'Authorization': 'Bearer ' + st.session_state['token']}
        params = { 'docId': docId }

        file = {
            'file': ('myfile.pdf', bytes_data, 'application/pdf')
        }

        res = requests.post(url=api3_url, headers=api_call_headers, verify=False, params=params, files=file) # unexpected field

        # file = {
        #     'form': bytes_data
        # }

        # res = requests.post(url=api3_url, headers=api_call_headers, verify=False, params=params, data=bytes_data) #File is missing
        # res = requests.post(url=api3_url, headers=api_call_headers, verify=False, params=params, data=file) # Internal server error
        # res = requests.post(url=api3_url, headers=api_call_headers, verify=False, params=params, files=file) # unexpected field

        print(res.url)
        print("POST", api3_url, res.status_code, res.text)

        st.write(res.status_code, res.text)
    
st.write(st.session_state)
    
    
    

