###   USE py -m pip install  ###
from google.oauth2 import service_account
from googleapiclient.discovery import build
import gspread


from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
ss_id = os.getenv('key')

SERVICE_ACCOUNT_FILE = 'creds.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = None
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

service = build('sheets','v4',credentials=creds)

sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=ss_id,
                            range='Data!A1:F').execute()

values = result.get('values',[])

values = pd.DataFrame(values)
new_header = values.iloc[0] 
values = values[1:]
values.columns = new_header
#values = values.to_json()

data = [values.columns.values.tolist()]
data.extend(values.values.tolist())
value_range_body = {"values": data}

request = sheet.values().update(spreadsheetId=ss_id, range='Sheet2!A2', valueInputOption='USER_ENTERED',body=value_range_body).execute()

print(data)