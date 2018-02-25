import traceback

from utility.pattern import *
import sqlite3
import requests
import os


def other_info_retriever(db_name: str):
    path = os.path.dirname(os.path.abspath(__file__))
    db_conn = sqlite3.connect(path + '/' + db_name)
    db_cur = db_conn.cursor()
    db_cur.execute('''SELECT Account, RawURL FROM AccountWallet''')
    account_email_dict = {}  # type: Dict[int, str]
    account_website_dict = {}  # type: Dict[int, str]
    for row in db_cur:
        try:
            resp_text = None
            if row[1] is not None:
                try:
                    response = requests.get(row[1])
                    resp_text = response.text
                except Exception:
                    traceback.print_exc()
            if resp_text is not None:
                email_list = match_email(resp_text)
                website_list = match_personal_website(resp_text)
                email_list = list(set([email.lower() for email in email_list
                                       if len(email.strip()) > 0]))
                website_list = list(set([website for website in website_list
                                         if len(website.strip()) > 0]))
                emails = ''
                if len(email_list) == 1:
                    emails = email_list[0]
                elif 1 < len(email_list) < 6:
                    emails = ','.join(email_list)
                websites = ''
                if len(website_list) == 1:
                    websites = website_list[0]
                elif 1 < len(website_list) < 9:
                    websites = ','.join(website_list)
                print(str(row[0]) + ' emails:' + str(len(email_list)) +
                      ' websites:' + str(len(website_list)))
                account_email_dict[row[0]] = emails
                account_website_dict[row[0]] = websites
        except:
            traceback.print_exc()
    db_cur.execute('''PRAGMA foreign_keys = OFF''')
    for id_acc in account_email_dict:
        db_cur.execute('''SELECT Info FROM Account WHERE _id = ?''', (id_acc,))
        info = db_cur.fetchone()[0]
        if isinstance(info, int):
            db_cur.execute('''SELECT * FROM Information WHERE _id = ?''',
                           (info,))
            row = db_cur.fetchone()
            if len((row[2]).strip()) > 0:
                new_website_list = account_website_dict[id_acc].split(',')
                new_website_list = [web for web in new_website_list
                                    if len(web.strip()) > 0]
                old_website_list = row[2].split(',')
                old_website_list = [web for web in old_website_list
                                    if len(web.strip()) > 0]
                website_list = list(set(old_website_list + new_website_list))
                websites = ','.join(website_list)
            else:
                websites = account_website_dict[id_acc]
            if len((row[3]).strip()) > 0:
                new_email_list = account_email_dict[id_acc].split(',')
                new_email_list = [email for email in new_email_list
                                  if len(email.strip()) > 0]
                old_email_list = row[3].split(',')
                old_email_list = [email for email in old_email_list
                                  if len(email.strip()) > 0]
                email_list = list(set(old_email_list + new_email_list))
                emails = ','.join(email_list)
            else:
                emails = account_email_dict[id_acc]
            db_cur.execute('''UPDATE Information
                              SET Website = ?, Email = ?
                              WHERE _id = ?''', (websites, emails, info,))
        else:
            emails = account_email_dict[id_acc]
            websites = account_website_dict[id_acc]
            db_cur.execute('''INSERT INTO 
                              Information(Name, Website, Email, Json)
                              VALUES (?,?,?,?)''',
                           (' ', websites, emails, ' ',))
            db_cur.execute('SELECT max(_id) FROM Information')
            max_id = db_cur.fetchone()[0]
            db_cur.execute('''UPDATE Account
                              SET Info = ?
                              WHERE _id = ?''', (max_id, id_acc))
    db_conn.commit()
    db_conn.close()
