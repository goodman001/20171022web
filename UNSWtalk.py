#!/web/cs2041/bin/python3.6.3

# written by andrewt@cse.unsw.edu.au October 2017
# as a starting point for COMP[29]041 assignment 2
# https://cgi.cse.unsw.edu.au/~cs2041/assignments/UNSWtalk/

import os
import sqliteOp
from flask import Flask, render_template, session,request, send_from_directory

#students_dir = "dataset-medium";
students_dir = "dataset-small";
app = Flask(__name__)

# Show unformatted details for student "n"
# Increment n and store it in the session cookie
def getStudentAll():
    user = sqliteOp.User(students_dir+'.db')
    cursor = user.select_all('*')
    #print(cursor.fetchall())
    students = cursor.fetchall()
    cursor.close()
    return students
def getStudent(zid):
    user = sqliteOp.User(students_dir+'.db')
    stu = user.select('*',zid = zid)
    #print(stu)
    return stu
def searchStudentByname(name):
    user = sqliteOp.User(students_dir+'.db')
    stu = user.searchbyname('*',full_name = name)
    #print("search user");
    #print(stu)
    return stu
def getFriends(zid):
    friend = sqliteOp.Friend(students_dir+'.db')
    friends = friend.select('twozid',mainzid = zid)
    #friends = cursor.fetch()
    #print(friends)
    flist = []
    for f in friends:
        print(f[0])
        stu = getStudent(f[0])
        flist.append([stu[0][0],stu[0][3]])
    return flist
    #cursor.close()
    #cursor.close()
def getPost(zid):
    post = sqliteOp.Posts(students_dir+'.db')
    posts = post.select_order('*',zid = zid)
    #print(posts)
    return posts
def checkLogin(zid,pwd):
    user = sqliteOp.User(students_dir+'.db')
    return user.authenticate(zid,pwd)
@app.route('/', methods=['GET','POST'])
@app.route('/start', methods=['GET','POST'])
def start():
    n = session.get('n', 0)
    students = sorted(getStudentAll())
    print(n % len(students));
    student_to_show = students[n % len(students)]
    session['n'] = n + 1
    flist = getFriends(student_to_show[0])
    print(flist)
    student_posts = getPost(student_to_show[0])
    return render_template('start.html', student_details=student_to_show,student_friends = flist,student_posts = student_posts)
@app.route("/images/<zid>")
def get_image(zid):
    print(students_dir + "/" + zid)
    return send_from_directory(students_dir + "/" + zid, "img.jpg")	
@app.route('/students/<zid>', methods=['GET'])
def get_one(zid):
    print(zid)
    stu = getStudent(zid)
    n = session.get('n', 0)
    students = sorted(getStudentAll())
    index = 0;
    for cell in students:
        if cell[0] == zid:
            n = index
            break
        index = index + 1
    session['n'] = n + 1
    flist = getFriends(zid)
    return render_template('start.html', student_details=stu[0],student_friends = flist)
    '''
    n = session.get('n', 0)
    students = sorted(getStudentAll())
    print(n % len(students));
    student_to_show = students[n % len(students)]
    session['n'] = n + 1
    flist = getFriends(student_to_show[0])
    print(flist)
    return render_template('start.html', student_details=student_to_show,student_friends = flist)
    '''
####search page####
@app.route('/searchpage', methods=['GET'])
def show_searchpage():
    return render_template('search.html',search_list = [],flag = 0)
@app.route('/searchname', methods=['POST'])
def search_name():
    content = request.form['searchname']
    students = searchStudentByname(content)
    print(students)
    flag = 0
    if(len(students) == 0):
        flag = 1
    return render_template('search.html',search_list = students,flag = flag)
@app.route('/loginpage', methods=['GET'])
def show_loginpage():
    return render_template('login.html')
@app.route('/checklogin', methods=['POST'])
def check_login():
    zid = request.form['zid']
    password = request.form['password']
    if(checkLogin(zid,password)):
        session['zid'] = zid
        return render_template('posts.html')
    else:
        return render_template('loginerror.html')
    #return render_template('login.html')
if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run('0.0.0.0',debug=True)
#### login in 
