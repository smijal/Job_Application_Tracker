import imaplib
import json
import configparser
import psycopg2
from email.utils import parsedate_to_datetime
from tqdm import tqdm
from email import message_from_bytes
from email.header import decode_header
import sys

# Prints straight line of '=' for nicer formating
def printFrame():
    print("="*100)

# Cleans up text by removing \n and \r
def clean(text):
    text = str(text)
    return text.replace('\r','').replace('\n','')

# To decode email subject
def decodeSubject(msg):
    try:
        subject, encoding = decode_header(msg['Subject'])[0]
    except:
        subject = 'NULL'
    if isinstance(subject, bytes):
        # if it's a bytes, decode to str
        try:
            subject = subject.decode(encoding)
        except:
            subject = 'NULL'
            
    return clean(subject)

# To decode email sender
def decodeSender(msg):
    try:
        sender, encoding = decode_header(msg.get('From'))[0]
    except:
        sender = 'NULL'
    if isinstance(sender, bytes):
        # if it's a bytes, decode to str
        try:
            sender = sender.decode(encoding)
        except:
            subject = 'NULL'
            
    return clean(sender)
               
# To decode email body
def decodeBody(msg):
    if msg.is_multipart():
        # iterate over email parts
        for part in msg.walk():
            # extract content type of email
            content_type = part.get_content_type()
            content_disposition = str(part.get('Content-Disposition'))
            try:
                # get the email body
                body = part.get_payload(decode=True).decode()
            except:
                pass
            if content_type == 'text/plain':
                # print text/plain emails and skip attachments
                return clean(body[:1000])
    else:
        # extract content type of email
        content_type = msg.get_content_type()
        # get the email body
        try:
            body = msg.get_payload(decode=True).decode()
        except:
            pass
        if content_type == 'text/plain':
            # print only text email parts
            return clean(body[:1000])
    
    return 'NULL'

    return subject,sender,body

# Finds if the email is job related
def isJobRelated(subject):
    keywords = ['application', 'applying', 'applied', 'talent acquisition', 'interest',
     'update on', 'update from', 'thank you for']
    falsePositives = ['viewed', 'started', 'tips', 'forget', 'track', 'apply now', 'interested', 'account', 'salary']

    if any(match in subject for match in keywords) and not any(match in subject for match in falsePositives):
        return True
    else:
        return False

# Finds application status: Rejected, Awaits decision or NULL
def applicationStatus(subject, body):

    if(body == 'NULL'):
        return 'NULL'
    
    status = 'NULL'

    keywords = ['successfully', 'submitted', 'applied', 'received', 'added', 'started']

    body_keywords = ['will be reviewed', 'will review']

    rejected_keywords = ['unfortunately', 'regret', 'although', 'not', 'not move forward','not a fit', 'other']

    if any(match in subject for match in keywords) or any(match in body for match in body_keywords):
        return 'Awaits decision'
    elif status=='NULL':
        if(body.find('received')!=-1):
            status = 'Awaits decision'
    if any(match in body for match in rejected_keywords):
        status = 'Rejected'
    return status

# Finds the name of the company
def findCompanyName(subject, sentFrom):
    subjectCpy = subject.lower()

    length = len(subjectCpy)

    keywords = [' at ', ' to ', ' in ']

    for word in keywords:
        indx = subjectCpy.find(word)
        if(indx != -1):
            retVal = subjectCpy[indx+4:length]
            retVal = retVal.split(',', 1)[0]
            retVal = clean(retVal)
            return retVal

    keywords = [' from ', ' with ']

    for word in keywords:
        indx = subjectCpy.find(word)
    
        if(indx != -1):
            return subjectCpy[indx+6:length].split(' ',1)[0]

    return 'NULL'

# To insert record into a database
def addInDatabase(email,cur):
    company = email['company']
    subject = email['subject']
    sender = email['sender']
    status = email['status']
    body = email['body']
    timestamp = email['timestamp']
    try:
        cur.execute('INSERT INTO emails (company, subject, sender, status, content, timestamp) VALUES (%s,%s,%s,%s,%s,%s)' ,
        (company, subject, sender, status, body, timestamp))
    except:
        cur.execute('rollback')
        
