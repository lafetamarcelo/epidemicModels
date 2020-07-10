import nbformat as nbf
import pandas_gbq
import pandas as pd
from google.oauth2 import service_account
from nbconvert.preprocessors import ExecutePreprocessor
import os

# email 
import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 

from datetime import datetime
import base64

fromaddr = ' '
password = ' '
credential_path = '../update-countries/keys/epidemicapp-62d0d471b86f.json'

email_subject = "Aqui estão os resultados!"
email_body = "Previdições EpidemicModels"
nb_filename = "ResultadosEpidemicModels.ipynb"

project_id = "epidemicapp-280600"

def send_email(nb, toaddr):
  msg = MIMEMultipart()
  msg['From'] = fromaddr
  msg['To'] = toaddr
  msg['Subject'] = email_subject
  body = email_body
  msg.attach(MIMEText(body, 'plain'))
  filename = nb_filename
  p = MIMEBase('application', 'octet-stream')
  p.set_payload( nb )
  encoders.encode_base64(p)
  p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
  msg.attach(p) 
  s = smtplib.SMTP('smtp.gmail.com', 587) 
  s.starttls() 
  s.login(fromaddr, password) 
  text = msg.as_string() 
  s.sendmail(fromaddr, toaddr, text) 

  s.quit()
  return True

def get_data(table_id):

  credentials = service_account.Credentials.from_service_account_file(    
                                  credential_path)
  sql_command = f'SELECT * FROM `users_log.estimation_log_parameters` WHERE table_id = "{table_id}"'
  data = pandas_gbq.read_gbq(sql_command,
                             project_id=project_id)

  return data

def run_notebook(nb):
         
  proc = ExecutePreprocessor(timeout=600, kernel_name='python3')
  proc.allow_errors = True
  proc.preprocess(nb, {'metadata': {'path': '/'}})

  return nb

def edit_notebook(nb,user_data, user_id):

  Ro, D   = user_data['Ro'][0], user_data['D'][0]
  mu, pop = user_data['mu'][0], user_data['pop'][0]

  nb = edit_string(nb, 'Ro' , Ro  )
  nb = edit_string(nb, 'D'  , D   )
  nb = edit_string(nb, 'mu' , mu  )
  nb = edit_string(nb, 'pop', pop )
  nb = edit_string(nb, 'user_id', user_id )

  return nb

def edit_string(nb, search_for, replace_with):

  old = f'@${search_for}$@' 
  nb = nb.replace(old, str(replace_with))

  return nb

def do_main(table_id):
  data = get_data(table_id)
  
  nb = open('./nb_model.ipynb').read()
  nb = edit_notebook(nb, data, table_id)
  toaddr = data['email'][0]
  now = datetime.now()
  try:
    status = send_email(nb, toaddr)
    print(f'Email sent to {toaddr} - {table_id} @ {now}')
  except Exception as e:
    print('ERROR: ',e)
    print(f'Could not send email to {toaddr} - {table_id} @ {now}')

if __name__ == '__main__':
  table_id = 'users_data.sp_teste_20200706213733897154'   # test id
  do_main(table_id)