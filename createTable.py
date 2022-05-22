import psycopg2
import configparser

# Read config.ini file
config_object = configparser.ConfigParser()
config_object.read('config.ini')

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

# To create table in existing database
def createTable(tableName):

    cur.execute("CREATE TABLE " + tableName +  " (company VARCHAR(50), subject VARCHAR(100), sender VARCHAR(50), status VARCHAR(20), content VARCHAR(1000), timestamp TIMESTAMPTZ, PRIMARY KEY (company,subject));")
    conn.commit()
    cur.close()
    print("Table {} sucessfully created!".format(tableName))

tableName = input("Enter table name: ")


createTable(tableName)