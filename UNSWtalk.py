#!/web/cs2041/bin/python3.6.3

# written by andrewt@cse.unsw.edu.au October 2017
# as a starting point for COMP[29]041 assignment 2
# https://cgi.cse.unsw.edu.au/~cs2041/assignments/UNSWtalk/

import os
import sqliteOp
from flask import Flask, render_template, session,request, send_from_directory,escape
from flask import Markup
import re
import uuid
import time
students_dir = "dataset-medium";
#students_dir = "dataset-small";
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
def searchPost(keyword):
    post = sqliteOp.Posts(students_dir+'.db')
    posts = post.searchbykey('*',message = keyword)
    return posts
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
def getRecentPost(zid):
    post = sqliteOp.Posts(students_dir+'.db')
    posts = post.select_order_recent('*',zid = zid)
    #print(posts)
    return posts
def getComment(postid):
    comment = sqliteOp.Comments(students_dir+'.db')
    comments = comment.select_order('*',postid = postid)
    return comments
def getReply(commentid):
    reply = sqliteOp.Replies(students_dir+'.db')
    replies = reply.select_order('*',commentid = commentid)
    return replies
def checkLogin(zid,pwd):
    user = sqliteOp.User(students_dir+'.db')
    return user.authenticate(zid,pwd)
def insteadOfZid(msg):
    #print("test instead")
    #stu = getStudent(msg) #[]
    zids = re.findall(r"z[0-9]{7}",msg)#
    #print(zids)
    for z in zids:
        stu = getStudent(z)
        #print(stu)
        if(len(stu)>0):
            msg = msg.replace(z,'''<a href="/students/''' + stu[0][0] + '''" >@''' + stu[0][3] + ''' </a>  ''')
    return msg
def getIncludZid(zid):
	post = sqliteOp.Posts(students_dir+'.db')
	posts = post.select_order_leftjoin("posts.*",message=zid,message1=zid,message2=zid)
	#print(posts)
	return posts
def showPost(name,zid,posts):
    showdiv = ""
    for post in posts:
            #print(post[1])
            msg = insteadOfZid(post[4])
            showdiv = showdiv + '''
<h4 class="posttitle"><a href="/students/''' + zid + '''" >''' + name + ''' </a>make a Post at '''+ post[5]+'''<i> <a class="makecomment" href="/makecomment/'''+ post[1] +'''"> comment</a></i></h4>
<p class="pcontent">''' + msg + '''</p>'''
            comments = getComment(post[1])
            if(len(comments)>0):
                showdiv = showdiv + '''
<div class="div10 wellcomment">'''
            for comment in comments:
                stu = getStudent(comment[2])
                msg = insteadOfZid(comment[3])
                username = stu[0][3]
                if(stu[0][0] == zid):
                    username = name
                showdiv = showdiv + '''
    <p class="pcomment"><strong><a href="/students/'''+ stu[0][0] + '''">'''+ username + ''' </a>comments at ''' + comment[4] + '''</strong><a class="makereply" href="/makereply/'''+ comment[1] +'''">Reply</a></p>
    <p class="pcomment">''' + msg + '''</p>'''
                replies = getReply(comment[1])
                #print(replies)
                for reply in replies:
                    ss = getStudent(reply[2])
                    msg = insteadOfZid(reply[3])
                    rusername = ss[0][3]
                    if(ss[0][0] == zid):
                        rusername = name
                    showdiv = showdiv + '''
    <div class="div10 wellreply">
					<p class="preply"><strong><a href="/students/'''+ ss[0][0] + '''">'''+ rusername + '''</a> reply at ''' + reply[4] + '''</strong></p>
					<p class="preply">''' + msg + '''</p>
    </div>
   
                    '''
            if(len(comments)>0):
                showdiv = showdiv + '''
</div>
<hr>'''
    return showdiv
