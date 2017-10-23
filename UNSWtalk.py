#!/web/cs2041/bin/python3.6.3

# written by andrewt@cse.unsw.edu.au October 2017
# as a starting point for COMP[29]041 assignment 2
# https://cgi.cse.unsw.edu.au/~cs2041/assignments/UNSWtalk/

import os
import sqliteOp
from flask import Flask, render_template, session

#students_dir = "dataset-medium";
students_dir = "dataset-small";
app = Flask(__name__)

# Show unformatted details for student "n"
# Increment n and store it in the session cookie
def getStudent():
    user = sqliteOp.User(students_dir+'.db')
    cursor = user.select_all('*')
    #print(cursor.fetchall())
    students = cursor.fetchall()
    cursor.close()
    return students
@app.route('/', methods=['GET','POST'])
@app.route('/start', methods=['GET','POST'])
def start():
    n = session.get('n', 0)
    students = sorted(getStudent())
    print(n % len(students));
    student_to_show = students[n % len(students)]
    session['n'] = n + 1
    return render_template('start.html', student_details=student_to_show)
@app.route('/img/profile', methods=['GET']):
	
if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run('0.0.0.0',debug=True)
