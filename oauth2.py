from requests import request
from rsa import verify
import secrets
from locale import str
import streamlit as st
import requests, json

if 'refresh_token' not in st.session_state: st.session_state['refresh_token'] = False
if 'access_token_response' not in st.session_state: st.session_state['access_token_response'] = ''
if 'token' not in st.session_state: st.session_state['token'] = ''
if 'pdf_file' not in st.session_state: st.session_state['pdf_file'] = None

st.header('Get Token')
with st.container():
    token_url = st.text_input('token url', '')

    c1, c2, c3 = st.columns(3)
    with c1:
        scope = st.text_input('scope', '')
    with c2:
        client_id = st.text_input('client_id', '')
    with c3:
        client_secret = st.text_input('client_secret', '')

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

    c1, c2, c3 = st.columns(3)
    with c1:
        docType = st.text_input('docType', 'woundAxRpt')
    with c2:
        patHospCode = st.text_input('Pat Hosp Code', 'QMH')
    with c3:
        caseNum = st.text_input('Case No.', 'HN15000186X')

    api_call_headers = {'Authorization': 'Bearer ' + st.session_state['token']}
    params = {'docType': docType, 'patHospCode': patHospCode, 'caseNum': caseNum}

    if st.button('API2', disabled=(api_url=='')):
        res = requests.get(url=api_url, headers=api_call_headers, verify=False, params=params)
        
        print("GET", api_url, res.status_code, res.text)

        st.write(res.status_code, res.text)
    
st.header('API 3')
with st.container():
    api3_url = st.text_input('api3 url', '')
    if api3_url == "":
        if "api3_url" in st.secrets['apiurl']:
            api3_url = st.secrets['apiurl']['api3_url']
    
    pdf_file = st.file_uploader('select pdf file', 'pdf')
    if pdf_file is not None:
        st.session_state['pdf_file'] = pdf_file
        
    if st.button('API3', disabled=(api3_url=='' or pdf_file is None)):
        bytes_data = st.session_state['pdf_file'].getvalue()
        api_call_headers = {'Authorization': 'Bearer ' + st.session_state['token']}

        res = requests.post(url=api3_url, headers=api_call_headers, verify=False, data=bytes_data)
        print("POST", api3_url, res.status_code, res.text)

        st.write(res.status_code, res.text)
    
st.write(st.session_state)
    
    
    

