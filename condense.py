import os
import sys
import pandas as pd
import numpy as np
import pyarrow
#import re
from email.parser import Parser
#import time
from datetime import datetime

path = sys.argv[1]


# email address normalize func
def user(addr):
    if '@enron.com' not in addr:
        return None
    addr = addr[0:addr.index('@')]
    if '<' in addr or '#' in addr or "/o" in addr:
        return None
    if "'" in addr:
        addr = addr.replace("'", "")
    if len(addr) > 0 and addr[0] == '.':
        addr = addr[1:]
    if len(addr) == 0:
        return None
    return addr


def enrondf(path):
    # timer start
    #start = time.time()

    filename = []
    Date = []
    From = []
    To = []
    Date = []
    Subject = []
    MailID = []
    Recipients = []

    mailid = 0
    for root, dircs, files in sorted(os.walk(path)):
        for name in sorted(files):
            if name == ".DS_Store":
                continue
            # create fullpath
            fullpath = os.path.join(root, name)

            # filter To
            with open(fullpath, encoding='latin1') as f:
                content = f.read()
                email = Parser().parsestr(content, headersonly=True)
                #email = Parser().parse(content,headersonly=True)

                # try out user function
                if email['To'] and email['From']:
                    normal_receiver = list(
                        filter(None, [user(i.strip()) for i in email["To"].split(',')]))
                    normal_sender = user(email["From"])

                    if normal_receiver and normal_sender:
                        mailid += 1
                        for i in normal_receiver:
                            To.append(i)
                            From.append(normal_sender)
                            filename.append(fullpath.split('maildir/')[1])

                            # replace invalid dates
                            date = email["Date"].split(":")[0][:-3].split(", ")[1]
                            if date.split(' ')[2] == '0001':
                                date = date.replace('0001', '2001')
                            elif date.split(' ')[2] == '0002':
                                date = date.replace('0002', '2002')
                            # append date
                            Date.append(date)

                            # subjects
                            Subject.append(content.split("Subject: ")[1].split("\n")[0])
                            # Subject.append(email["Subject"].split("\n")[0])
                            # print(email["Subject"].split("\n")[0],"\n++++++++++")

                            # append mail ids
                            MailID.append(mailid)
                            # append number of Recipients
                            Recipients.append(len(normal_receiver))

    Subject[0] += ' '
    Subject[3] += '  '
    Subject[6] += '   '
    Subject[7] += '    '

    df_dict = {'MailID': MailID,
               'Date': Date,
               'From': From,
               'To': To,
               'Recipients': Recipients,
               'Subject': Subject,
               'filename': filename}

    enrondf = pd.DataFrame.from_dict(df_dict)

    # change dtype to datetime
    enrondf['Date'] = pd.to_datetime(enrondf['Date'], format="%d %b %Y",
                                     errors='coerce').dt.strftime("%Y-%m-%d")

    # timer done
    #done = time.time()
    # duration
    # print((done-start)/60)

    return enrondf  # , Subject


# function call
df = enrondf(path)
# save df
df.to_feather('./enron.feather')