def showPostNew(posts):
    showdiv = ""
    for post in posts:
            #print(post[1])
            msg = insteadOfZid(post[4])
            sn = getStudent(post[0])
            zid = post[0]
            username = sn[0][3]
            try:
                if(zid == session['zid']):
                    username = "I" 
            except:
                username = sn[0][3]
            showdiv = showdiv + '''
<h4 class="posttitle"><a href="/students/''' + zid + '''" >''' + username + ''' </a>make a Post at '''+ post[5]+'''<i> <a class="makecomment" href="/makecomment/'''+ post[1] +'''"> comment</a></i></h4>
<p class="pcontent">''' + msg + '''</p>'''
            comments = getComment(post[1])
            if(len(comments)>0):
                showdiv = showdiv + '''
<div class="div10 wellcomment">'''
            for comment in comments:
                stu = getStudent(comment[2])
                msg = insteadOfZid(comment[3])
                cusername = stu[0][3]
                try:
                    if(stu[0][0] == session['zid']):
                        cusername = "I"
                except:
                    cusername = stu[0][3]
                showdiv = showdiv + '''
    <p class="pcomment"><strong><a href="/students/'''+ stu[0][0] + '''">'''+ cusername + ''' </a>comments at ''' + comment[4] + '''</strong><a class="makereply" href="/makereply/'''+ comment[1] +'''">Reply</a></p>
    <p class="pcomment">''' + msg + '''</p>'''
                replies = getReply(comment[1])
                #print(replies)
                for reply in replies:
                    ss = getStudent(reply[2])
                    msg = insteadOfZid(reply[3])
                    rusername = ss[0][3]
                    try:
                        if(ss[0][0] == session['zid']):
                            rusername = "I"
                    except:
                        rusername = ss[0][3]
                    showdiv = showdiv + '''
    <div class="div10 wellreply">
					<p class="preply"><strong><a href="/students/'''+ ss[0][0] + '''">'''+ rusername + '''</a> reply at ''' + reply[4] + '''</strong></p>
					<p class="preply">''' + msg + '''</p>
    </div>
                    '''
            if(len(comments)>0):
                showdiv = showdiv + '''
</div>
<hr>'''
    return showdiv
def makepost(zid,message):
    latitude = ''
    longitude = ''
    postid = str(uuid.uuid1())
    createdate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    post = sqliteOp.Posts(students_dir+'.db')
    post.insert(zid,postid,latitude,longitude,message,createdate)
def makecomment(zid,message,postid):
    commentid = str(uuid.uuid1())
    createdate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    comment = sqliteOp.Comments(students_dir+'.db')
    comment.insert(postid,commentid,zid,message,createdate)
def makereply(zid,message,commentid):
    replyid = str(uuid.uuid1())
    createdate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    comment = sqliteOp.Comments(students_dir+'.db')
    reply = sqliteOp.Replies(students_dir+'.db')
    reply.insert(commentid,replyid,zid,message,createdate)
@app.route('/', methods=['GET','POST'])
@app.route('/start', methods=['GET','POST'])
def start():
    n = session.get('n', 0)
    students = sorted(getStudentAll())
    print(n % len(students));
    student_to_show = students[n % len(students)]
    session['n'] = n + 1
    flist = getFriends(student_to_show[0])
    #print(flist)
    student_posts = getPost(student_to_show[0])
    return render_template('start.html', student_details=student_to_show,student_friends = flist,student_posts = student_posts)
@app.route("/images/<zid>")
def get_image(zid):
    #print(students_dir + "/" + zid)
    if os.path.exists(students_dir + "/" + zid + '/img.jpg'):
        return send_from_directory(students_dir + "/" + zid ,"img.jpg")	
    else:
        return send_from_directory("headlogo.jpg")	
        
@app.route('/students/<zid>', methods=['GET'])
def get_one(zid):
    #print(zid)
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
    student_posts = getPost(zid)
    return render_template('start.html', student_details=stu[0],student_friends = flist,student_posts = student_posts)
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
    #print(students)
    flag = 0
    if(len(students) == 0):
        flag = 1
    return render_template('search.html',search_list = students,flag = flag)
@app.route('/loginpage', methods=['GET'])
def show_loginpage():
    return render_template('login.html')
@app.route('/checklogin', methods=['POST'])
def check_login():
    session['zid'] = 0
    zid = request.form['zid']
    password = request.form['password']
    if(checkLogin(zid,password)):
        session['zid'] = zid
        print("zid")
        print(session['zid'])
        stu = getStudent(zid)
        #show personal posts
        recentposts = getRecentPost(zid)
        showdiv = showPost("I",zid,recentposts)
        recentposts = Markup(showdiv);
        #show friend recent post
        flist = getFriends(zid)
        showf = ''
        for friend in flist:
            fposts = getPost(friend[0])
            showfri = showPost(friend[1],friend[0],fposts)
            showf = showf + showfri;
        friposts = Markup(showf);
        includeposts = getIncludZid(zid)
        showinclude = showPostNew(includeposts)
        #print(includeinfo)
        showinclude = Markup(showinclude);
        return render_template('posts.html',username = stu[0][3],recentposts = recentposts,friposts = friposts,showinclude = showinclude)
    else:
        return render_template('loginerror.html')
    #return render_template('login.html')
