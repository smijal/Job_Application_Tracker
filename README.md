# Job Application Status Tracker

### Description

The purpose of this script is to automatically retrieve data from email and recognize job-related emails. Once those emails are found, it exctracts data from them and stores the following data in a local Postgres SQL database: Company name, Email Subject, Email Sender Address, Job Application Status, Email Content and Timestamp.
This allows easy and automatic tracking of job applications.

### **Getting Started**

1. Clone the repository with: ``` git clone https://github.com/smijal/Job_Application_Tracker.git ```
2. Install requirements with: ``` pip install -r requirements.txt ```
3. Change the config.ini file: 
   - ![image]  (Images\configFIle.JPG)

