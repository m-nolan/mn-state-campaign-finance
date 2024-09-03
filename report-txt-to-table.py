import os
import pandas as pd
import re

from glob import glob

def get_report_txt_files(report_dir = './report_pdf'):
    return glob(os.path.join(report_dir,'*.txt'))

def parse_report_txt(report_txt_file):
    file_year, _, period, _, regnum, file_datestr, file_timestr = tuple(os.path.basename(report_txt_file).split('.')[0].split('_'))
    report_text = open(report_txt_file,'r').read()
    grab_pattern = lambda p: re.search(p,report_text).groups()
    committee= grab_pattern('Committee: (.+)')[0]
    treasurer = grab_pattern('Treasurer: (.+)')[0]
    period = grab_pattern('Period: (.+)')[0]
    submitted = grab_pattern('Submission [D,d]ate: (.+)')[0]
    received_s = re.search('Received by the Board (.+)',report_text)
    received = received_s.group(1) if received_s else ''
    name_s = re.search('Name: (.+)\n',report_text)
    name = name_s.group(1) if name_s else ''
    donor_regnum_s = re.search('\(Registered Id: (\d+).*\)',name) # e.g. (Registered Id: 20045), or (20045)
    donor_regnum = donor_regnum_s.group(1) if donor_regnum_s else ''
    unregistered_s = re.search('Unregistered: (.+)',report_text)
    unregistered = unregistered_s.group(1) if unregistered_s else ''
    employer_s = re.search('Employer: (.+)',report_text) # Employer not there sometimes
    employer = employer_s.group(1) if employer_s else ''
    street = grab_pattern('Address: (.+)')[0]
    city = grab_pattern('.*City: (.+)')[0].split(' State:')[0]
    state = grab_pattern('.*State: (\w+)')[0]
    zip = grab_pattern('.*Zip [C,c]ode: (.+)[\w.+,\n]')[0]
    date = grab_pattern('.*Date: ([\d,/]+)')[0]
    amount = grab_pattern('.*Amount: (.+)[\w.+,\n]')[0]
    inkind = grab_pattern('.*Inkind: (\w+)')[0]
    description = grab_pattern('.*Description:(.*)\n')[0].strip()   # description may be empty
    loan = grab_pattern('Loan: (.+)')[0]
    return pd.DataFrame(
            {
                'fileyear': file_year,
                'filedate': file_datestr,
                'filetime': file_timestr,
                'committee': committee,
                'regnum': int(regnum),
                'treasurer': treasurer,
                'period': period,
                'submitted': submitted,
                'received': received,
                'name': name,
                'unregistered': unregistered,
                'donor_regnum': donor_regnum,
                'employer': employer,
                'street': street,
                'city': city,
                'state': state,
                'zip': zip,
                'date': date,
                'amount': float(amount.replace(',','').replace('$','')),
                'inkind': inkind,
                'description': description,
                'loan': loan
            },
            index=[0]
        )

def main():
    report_txt_files = get_report_txt_files()
    report_df = pd.DataFrame()
    for report_txt_file in report_txt_files:
        print(report_txt_file)
        report_df = pd.concat([report_df,parse_report_txt(report_txt_file)],ignore_index=True)
    print(report_df)
    report_df.to_csv('./daily-large-reports.csv')

if __name__ == "__main__":
    main()