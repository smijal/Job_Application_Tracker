import psycopg2

# Connect to your postgres DB
conn = psycopg2.connect(user="postgres", host="localhost", database="job_applications_database",password="122156")

# Open a cursor to perform database operations
cur = conn.cursor()

# To create table in existing database
def createTable(tableName):

    cur.execute("CREATE TABLE " + tableName +  " (company VARCHAR(50), subject VARCHAR(100), sender VARCHAR(50), status VARCHAR(20), content VARCHAR(1000), timestamp TIMESTAMPTZ, PRIMARY KEY (company,subject));")
    conn.commit()
    cur.close()
    print("Table sucessfully created!")

tableName = input("Enter table name: ")


createTable(tableName)