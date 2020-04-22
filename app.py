from flask import Flask, request, make_response
import json
import os
from flask_cors import cross_origin
from SendEmail.sendEmail import EmailSender
from logger import logger
from email_templates import template_reader
import requests
import pandas as pd

app = Flask(__name__)



# geting and sending response to dialogflow
@app.route('/webhook', methods=['POST'])
@cross_origin()
def webhook():

    req = request.get_json(silent=True, force=True)

    #print("Request:")
    #print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    #print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


# processing the request from dialogflow
def processRequest(req):

    log = logger.Log()
    sessionID=req.get('responseId')
    result = req.get("queryResult")
    user_says=result.get("queryText")
    log.write_log(sessionID, "User Says: "+user_says)
    #parameters = result.get("parameters")

    
    intent = result.get("intent").get('displayName')

    if (intent=='covid_selection'):
        
        parameters = result.get("parameters")
        cust_name = parameters.get("user_name")
        cust_contact = parameters.get("user_number")
        cust_email = parameters.get("user_email")
        course_name = 'CoronaFAQ'

        email_sender=EmailSender()
        template= template_reader.TemplateReader()
        email_message=template.read_course_template(course_name)
        
        email_sender.send_email_to_user(cust_email,email_message)
        #email_file_support = open("email_templates/support_team_Template.html", "r")
        #email_message_support = email_file_support.read()
        #email_sender.send_email_to_support(cust_name=cust_name,cust_contact=cust_contact,cust_email=cust_email,body=email_message_support)
        fulfillmentText="FAQ has been sent your mail id. Do you wan to continue conversation?"
        log.write_log(sessionID, "Bot Says: "+fulfillmentText)
        return {
            "fulfillmentText": fulfillmentText
        }
    elif (intent =='covid_intent'):
        parameters = result.get("parameters")
        st = parameters.get("State_Name")
        url = "https://corona-virus-world-and-india-data.p.rapidapi.com/api_india"

        headers = {
            'x-rapidapi-host': "corona-virus-world-and-india-data.p.rapidapi.com",
            'x-rapidapi-key': "ad8a7c9180msh729a7f9bc08c271p14f0c7jsn97160dd9c399"
        }

        response = requests.request("GET", url, headers=headers)
        # print(response.text)

        parsed_data = json.loads(response.text)

        # print(json.dumps(parsed_data,indent = 4,sort_keys = True))

        def flatten_json(json):
            out = {}

            def flatten(x, name=''):

                if type(x) is dict:
                    for a in x:
                        flatten(x[a], name + a + '_')
                else:
                    out[name[:-1]] = x

            flatten(json)
            return out

        df = pd.DataFrame.from_dict(flatten_json(parsed_data), orient='index')
        print(df.head(5))
        states = ['Andhra Pradesh','Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana',
                  'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
                  'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
                  'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Andaman and Nicobar Islands',
                  'Chandigarh', 'Dadra and Nagar Haveli', 'Daman and Diu', 'Delhi', 'Lakshadweep', 'Puducherry',
                  'Jammu and Kashmir', 'Ladakh']
        
        if st in states:
           print(st)
           p = df.at['state_wise_{}_confirmed'.format(st), 0]
           q = df.at['state_wise_{}_active'.format(st), 0]
           rr = df.at['state_wise_{}_deaths'.format(st), 0]
           ss = df.at['state_wise_{}_recovered'.format(st), 0]
           p1 = df.at['total_values_confirmed', 0]
           q1 = df.at['total_values_active', 0]
           r1 = df.at['total_values_deaths', 0]
           s1 = df.at['total_values_recovered', 0]
           print(p,q,rr,ss,p1,q1,r1,s1)
           fulfillmentText = 'In {} \n Confirmed Case: {}, Active Cases: {}, Deaths: {}, recovered: {}.\nIn India \n Confirmed Case: {}, Active Cases: {}, Deaths: {}, recovered: {}'.format(st,p,q,rr,ss,p1,q1,r1,s1)
           print(fulfillmentText)
           log.write_log(sessionID, "Bot Says: " + fulfillmentText)
           return {
               "fulfillmentText": fulfillmentText
               }
       
    else:
        log.write_log(sessionID, "Bot Says: " + result.fulfillmentText)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 7586))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')



