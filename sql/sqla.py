# Create a SQLite3 database and table 

# import the sqlite3 library
import sqlite3
import csv
import urllib2

# create a new database if the databasee doesn't already exist
conn = sqlite3.connect("new.db")

# get a cursor object used to execute SQL commands
#cursor = conn.cursor()

# create a table
#cursor.execute("""CREATE TABLE population (city TEXT, state TEXT, population INT)""")

# insert data
#cursor.execute("INSERT INTO population VALUES('New York City', 'NY', 8200000)")
#cursor.execute("INSERT INTO population VALUES('San Francisco', 'CA',800000)")

#conn.commit()

# close the database connection 
#conn.close()
'''
# using the 'with' command make sqlite automatically commit the INSERT comannds without having to hit conn.commit() after 
with sqlite3.connect("new.db") as connection:
	c = connection.cursor()
	
	# insert multiple records using a tuple
	cities = [
		('Boston','MA', 600000),
		('Chicago','IL',2700000),
		('Houston','TX',2100000),
		('Phoenix','AZ',1500000)]

	# insert data into table
	c.executemany('INSERT INTO population VALUES(?,?,?)', cities)

# close the database connection 
c.close()

'''
# using the 'with' command make sqlite automatically commit the INSERT comannds without having to hit conn.commit() after 
with sqlite3.connect("new.db") as connection:
	c = connection.cursor()

	# open the csv file and assign it to a variable
	employees = csv.reader(open("employees.csv","rU"))
	
	# create a table called employeess
	#c.execute("CREATE TABLE employees(firstname TEXT, lastname TEXT)")
	
	# insert data into table 
	c.executemany("INSERT INTO employees(firstname, lastname) values (?, ?)", employees)
	
