#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import sqlite3
import os, sys
import re
import uuid
queries = {
    'SELECT': 'SELECT %s FROM %s WHERE %s',
    'SELECT_ALL': 'SELECT %s FROM %s',
    'INSERT': 'INSERT INTO %s VALUES(%s)',
    'UPDATE': 'UPDATE %s SET %s WHERE %s',
    'DELETE': 'DELETE FROM %s where %s',
    'DELETE_ALL': 'DELETE FROM %s',
    'CREATE_TABLE': 'CREATE TABLE IF NOT EXISTS %s(%s)',
    'DROP_TABLE': 'DROP TABLE %s'}


class DatabaseObject(object):

    def __init__(self, data_file):
        self.db = sqlite3.connect(data_file, check_same_thread=False)
        self.data_file = data_file

    def free(self, cursor):
        cursor.close()

    def write(self, query, values=None):
        cursor = self.db.cursor()
        if values is not None:
            cursor.execute(query, list(values))
        else:
            cursor.execute(query)
        self.db.commit()
        return cursor

    def read(self, query, values=None):
        cursor = self.db.cursor()
        if values is not None:
            cursor.execute(query, list(values))
        else:
            cursor.execute(query)
        return cursor

    def select(self, tables, *args, **kwargs):
        vals = ','.join([l for l in args])
        locs = ','.join(tables)
        conds = ' and '.join(['%s=?' % k for k in kwargs])
        subs = [kwargs[k] for k in kwargs]
        query = queries['SELECT'] % (vals, locs, conds)
        return self.read(query, subs)

    def select_all(self, tables, *args):
        vals = ','.join([l for l in args])
        locs = ','.join(tables)
        query = queries['SELECT_ALL'] % (vals, locs)
        return self.read(query)
    
    def insert(self, table_name, *args):
        values = ','.join(['?' for l in args])
        query = queries['INSERT'] % (table_name, values)
        return self.write(query, args)

    def update(self, table_name, set_args, **kwargs):
        updates = ','.join(['%s=?' % k for k in set_args])
        conds = ' and '.join(['%s=?' % k for k in kwargs])
        vals = [set_args[k] for k in set_args]
        subs = [kwargs[k] for k in kwargs]
        query = queries['UPDATE'] % (table_name, updates, conds)
        return self.write(query, vals + subs)

    def delete(self, table_name, **kwargs):
        conds = ' and '.join(['%s=?' % k for k in kwargs])
        subs = [kwargs[k] for k in kwargs]
        query = queries['DELETE'] % (table_name, conds)
        return self.write(query, subs)

    def delete_all(self, table_name):
        query = queries['DELETE_ALL'] % table_name
        return self.write(query)

    def create_table(self, table_name, values):
        query = queries['CREATE_TABLE'] % (table_name, ','.join(values))
        self.free(self.write(query))

    def drop_table(self, table_name):
        query = queries['DROP_TABLE'] % table_name
        self.free(self.write(query))

    def disconnect(self):
        self.db.close()


class Table(DatabaseObject):

    def __init__(self, data_file, table_name, values):
        super(Table, self).__init__(data_file)
        self.create_table(table_name, values)
        self.table_name = table_name

    def select(self, *args, **kwargs):
        return super(Table, self).select([self.table_name], *args, **kwargs)

    def select_all(self, *args):
        return super(Table, self).select_all([self.table_name], *args)

    def insert(self, *args):
        return super(Table, self).insert(self.table_name, *args)

    def update(self, set_args, **kwargs):
        return super(Table, self).update(self.table_name, set_args, **kwargs)

    def delete(self, **kwargs):
        return super(Table, self).delete(self.table_name, **kwargs)

    def delete_all(self):
        return super(Table, self).delete_all(self.table_name)

    def drop(self):
        return super(Table, self).drop_table(self.table_name)


class User(Table):

    def __init__(self, data_file):
        super(User, self).__init__(data_file, 'users',
                                   ['zid TEXT PRIMARY KEY NOT NULL', 'password TEXT','email TEXT','full_name TEXT','birthday DATE','img BOOLEAN','courses TEXT','home_suburb TEXT' , 'home_latitude NUMERIC', 'home_longitude NUMERIC','program TEXT' ])

    def select(self, *args, **kwargs):
        cursor = super(User, self).select(*args, **kwargs)
        results = cursor.fetchall()
        cursor.close()
        return results

    def insert(self, *args):
        self.free(super(User, self).insert(*args))

    def update(self, set_args, **kwargs):
        self.free(super(User, self).update(set_args, **kwargs))

    def delete(self, **kwargs):
        self.free(super(User, self).delete(**kwargs))

    def delete_all(self):
        self.free(super(User, self).delete_all())

    def drop(self):
        self.free(super(User, self).drop())

    def exists(self, username):
        results = self.select('username', username=username)
        return len(results) > 0

    def authenticate(self, username, password):
        results = self.select('username', username=username,
                              password=password)
        return len(results) > 0
