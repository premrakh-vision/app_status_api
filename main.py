from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import requests
from bs4 import BeautifulSoup
import json

app = FastAPI()

@app.get('/api/app_status')
def get_app_status():
    get_data = requests.get("https://app-manager-api.maheshpatel.me/api/app/get-all-app-packages")
    if(get_data.status_code == 200):
        app_data = {}
        data_string = get_data.content.decode('utf-8')  # Use the appropriate encoding if needed

        json_data = json.loads(data_string)
        data = json_data['data']
        success_count = 0
        for app_info in data:
            app_id = None
            try:
                app_id = app_info["packageName"]
                url = f'https://play.google.com/store/apps/details?id={app_id}'
                
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    app_name_element = soup.find('h1', itemprop='name')
                    if app_name_element:
                        status = "Active"
                    else:
                        status = "InActive"

                    app_data[app_id] = status
                else:
                    app_data[app_id] = "InActive"
            except:
                pass
            
            if(app_id):
                app_status = app_data.get(app_id)
                update_data = {   
                    "packageName": app_id,
                    "status" : app_status
                }            
                update_api = requests.post("https://app-manager-api.maheshpatel.me/api/app/modify-app-status-based-on-playconsole",data=update_data)

                if update_api.status_code == 200:
                    success_count+=1    

        if success_count == len(data):
            return JSONResponse(content={'status':'success','message':'all data successfully updated'},status_code=200)
        elif success_count:
            return JSONResponse(content={'status':'success','message':f'{len(data)} out of {success_count} data successfully updated'},status_code=400)
        else:
            return JSONResponse(content={'status':'fail','message':'app status not updated'},status_code=400)
    else:
        return JSONResponse(content={'status':'fail','message':'app status not updated'},status_code=400)