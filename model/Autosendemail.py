from email import encoders
import os
import traceback
from email.header import Header
from email.mime.text import  MIMEText
from email.mime.base import MIMEBase
from email.utils import parseaddr,formataddr
from email.mime.multipart import  MIMEMultipart
import smtplib

def _format_addr(s):
    name,addr=parseaddr(s)
    return formataddr((Header(name ,'utf-8').encode(),addr))
def send_email(from_addr,password,to_addr_in,filepath_in):
    from_addr=from_addr
    smtp_server='smtp.exmail.qq.com'
    password=password
    to_addr=to_addr_in
    to_addrs=to_addr.join(',')
    msg=MIMEMultipart()
    msg['From']=_format_addr('Alina <%s>' % from_addr)
    msg['To']=",".join(to_addrs)
    msg['Subject']=Header('寻秦集日报','utf-8').encode()
    filepath=filepath_in
    r=os.path.exists(filepath)
    if r is False:
        msg.attach(MIMEText('no file ...','plain','utf-8'))
    else:
        msg.attach(MIMEText('***：/n您好，*****，祝好！','plain','utf-8'))
        pathDir=os.listdir(filepath)
        for allDir in pathDir:
            child=os.path.join(filepath,allDir)
            with open(child,'rb') as f :
                mime=MIMEBase('file','xlsx',filename=allDir)
                mime.add_header('Content-Disposition','attachment',filename=('gbk','',allDir))
                mime.add_header('Content-ID','<0>')
                mime.add_header('X-Attachment-ID','0')
                mime.set_payload(f.read())
                encoders.encode_base64(mime)
                msg.attach(mime)
    try:
        server=smtplib.SMTP_SSL(smtp_server,port=465)
        server.set_debuglevel(1)
        server.login(from_addr,password)
        server.sendmail(from_addr,to_addrs,msg.as_string())
        server.close()
        print("send email successful")
    except Exception:
        print("unable to send email")
        print(traceback.format_exc())
if __name__=='__main__':
    send_email('from_address','password','to_address','filename')