@app.route('/showmyprofile', methods=['GET'])
def show_my_profile():
    if re.match(r"^z[0-9]{7}$",session['zid']):
        zid = session['zid']
        print("zid")
        print(session['zid'])
        stu = getStudent(zid)
        #show personal posts
        recentposts = getRecentPost(zid)
        showdiv = showPost("I",zid,recentposts)
        recentposts = Markup(showdiv);
        #show friend recent post
        flist = getFriends(zid)
        showf = ''
        for friend in flist:
            fposts = getPost(friend[0])
            showfri = showPost(friend[1],friend[0],fposts)
            showf = showf + showfri;
        friposts = Markup(showf);
        includeposts = getIncludZid(zid)
        showinclude = showPostNew(includeposts)
        #print(includeinfo)
        showinclude = Markup(showinclude);
        return render_template('posts.html',username = stu[0][3],recentposts = recentposts,friposts = friposts,showinclude = showinclude)
    else:
        return render_template('loginerror.html')
    #return render_template('login.html')
@app.route('/makepost', methods=['POST'])
def make_post():
    postcontent = request.form['postcontent']
    #print(session['zid'])
    if re.match(r"^z[0-9]{7}$",session['zid']) :
        zid = session['zid']
        try:
            makepost(zid,postcontent)
            return render_template('makepostsuc.html',tag="post")
        except:
            return render_template('makepostwrong.html',tag="post")
    else:
        return render_template('login.html')
@app.route("/makecomment/<postid>")
def show_comment(postid):
    if re.match(r"^z[0-9]{7}$",session['zid']) :
        return render_template('makecomment.html',postid = postid)
    else:
        return render_template('login.html')
    '''
    latitude = ''
    longitude = ''
    postid = str(uuid.uuid1())
    createdate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    post = sqliteOp.Posts(students_dir+'.db')
    post.insert(zid,postid,latitude,longitude,message,createdate)
    '''
@app.route("/postcomment",methods=['POST'])
def post_comment():
    postid = request.form['postid']
    postcontent = request.form['postcontent'];
    if re.match(r"^z[0-9]{7}$",session['zid']) :
        zid = session['zid'];
        try:
            makecomment(zid,postcontent,postid)
            return render_template('makepostsuc.html',tag="comment")
        except:
            return render_template('makepostwrong.html',tag ="comment")
    else:
        return render_template('login.html')
    '''
    latitude = ''
    longitude = ''
    postid = str(uuid.uuid1())
    createdate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    post = sqliteOp.Posts(students_dir+'.db')
    post.insert(zid,postid,latitude,longitude,message,createdate)
    '''
@app.route("/makereply/<commentid>")
def show_reply(commentid):
    if re.match(r"^z[0-9]{7}$",session['zid']) :
        return render_template('makereply.html',commentid = commentid)
    else:
        return render_template('login.html')
@app.route("/postreply",methods=['POST'])
def post_reply():
    commentid = request.form['commentid']
    postcontent = request.form['postcontent'];
    if re.match(r"^z[0-9]{7}$",session['zid']) :
        zid = session['zid'];
        try:
            makereply(zid,postcontent,commentid)
            return render_template('makepostsuc.html',tag="reply")
        except:
            return render_template('makepostwrong.html',tag ="reply")
    else:
        return render_template('login.html')
@app.route('/logout')
def logout():
    session.pop('zid')
    n = session.get('n', 0)
    students = sorted(getStudentAll())
    print(n % len(students));
    student_to_show = students[n % len(students)]
    session['n'] = n + 1
    flist = getFriends(student_to_show[0])
    #print(flist)
    student_posts = getPost(student_to_show[0])
    return render_template('start.html', student_details=student_to_show,student_friends = flist,student_posts = student_posts)
####search page####
@app.route('/searchpost', methods=['GET'])
def show_searchpost():
    return render_template('searchpost.html',search_list = "",flag = 0)
@app.route('/searchpp', methods=['POST'])
def search_pp():
    content = request.form['searchname']
    posts = searchPost(content)
    showdiv = showPostNew(posts)
    posts = Markup(showdiv);
    flag = 0
    if(len(posts) == 0):
        flag = 1
    return render_template('searchpost.html',search_list = posts,flag = flag)
if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run('0.0.0.0',debug=True)
#### login in 