# To fetch data from database, for debug purposes
def fetchDb(cur):
    cur.execute('SELECT company,status FROM emails')
    print(cur.fetchall())


def main():

    printFrame()
    # Read config.ini file
    config_object = configparser.ConfigParser()
    config_object.read('config.ini')

    # If you use GMAIL check the link bellow on how to obtain your credentials
    # https://coderzcolumn.com/tutorials/python/imaplib-simple-guide-to-manage-mailboxes-using-python

    #email account credentials
    emailInfo = config_object['EMAILINFO']

    username = emailInfo['username']
    password = emailInfo['password']
    # create an IMAP4 class with SSL y
    try:
        imap = imaplib.IMAP4_SSL(emailInfo['imapserver'])
    except:
        print("No internet connection or Imap server URL incorrect, check your config.ini file...")
        exit()

    # Authenticate
    try:
        print("Connecting to the imap server...  ", end='')
        imap.login(username, password)
    except:
        print("\nNo internet connection or Invalid credentials, check your config.ini file...")
        exit()
    print("Connected!")

    databaseInfo = config_object['DATABASEINFO']

    # Connect to your postgres DB
    try:
        print("Connecting to the database...  ", end='')
        conn = psycopg2.connect(user=databaseInfo['user'], host=databaseInfo['host'], database=databaseInfo['database'],password=databaseInfo['password'])
    except:
        print("\nNo internet connection or Invalid credentials. Check your config.ini file...")
        exit()
    print("Connected!")
    # Open a cursor to perform database operations
    cur = conn.cursor()

    status, messages = imap.select('INBOX')
    
    # number of top emails to fetch
    # If the script is invoked with arguments, it will analyze that many emails
    # If not, the default is 100
    if(len(sys.argv)>1 and sys.argv[1].isnumeric()):
        N = int(sys.argv[1])
    elif(len(sys.argv)==3 and sys.argv[2].isnumeric()):
        N = int(sys.argv[2])
    else:
        N = 100

    # total number of emails
    messages = int(messages[0])
    jobRelatedCount = 0
    jobEmailList = []
    companySet = set()
    N = min(messages, N)

    
    for emailNumber in tqdm (range(messages, messages-N, -1), 'Searching for job-related emails...'):

        res, msg = imap.fetch(str(emailNumber), '(RFC822)')
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = message_from_bytes(response[1])   

                subject = decodeSubject(msg)
                subject_lowerCase = subject.lower()

                sender = decodeSender(msg)
                sender_lowerCase = sender.lower()     

                timestamp = parsedate_to_datetime(msg['date'])

                if(isJobRelated(subject)):
                    jobRelatedCount+=1
                    body = decodeBody(msg)
                    company = findCompanyName(subject,sender)
                    status = applicationStatus(subject,body)

                    if(company != 'NULL' and company in companySet):
                        #print('    Job status update from ' + company)
                        continue
                    else:
                        companySet.add(company)

                    dictInstance = {
                        'company' : company,
                        'subject' : subject,
                        'sender'  : sender,
                        'status'  : status,
                        'body'    : body[:1000],
                        'timestamp': timestamp
                    }

                    jobEmailList.append(dictInstance)

    print('\rFound: {} out of {}'.format(jobRelatedCount,N))

    
    for email in jobEmailList:
        addInDatabase(email,cur)

    #fetchDb(cur)

    # If the script is invoked with argument 'y', then it will automatically add to database
    # If not, it will ask for permission
    if( (len(sys.argv)>1 and str(sys.argv[1]) == 'y') or (len(sys.argv)==3 and sys.argv[2] =='y')):
        response = 'y'
    else:
        response = input('\nDo you want to add the records to the database? [y for YES] > ')

    if(response.lower() == 'y'):
        conn.commit()
        print("Successfully added records to the database!")
        print("NOTE: If records already existed in the database, they will be auto-rejected and not overwritten...")

    print("Closing connection...  ",end='')
    # close the connection and logout
    imap.close()
    imap.logout()
    cur.close()
    conn.close()
    print("Closed.")

    printFrame()

if __name__ == "__main__":
    main()