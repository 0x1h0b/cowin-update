import requests
from datetime import date
import smtplib
from email.message import EmailMessage
from time import sleep

def query(data):
    
    my_list = []

    for center in data['centers']:
        vaccine_center = {}
        vaccine_center['center-name'] = center['name']
        center_address = '{},{},{},{},{}'.format(center['address'],center['block_name'],center['district_name'],center['pincode'],center['state_name'])
        vaccine_center['address'] = center_address
        vaccine_center['price'] = center['fee_type']
        slots=[]
        for slot in center['sessions']:
            temp={}
            temp['date']=slot['date']
            temp['available_dose']=slot['available_capacity']
            temp['age_limit']= slot['min_age_limit']
            temp['vaccine']=slot['vaccine']
            temp['time-slots']=list(slot['slots'])
            if slot['min_age_limit']<=25:
                slots.append(temp)
        if slots!=[]:
            vaccine_center['slot-details']=slots
            my_list.append(vaccine_center)

    all_payload ='' 
    for i in range(len(my_list)):
        item=my_list[i]
        payload = '''
>>>>>>>>>>>>>>>>>>>
CENTER-NAME : {}
ADDRESS : {}
PRICE : {}
SLOT-DETAILS :
'''.format(item['center-name'],item['address'],item['price'])

        time_slot_payload = ''
        for idx,val in enumerate(item['slot-details']):
            if val['available_dose']==0:
                time_slot=''
                slot_payload='\t{}. {} {} vaccine available on date {}.'.format(idx+1,val['available_dose'],val['vaccine'],val['date'])
            else:
                time_slot = ' , '.join(val['time-slots'])
                slot_payload = '\t{}. {} {} vaccine available on date {} ,for below time-slots:\n{}'.format(idx+1,val['available_dose'],val['vaccine'],val['date'],time_slot)
            time_slot_payload+=(slot_payload+'\n')
        all_payload+=payload+time_slot_payload

    header = '''
Hi,

** VACCINE SLOT UPDATE **
'''
    footer = '''
    
Above results are bot generated.
Best Regards
0x1h0b
'''
    msg_string=''
    if all_payload=='':
        msg_string = header+all_payload+'\nNo new slots available for 18+ age group.'+footer
        return msg_string,False
    else:
        msg_string=header+all_payload+footer
        return msg_string,True



def mail_alert(subject,body,to):
    msg=EmailMessage()
    msg.set_content = body
    msg['subject'] = subject
    msg['to']=to

    user = "hitubag@gmail.com"
    password = 'bfofozxjmjjvzxqy'
    msg['from']=user

    server = smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login(user,password)
    server.send_message(msg)

    server.quit()



if __name__=='__main__':
    while True:
        try:
            t=date.today()
            day=t.strftime("%d-%m-%Y")
            url='https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode=766105&date='+day
            res = requests.get(url)
            data = eval(res.text)
            output,flag = query(data)
            print('Output:\n',output)
            print('Msg Flag:',flag)
            if flag:
                mail_alert('[BOT][Vaccine Update:-)',output,'himanshubag12@gmail.com')
        except Exception as e:
            print(str(e))
            output = "Hi \n following error occurred: "+str(e)
            mail_alert('[BOT] Vaccine Update !!!',output,'himanshubag12@gmail.com')
        sleep(60*3)