class Friend(Table):

    def __init__(self, data_file):
        super(Friend, self).__init__(data_file, 'friend',
                                   ['mainzid TEXT', 'twozid TEXT'])
    def insert(self, *args):
        self.free(super(Friend, self).insert(*args))
class Posts(Table):

    def __init__(self, data_file):
        super(Posts, self).__init__(data_file, 'posts',
                                   ['zid TEXT', 'postid TEXT','latitude NUMERIC','longitude NUMERIC','message TEXT','createdate DATETIME'])
    def insert(self, *args):
        self.free(super(Posts, self).insert(*args))
class Comments(Table):

    def __init__(self, data_file):
        super(Comments, self).__init__(data_file, 'comments',
                                   ['postid TEXT', 'commentid TEXT','zid','message TEXT','createdate DATETIME'])
    def insert(self, *args):
        self.free(super(Comments, self).insert(*args))    
class Replies(Table):

    def __init__(self, data_file):
        super(Replies, self).__init__(data_file, 'replies',
                                   ['commentid TEXT', 'replyid TEXT','zid','message TEXT','createdate DATETIME'])
    def insert(self, *args):
        self.free(super(Replies, self).insert(*args))  
def readUserprofile(userobj,friobj,fn,imgflag):
	print("[**]" + fn)
	zid = ''
	password = ''
	email = ''
	full_name = ''
	birthday = ''
	img = 0
	courses = ''
	home_suburb = ''
	home_latitude = 0
	home_longitude = 0
	program = ''
	friend = ''
	file = open(fn)
	while 1:
		line = file.readline()
		if not line:
			break
		#print(line)
		line = re.sub(r'\s$', "", line)
		if(re.match('^[ ]*zid:',line)):
			tmp = re.split(':[ ]*',line)
			zid = tmp[1]
		elif(re.match('^[ ]*password:',line)):
			tmp = re.split(':[ ]*',line)
			password = tmp[1]
		elif(re.match('^[ ]*email:',line)):
			tmp = re.split(':[ ]*',line)
			email = tmp[1]
		elif(re.match('^[ ]*full_name:',line)):
			tmp = re.split(':[ ]*',line)
			full_name = tmp[1]
		elif(re.match('^[ ]*birthday:',line)):
			tmp = re.split(':[ ]*',line)
			birthday = tmp[1]
		elif(re.match('^[ ]*courses:',line)):
			tmp = re.split(':[ ]*',line)
			#courses = tmp[1]
			courses = re.sub(r'[\(\)\s]+', "", tmp[1])
		elif(re.match('^[ ]*home_suburb:',line)):
			tmp = re.split(':[ ]*',line)
			home_suburb = tmp[1]
		elif(re.match('^[ ]*home_latitude:',line)):
			tmp = re.split(':[ ]*',line)
			home_latitude = tmp[1]
		elif(re.match('^[ ]*home_longitude:',line)):
			tmp = re.split(':[ ]*',line)
			home_longitude = tmp[1]
		elif(re.match('^[ ]*program:',line)):
			tmp = re.split(':[ ]*',line)
			program = tmp[1]
		elif(re.match('^[ ]*friends:',line)):
			tmp = re.split(':[ ]*',line)
			friend = tmp[1]
			
	'''
	print("zid:" + zid)
	print("password:" + password)
	print("email:" + email)
	print("full_name:" + full_name)
	print("birthday:" + birthday)
	print("courses:" + courses)
	print("home_suburb:" + home_suburb)
	print("home_latitude:" + home_latitude)
	print("home_longitude:" + home_longitude)
	print("program:" + program)
	print("friend:" + friend)
	'''
	try:
		userobj.insert(zid,password,email,full_name,birthday,imgflag,courses,home_suburb,home_latitude,home_longitude,program)
		print("[**]Insert student record successfully")
		fss = re.sub(r'[\(\)\s]+', "", friend)
		fs = re.split(',',fss)
		for cell in fs:
			friobj.insert(zid,cell);
			print("[**]Insert friend record successfully")
	except :
		print("[**]student has existed")
	#print(fs)
	pass
def findreply(commentid,fn,replies):
    print("[++++++] replyfile: " + fn) 
    #print(postid)
    #print(file)
    replyid = str(uuid.uuid1())
    zid = '' 
    message = ''
    createdate = ''
    file = open(fn)
    while 1:
        line = file.readline()
        if not line:
            break
        #print(line)
        line = re.sub(r'\s$', "", line)
        if(re.match('^[ ]*from:',line)):
            tmp = re.split(':[ ]*',line)
            zid = tmp[1]
        elif(re.match('^[ ]*time:',line)):
            tmp = re.split(':[ ]*',line,1)
            createdate = tmp[1]
        elif(re.match('^[ ]*message:',line)):
            tmp = re.split(':[ ]*',line,1)
            message = tmp[1]
    '''
    print("commentid:" + commentid )
    print("replyid:" + replyid)
    print("zid:" + zid)
    print("message:" + message )
    print("createdate:" + createdate )
    '''
    print("[******] replyid:" + replyid)
    #coments.insert(postid,commentid,zid,message,createdate)
    replies.insert(commentid,replyid,zid,message,createdate)
    pass
