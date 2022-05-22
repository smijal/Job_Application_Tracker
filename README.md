# Job Application Status Tracker

### Description

The purpose of this script is to automatically retrieve data from email and recognize job-related emails. Once those emails are found, it exctracts data from them and stores the following data in a local Postgres SQL database: Company name, Email Subject, Email Sender Address, Job Application Status, Email Content and Timestamp.
This allows easy and automatic tracking of job applications.

### Getting Started

1. Clone the repository with: ``` git clone https://github.com/smijal/Job_Application_Tracker.git ```
2. Install requirements with: ``` pip install -r requirements.txt ```
3. Install PostgreSQL and pgAdmin - [Windows](https://www.youtube.com/watch?v=e1MwsT5FJRQ), [Ubuntu](https://www.youtube.com/watch?v=lX9uMCSqqko), [MacOS](https://www.youtube.com/watch?v=1aybOgni7lI)
   - Check the [link](https://www.postgresqltutorial.com/postgresql-getting-started/) on how to get started with PostgreSQL and how to create a database.
4. Modify the config.ini file: 
- ![image](https://github.com/smijal/Job_Application_Tracker/blob/main/Images/configFIle.JPG)
- If you use GMAIL check the [link](https://coderzcolumn.com/tutorials/python/imaplib-simple-guide-to-manage-mailboxes-using-python) on how to obtain your credentials.
5. Run createTable.py: ``` python createTable.py ``` or ``` python3 createTable.py ```. When promted: "Enter table name: " , type: emails. If you use a different table name you will need to change the SQL queries in job_tracker.py to match the table name.
6. Run job_tracker.py
   - If you run with arguments ex. ``` python createTable.py 200 y ``` -> it will process the newest 200 emails and save the records into the database.
   - If you run with arguments ex. ``` python createTable.py 1000 n ``` -> it will process the newest 1000 emails and NOT save the records to the database.
   - If you run with no arguments ex. ``` python createTable.py ``` -> you will be prompted to input if you want to save or not save to the database. Newest 100 emails will be processed.

### Tips

1. Add the script to your OS task-scheduler and and execute it once a week to keep track of your job applications.
2. Sometimes the email body cannot be decoded. Search for that specific email manually and add update the database manually.
3. Modify the script for your own goals. Modify job_tracker.py to save records in a text file instead of a database.

### Outputs
![image](https://github.com/smijal/Job_Application_Tracker/blob/main/Images/console_argv.JPG)
![image](https://github.com/smijal/Job_Application_Tracker/blob/main/Images/database_screenshot.JPG)
![image](https://github.com/smijal/Job_Application_Tracker/blob/main/Images/ghosted.JPG)



