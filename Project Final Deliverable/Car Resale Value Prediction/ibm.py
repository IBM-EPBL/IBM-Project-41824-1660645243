from flask import Flask,render_template,request
import jsonify
import requests
import pickle
import numpy as np
import sklearn

from sklearn.preprocessing import StandardScaler

# NOTE: you must manually set API_KEY below using information retrieved from your IBM Cloud account.
API_KEY = "nsMPxkqMjnLbFOa4okSPCk2ZKV0Mr8Mry0NxF6J3KgUb"
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":
 API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]
header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}


app = Flask(__name__)
model = pickle.load(open('file.pkl','rb'))

@app.route('/',methods=['GET'])
def Home(): 
  return render_template('index.html')


standard_to = StandardScaler()

@app.route('/predict',methods = ['POST'])
def predict():
    Fuel_Type_Diesel =0
    if request.method == 'POST':
        Year = int(request.form['Year'])
        Present_Price = float(request.form['Present_Price'])
        Kms_Driven = int(request.form['Kms_Driven'])
        Owner = int(request.form['Owner'])
        Fuel_Type_Petrol = request.form['Fuel_Type_Petrol']
        if(Fuel_Type_Petrol == 'Petrol'):
            Fuel_Type_Diesel = 0
            Fuel_Type_Petrol = 1
        
        elif(Fuel_Type_Diesel=='Diesel'):
            Fuel_Type_Petrol = 0
            Fuel_Type_Diesel = 1
        else:
            Fuel_Type_Petrol = 0
            Fuel_Type_Diesel = 0
            
        Year = 2020 - Year
        Seller_Type_Individual = request.form['Seller_Type_Individual']
        if(Seller_Type_Individual=='Individual'):
            Seller_Type_Individual =1
        else: 
            Seller_Type_Individual = 0
            
        Transmission_Manual = request.form['Transmission_Manual']
        if(Transmission_Manual == 'Manual'):
            Transmission_Manual = 1
        else:
            Transmission_Manual = 0
            
        prediction = model.predict([[Present_Price,Kms_Driven,Owner,Year,Fuel_Type_Diesel,Fuel_Type_Petrol,Seller_Type_Individual,Transmission_Manual]])
        output = round(prediction[0],2)
        
        
        feilds=[Present_Price,Kms_Driven,Owner,Year,Fuel_Type_Diesel,Fuel_Type_Petrol,Seller_Type_Individual,Transmission_Manual]
        payload_scoring = {"input_data": [{"fields": [['Present_Price','Kms_Driven','Owner','Year','Fuel_Type_Diesel','Fuel_Type_Petrol','Seller_Type_Individual','Transmission_Manual']], "values": [feilds]}]}
        response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/1a9cf846-2d3f-459a-ab1f-79c098a5df4b/predictions?version=2022-11-18', json=payload_scoring,headers={'Authorization': 'Bearer ' + mltoken})
        pred=response_scoring.json()
        out=pred['predictions'][0]['values'][0][0]
        
        
        if output<0:
            return render_template('index.html',prediction_text='Sorry! You cannot sell this car')
        else:
            return render_template('index.html', prediction_text='You can sell this car at Rs.{} lakhs'.format(output))
        
    else:
        return render_template('index.html')
    
    
    
if __name__ == '__main__':
    app.run(debug=True)