import nbformat as nbf
import pandas_gbq
import pandas as pd
from google.oauth2 import service_account
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter, PDFExporter
from IPython.display import Javascript
import os

# email 
import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 

from datetime import datetime
import base64

fromaddr = 'epidemicmodels.covid@gmail.com'
password = ''
credential_path = '../update-countries/keys/epidemicapp-62d0d471b86f.json'

email_subject = 'Aqui estão os resultados!'
email_body = open('html_mail.html', 'r', encoding='utf-8').read()
filename = 'ResultadosEpidemicModels'

project_id = "epidemicapp-280600"

RUN_NOTEBOOK = True

def send_email(payload, toaddr):
  msg = MIMEMultipart()
  msg['From'] = fromaddr
  msg['To'] = toaddr
  msg['Subject'] = email_subject
  msg.attach(MIMEText(email_body, 'html'))
  msg.attach(payload) 
  s = smtplib.SMTP('smtp.gmail.com', 587) 
  s.starttls() 
  s.login(fromaddr, password) 
  text = msg.as_string() 
  s.sendmail(fromaddr, toaddr, text) 

  s.quit()
  return True

def create_MIMEpayload( file_str, file_type, nb_filename):
  if file_type =='pdf':
      p = MIMEApplication(file_str , _subtype="pdf")
      p.add_header('Content-Disposition','attachment',filename= nb_filename)
  else:
    p = MIMEBase('application', 'octet-stream')
    p.set_payload( file_str.encode('utf-8') )
    encoders.encode_quopri(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % nb_filename)
  return p 

def get_data(table_id):

  credentials = service_account.Credentials.from_service_account_file(    
                                  credential_path)
  sql_command = f'SELECT * FROM `users_log.estimation_log_parameters` WHERE table_id = "{table_id}"'
  data = pandas_gbq.read_gbq(sql_command,
                             project_id=project_id,  credentials=credentials )

  return data

def run_notebook(nb):

  nb = nbf.reads(nb, as_version = 4)
         
  proc = ExecutePreprocessor(timeout=600, kernel_name='python3')
  proc.allow_errors = True
  proc.preprocess(nb) # , {'metadata': {'path': '/'}}
  with open('original.ipynb', 'w') as f:
    nbf.write(nb, f)

  nb = nbf.writes(nb)

  return nb

def edit_notebook(nb,user_data, user_id):

  Ro, D   = user_data['Ro'][0], user_data['D'][0]
  mu, pop = user_data['mu'][0], user_data['pop'][0]
  r = 1 / D
  beta = Ro * r / pop

  nb = edit_string(nb, 'Ro'     , Ro,  True)
  nb = edit_string(nb, 'D'      , D ,  True)
  nb = edit_string(nb, 'mu'     , mu,  True)
  nb = edit_string(nb, 'pop'    , pop, True)
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

def output_HTML(nb):
  output_notebook = nbf.reads(nb, as_version = 4)
  exporter = HTMLExporter()
  exporter.template_file = 'hidecode.tpl'
  return exporter.from_notebook_node(output_notebook)

def create_pdf(nb):
  output_notebook = nbf.reads(nb, as_version = 4)
  output_notebook.metadata['title'] = 'Epidemic Models Report'
  pdf_exporter = PDFExporter()
  pdf_exporter.template_file = 'hidecode_pdf.tpl'
  return pdf_exporter.from_notebook_node(output_notebook)

def do_main(table_id, file_type , debug = False):
  if debug:
    save_file = True
    data = get_data(table_id)
    toaddr = 'vparro@ieee.org'

  else:
    data = get_data(table_id)
    toaddr = data['email'][0]
   
  ltable_id = table_id.split('.', 1)
  user_id = ltable_id[-1]
  

  template_notebook = file_type + '_model.ipynb' 
  nb = open(template_notebook).read()
  nb = edit_notebook(nb, data, user_id)

  if file_type == 'html':
    nb = run_notebook(nb)
    str_file, _ = output_HTML(nb)

  elif file_type == 'pdf':
    nb = run_notebook(nb)
    str_file, _ = create_pdf(nb)

  elif file_type == 'ipynb':
    str_file = nb

  output_file = filename + '.' + file_type
  payload = create_MIMEpayload(str_file, file_type, output_file)

  if save_file:
    if file_type == 'pdf':
      with open(output_file, 'wb') as f:
        f.write(str_file)
    else:
      with open(output_file, 'w') as f:
        f.write(str_file)


  now = datetime.now()
  try:
    status = send_email(payload, toaddr, )
    print(f'Email sent to {toaddr} - {table_id} @ {now}')
  except Exception as e:
     print('ERROR: ',e)
     print(f'Could not send email to {toaddr} - {table_id} @ {now}')

if __name__ == '__main__':
  table_id = 'users_data.sp_teste_20200706213733897154'   # test id
  do_main(table_id, 'pdf', debug = True)