import streamlit as st
import requests, json
from datetime import datetime

if 'refresh_token' not in st.session_state: st.session_state['refresh_token'] = False
if 'access_token_response' not in st.session_state: st.session_state['access_token_response'] = ''
if 'token' not in st.session_state: st.session_state['token'] = ''

if 'mailno' not in st.session_state: st.session_state['mailno'] = 'SF7444400031887'
if 'acceptAddress' not in st.session_state: st.session_state['acceptAddress'] = 'test'
if 'orderid' not in st.session_state: st.session_state['orderid'] = '100000000000004'
if 'payload' not in st.session_state: st.session_state['payload'] = None
if 'raw_payload' not in st.session_state: st.session_state['raw_payload'] = None
if 'push_response' not in st.session_state: st.session_state['push_response'] = ''


st.set_page_config(layout="wide")
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
                data = {
                    'grant_type': 'client_credentials', 
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
                    st.success(access_token_response.status_code, )
            else:
                st.warning('token already available. Aborted!')

    with col2:
        st.checkbox("refresh token", value=False, key="refresh_token")

    if st.session_state['token']:
        st.caption("Token: {0}".format(st.session_state['token']))


###############################################################################

def route_push_call(api_url, api_call_headers, payload):
    print(datetime.now(), api_url)
    print(payload)

    push_res = requests.post(url=api_url, headers=api_call_headers, verify=False, json=payload)
    
    try:
        st.session_state['push_response'] = json.loads(push_res.text)
    except Exception:
        st.session_state['push_response'] = {"error": True}

    print("POST", api_url, push_res.status_code, push_res.text)

    if "error" in st.session_state['push_response']:
        st.error("{0} - {1}".format(push_res.status_code, push_res.text))
    else:
        if push_res.status_code == 200 or push_res.status_code == 201:
            if st.session_state['push_response']['return_code'] == "0000":
                st.success("{0} - {1} - {2}".format(
                    push_res.status_code, 
                    st.session_state['push_response']['return_code'],
                    st.session_state['push_response']['return_msg']))
            else:
                st.warning("{0} - {1} - {2}".format(
                    push_res.status_code, 
                    st.session_state['push_response']['return_code'],
                    st.session_state['push_response']['return_msg']))
        else:
            st.error("{0} - {1}".format(push_res.status_code, push_res.text))

st.header('RoutePush')
with st.container():
    api_url = st.text_input('RoutePush url', '')

    if api_url == "":
        if "api_url" in st.secrets['apiurl']:
            api_url = st.secrets['apiurl']['api_url']

    opCodeMap = {
        "50": "Collected",
        "80": "Delivered",
        "70": "Failed; will retry", # exception
        "99": "Address Updated; will deliver", # exception
        "8000": "Remark for 8000" # exception
    }

    c1, c2, c3 = st.columns(3)
    with c1:
        mailno = st.text_input('Waybill No.', st.session_state['mailno'])
        acceptAddress = st.text_input('acceptAddress', st.session_state['acceptAddress'])
        reasonName = ""
        orderid = st.text_input('orderid', st.session_state['orderid'])
        acceptTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        opCode = st.selectbox('opCode', ('50', '80', '70', '99', '8000'))
        remark = st.text_input('remark', opCodeMap[opCode])
        id = datetime.now().strftime("%Y%m%d%H%M%S%s") 
        reasonCode = ""

        item = {
            
                "mailno": mailno,
                "acceptAddress": acceptAddress,
                "reasonName": reasonName,
                "orderid": orderid,
                "acceptTime": acceptTime,
                "remark": remark,
                "opCode": opCode,
                "id": id,
                "reasonCode": reasonCode,
        }
        payload = {
            "WaybillRoute" : [item]
        }
        st.session_state['payload'] = payload


    with c2:
        st.write(payload)
        api_call_headers = {'Authorization': 'Bearer ' + st.session_state['token']}
        
        if st.button('Push', disabled=(api_url=='')):

            route_push_call(api_url, api_call_headers, payload)

    with c3:
        default_value = st.session_state['raw_payload']
        if (st.session_state['raw_payload']) == None:
            default_value = json.dumps(st.session_state['payload'])

        raw_payload = st.text_area("payload", value=default_value, height=400)
        st.session_state['raw_payload'] = raw_payload
        api_call_headers = {'Authorization': 'Bearer ' + st.session_state['token']}

        try:
            payload = json.loads(raw_payload)
        except Exception:
            payload = ""
            st.error("invalid json")

        if st.button('Push with raw payload', disabled=(api_url=='' or payload=="")):

            route_push_call(api_url, api_call_headers, payload)

with st.expander("session data", expanded=False):
    st.write(st.session_state)
