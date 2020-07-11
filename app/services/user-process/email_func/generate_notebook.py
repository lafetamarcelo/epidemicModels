
from google.oauth2 import service_account
from nbconvert.preprocessors import ExecutePreprocessor

import os
import base64
import nbformat as nbf
import pandas_gbq
import pandas as pd

# email 
import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 
from string import Template
from datetime import datetime

DEBUG = True

fromaddr = 'epidemicmodels.covid@gmail.com'
password = 'tgpasdlxgugvvopc'

if DEBUG:
  credential_path = '../keys/epidemicapp-62d0d471b86f.json'
else:
  credential_path = './keys/epidemicapp-62d0d471b86f.json'

email_subject = "Aqui estão os resultados!"
email_body  = "Predições EpidemicModels"
nb_filename = "ResultadosEpidemicModels.ipynb"

project_id = "epidemicapp-280600"

RUN_NOTEBOOK = False



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

  credentials = service_account.Credentials.from_service_account_file(credential_path)
  sql_command = f'SELECT * FROM `users_log.estimation_log_parameters` WHERE table_id = "{table_id}"'
  data = pandas_gbq.read_gbq(sql_command,project_id=project_id,  credentials=credentials )

  return data

def edit_notebook(nb,user_data, user_id):

  Ro, D   = user_data['Ro'][0], user_data['D'][0]
  mu, pop = user_data['mu'][0], user_data['pop'][0]
  r = 1 / D
  beta = Ro * r / pop
  
  nb = edit_string(nb, 'Ro'     , Ro,   True)
  nb = edit_string(nb, 'D'      , D ,   True)
  nb = edit_string(nb, 'mu'     , mu,   True)
  nb = edit_string(nb, 'pop'    , pop,  True)
  nb = edit_string(nb, 'beta'   , beta, True)
  nb = edit_string(nb, 'r'      , r,    True)
  nb = edit_string(nb, 'user_id', user_id, False)

  return nb

def edit_string(nb, search_for, replace_with, format_num):

  old = f'@${search_for}$@'
  if format_num:
    replace_with = formatted = '{0:.5g}'.format(replace_with)
  else:
    replace_with = str(replace_with)

  nb = nb.replace(old, str(replace_with))

  return nb

def do_main(table_id, send_email=True):
  data = get_data(table_id)
  ltable_id = table_id.split('.', 1)
  user_id = ltable_id[-1]
  
  if DEBUG:
    nb = open("./nb_model.ipynb").read()
  else:
    nb = open('./email_func/nb_model.ipynb').read()
  
  nb = edit_notebook(nb, data, user_id)
  toaddr = data['email'][0]
  
  if send_email:
    status = send_email(nb, toaddr)
  else:
    with open('./test_notebook.ipynb', 'w', encoding='utf-8') as f:
      nbf.write(nbf.reads(nb, as_version=4), f)
  

if __name__ == '__main__':
  table_id = 'users_data.sp_teste_20200706213733897154'   # test id
  do_main(table_id, send_email=False)