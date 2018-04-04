#!/usr/bin/python
# -*- coding: UTF-8 -*-
import smtplib
import sys
import email.mime.multipart
import email.mime.text
import pymysql
import datetime
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.mime.application import MIMEApplication
senders_desc={'robot@weicheche.cn': '数据监控小能手'}

def send_email(smtpHost, sendAddr, password, reci_addrs, subject='', content='', filepaths=None):
    msg = email.mime.multipart.MIMEMultipart()
    msg['from'] = "%s<%s>" %(senders_desc[sendAddr], sendAddr)
    msg['to'] = ';'.join(reci_addrs)
    msg['subject'] = subject
    content = content
    txt = email.mime.text.MIMEText(content, 'plain', 'utf-8')
    msg.attach(txt)

    # 添加附件，传送C:/Users/Administrator/Desktop/linux笔记.txt文件
    def msg_add_file(msg,filepath):
        filename = filepath.split('/')[-1]
        part = email.mime.application.MIMEApplication(open(filepath, 'rb').read())
        part.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(part)

    if filepaths and type(filepaths) is str:
        msg_add_file(msg, filepaths)
    elif filepaths and type(filepaths) is list:
        for filepath in filepaths:
            msg_add_file(msg, filepath)

    smtp = smtplib.SMTP()
    smtp.connect(smtpHost, '25')
    smtp.login(sendAddr, password)
    smtp.sendmail(sendAddr, reci_addrs, str(msg))
    print("发送成功！")
    smtp.quit()


def send_email_exqq(reci_addrs, subject='', content='', filepaths=None):
    if reci_addrs:
        return send_email('smtp.exmail.qq.com', 'robot@weicheche.cn', 'Chechewei123',reci_addrs, subject, content, filepaths)
    else:
        print('你需要添加收信人reci_addrs')
        return 0

if __name__ == '__main__':
    print('hello',sys.argv)
    if len(sys.argv) > 2 and sys.argv[1] == 'exqq':
        args = ['smtp.exmail.qq.com', 'robot@weicheche.cn', 'Chechewei123'] + sys.argv[2:]
        send_email(*args)