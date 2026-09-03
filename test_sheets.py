import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

creds_file = 'configs/google_credentials.json'
spreadsheet_id = '1iC5p-Jr9SP8oRxGh8cclNDwNeNvLY_QxCXFtkhCJ2rA'

if not os.path.exists(creds_file):
    print('ERROR: No existe google_credentials.json')
else:
    print('OK: Credenciales encontradas')
    try:
        creds = service_account.Credentials.from_service_account_file(
            creds_file,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        service = build('sheets', 'v4', credentials=creds)
        
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = spreadsheet.get('sheets', [])
        if sheets:
            sheet_name = sheets[0]['properties']['title']
            print(f'OK: Hoja encontrada: {sheet_name}')
            
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"'{sheet_name}'"
            ).execute()
            
            values = result.get('values', [])
            print(f'OK: {len(values) - 1} respuestas encontradas')
            
            if len(values) > 1:
                print(f'OK: Ultima respuesta: {values[-1][:3]}...')
        else:
            print('ERROR: No hay hojas en el spreadsheet')
    except Exception as e:
        print(f'ERROR: {e}')
