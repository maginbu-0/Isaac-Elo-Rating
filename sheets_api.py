###   USE py -m pip install  ###
from google.oauth2 import service_account
from googleapiclient.discovery import build


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
#values = values.set_index('Name') 

#up = values.values.tolist()

up = values.to_json()
#up = values.to_dict('records')
#request = sheet.values().update(spreadsheetId=ss_id, range='Sheet2!A2:F', valueInputOption='USER_ENTERED',body=values.to_json()).execute()

print(up)