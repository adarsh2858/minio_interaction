# Import different libraries

import os
import json
import argparse

from minio import Minio
from evaluate1 import evaluate
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                            BucketAlreadyExists)

# smtplib module included in python by default for email purpose

from string import Template
import smtplib, json

# import more necessary packages for sending email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

parser = argparse.ArgumentParser()
#-n  Test No. -u USERNAME
parser.add_argument("-n", help="Test Number")
parser.add_argument("-u", help="Username")

args = parser.parse_args()

# Put up environment variables here to take server name, access key and secret key from user
# Initialize the client server with an endpoint, access and secret keys.
minioClient = Minio(os.environ['SERVER_NAME'],
                   access_key=os.environ['ACCESS_KEY'],
                   secret_key=os.environ['SECRET_KEY'],
                   secure=False)

class mockTest:

    # Taking inputs for refining the folder structure            
    mockTestNo=args.n
    username =args.u

    def pull(self):
        try:                       
            bucket_name = "exams"        # refer to the current user bucket by her id
            object_name = "course-"+str(self.mockTestNo)+'/uid-'+self.username+'/'      # all the submissions with same name in different bucket names

            file_path = os.path.join(bucket_name, "course-"+str(self.mockTestNo),'uid-'+self.username)

            count=1
            while count<=len(os.listdir('answer_files')):
                minioClient.fget_object(bucket_name, object_name+str(count)+'.json', file_path+str(count)+'.json')
                count+=1
            
        except ResponseError as err:
            print(err)
    
    # EVALUATION METHOD OVERRIDING FOR DIFFERENT TESTS IMPORT THE FILE IN THIS FILE TO USE IT ACCORDINGLY

    def save(self):
        if(self.mockTestNo!=None or self.username!=None):
            score = evaluate(self.mockTestNo, self.username)
            with open("test"+self.mockTestNo+"-"+self.username+".json",'w') as f:
                f.write("Total Score = "+str(score))
        else:
            parser.print_help()

    # Program to read contacts from a file and return a list of name and emails
    # Followed by emailing the results back to the user

    # 3 email functions whose definition starts here

    def get_contacts(self, filename):
        names=[]    # this will contain all the names of users
        emails=[]   # it will contain the corresponding emails of users
        with open(filename, mode='r', encoding='utf-8') as contacts_file:
            for contact in contacts_file:
                names.append(contact.split()[0])
                emails.append(contact.split()[1])
            return names, emails

    def read_template(self, filename):
        with open(filename, mode='r', encoding='utf-8') as template_file:
            template_file_content = template_file.read()
        return Template(template_file_content)  

    def email(self, names, emails, message_template ):

        # set up the SMTP server
        s = smtplib.SMTP(host='smtp.gmail.com', port=587)   # email service provider info goes here
        s.starttls()
        MY_ADDRESS = ''     # Enter your email address
        PASSWORD = ''       # Enter corresponding password
        s.login(MY_ADDRESS, PASSWORD)           # pass email and password of the senders account

        # Sending emails logic starts here

        # For each contact, send the email:
        for name, email1 in zip(names, emails):
            msg = MIMEMultipart()       # create a message
            
            res = open('course-title-result.json', 'r')
            res = json.load(res)
            res1 = ''

            for x in res:
                res1  = res1 + ("%s - %s" %(x, res[x])) + "\n"

            # add in the actual person name to the message template
            message = message_template.substitute(PERSON_NAME=name.title(),RESULT=res1)

            print("email sent")  # to check the format of message being sent

            # setup the parameters of the message
            msg['From']=MY_ADDRESS
            msg['To']=email1
            msg['Subject']="Test Result - "

            # add in the message body
            msg.attach(MIMEText(message, 'plain'))

            # send the message via the server set up earlier.
            s.send_message(msg)
    
            del msg

        # terminate the SMTP connection and close the connection
        s.quit()

obj = mockTest()
obj.pull()
obj.save()
names, emails = obj.get_contacts('contacts.txt')        # read contacts
message_template = obj.read_template('message.txt')     # define a template for body
obj.email(names, emails, message_template)