def findComment(postid,fn,coments,replies,dirname):
    #print(postid)
    #print(file)
    print("[++++] commentfile: " + fn) 
    commentid = str(uuid.uuid1())
    zid = '' 
    message = ''
    createdate = ''
    file = open(dirname + '/' + fn)
    while 1:
        line = file.readline()
        if not line:
            break
        #print(line)
        line = re.sub(r'\s$', "", line)
        if(re.match('^[ ]*from:',line)):
            tmp = re.split(':[ ]*',line)
            zid = tmp[1]
        elif(re.match('^[ ]*time:',line)):
            tmp = re.split(':[ ]*',line,1)
            createdate = tmp[1]
        elif(re.match('^[ ]*message:',line)):
            tmp = re.split(':[ ]*',line,1)
            message = tmp[1]
    '''
    print("postid:" + postid)
    print("commentid:" + commentid )
    print("zid:" + zid)
    print("message:" + message )
    print("createdate:" + createdate )
    '''
    print("[*****] commentid:" + commentid )
    coments.insert(postid,commentid,zid,message,createdate)
    for file in os.listdir(dirname):
        num = fn.replace(".txt","")
        #find comment
        if(re.match("^"+ num +"-[0-9]+[.]{1}",file)):
            findreply(commentid,dirname + "/"+file,replies)
            
    pass
def storePost(fn,posts,comments,replies,dirname):
	print("[--]post file : " + fn)
	zid = ''
	postid = str(uuid.uuid1())
	latitude = ''
	longitude = ''
	message = ''
	createdate = ''
	file = open(dirname + '/' + fn)
	while 1:
		line = file.readline()
		if not line:
			break
		#print(line)
		line = re.sub(r'\s$', "", line)
		if(re.match('^[ ]*from:',line)):
		    tmp = re.split(':[ ]*',line)
		    zid = tmp[1]
		elif(re.match('^[ ]*time:',line)):
		    tmp = re.split(':[ ]*',line,1)
		    createdate = tmp[1]
		elif(re.match('^[ ]*latitude:',line)):
		    tmp = re.split(':[ ]*',line)
		    latitude = tmp[1]
		elif(re.match('^[ ]*longitude:',line)):
		    tmp = re.split(':[ ]*',line)
		    longitude = tmp[1]
		elif(re.match('^[ ]*message:',line)):
		    tmp = re.split(':[ ]*',line,1)
		    message = tmp[1]
	'''
    print("zid:" + zid )
	print("postid:" + postid)
	print("latitude:" + latitude )
	print("longitude:" + longitude )
	print("message:" + message )
	print("createdate:" + createdate )
    '''
	print("[****] postid:" + postid)
	posts.insert(zid,postid,latitude,longitude,message,createdate)
	for file in os.listdir(dirname):
		#print(file)
		num = fn.replace(".txt","")
        #find comment
		if(re.match("^"+ num +"-[0-9]+[.]{1}",file)):
			findComment(postid,file,comments,replies,dirname)
			#print(file)
	
	
if __name__ == '__main__':
	'''
	user = User('test.db')
    user.delete_all()
    user.insert('ben', 'attal')
    user.insert('hello', 'world')
    cursor =  user.select_all('*')
    print(cursor.fetchall())
    cursor.close()
	'''
	#get user
	ROOT = sys.argv[1]
	#print(ROOT)
	if(len(ROOT) == 0):
		exit(0) 
	print("[*]ROOT DIR name is:" + ROOT)
	user = User(ROOT+'.db')
	friend = Friend(ROOT+'.db')
	posts = Posts(ROOT+'.db')
	comments = Comments(ROOT+'.db')
	replies = Replies(ROOT+'.db')
	for dir in os.listdir(ROOT):
		print("[+]student zid : " + dir);
		for file in os.listdir(ROOT + "/"+ dir):	
			#print(file)
			if(file == "student.txt" and "img.jpg" in os.listdir(ROOT + "/"+ dir)):
				readUserprofile(user,friend,ROOT + "/"+ dir + '/' + file,1)
				pass
			elif(file == "student.txt" and "img.jpg" not in os.listdir(ROOT + "/"+ dir)):
				readUserprofile(user,friend,ROOT + "/"+ dir + '/' + file,0)
				pass
			elif("img" not in file ):
				#print(file)
				if(re.match("^[0-9]+[.]{1}.",file)):
					storePost(file,posts,comments,replies,ROOT + "/"+ dir)
				pass
	
	
	