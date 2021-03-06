#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import sqlite3
import os, sys
import re
import uuid
queries = {
    'SELECT': 'SELECT %s FROM %s WHERE %s',
	'SELECT_ORDER': 'SELECT %s FROM %s WHERE %s ORDER BY createdate desc',
    'SELECT_ORDER_ASC': 'SELECT %s FROM %s WHERE %s ORDER BY createdate asc',
    'SELECT_ORDER_Recent': 'SELECT %s FROM %s WHERE %s ORDER BY createdate desc LIMIT 10',
    'SELECT_ALL': 'SELECT %s FROM %s',
    'INSERT': 'INSERT INTO %s VALUES(%s)',
    'UPDATE': 'UPDATE %s SET %s WHERE %s',
    'DELETE': 'DELETE FROM %s where %s',
    'DELETE_ALL': 'DELETE FROM %s',
    'CREATE_TABLE': 'CREATE TABLE IF NOT EXISTS %s(%s)',
    'DROP_TABLE': 'DROP TABLE %s',
	'SELECT_SEARCH_NAME': 'SELECT %s FROM %s WHERE %s',
    'SELECT_SEARCH_KEY': 'SELECT %s FROM %s WHERE %s ORDER BY createdate desc',
    'SELECT_ORDER_LEFTJOIN': 'SELECT %s FROM %s LEFT JOIN comments ON comments.postid = posts.postid LEFT JOIN replies ON comments.commentid = replies.commentid WHERE %s ORDER BY posts.createdate desc',
}


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
    def select_order(self, tables, *args, **kwargs):
        vals = ','.join([l for l in args])
        locs = ','.join(tables)
        conds = ' and '.join(['%s=?' % k for k in kwargs])
        subs = [kwargs[k] for k in kwargs]
        query = queries['SELECT_ORDER'] % (vals, locs, conds)
        return self.read(query, subs)
    def select_order_leftjoin(self, tables, *args, **kwargs):
        vals = ','.join([l for l in args])
        locs = ','.join(tables)
        #conds = ' and '.join(['message like "%%%s%%"' % (kwargs[k]) for k in kwargs])
        conds = "posts.message like \"%%" + kwargs['message'] + "%%\" or  comments.message like \"%%" + kwargs['message1'] + "%%\" or replies.message like \"%%" + kwargs['message2'] + "%%\""
        query = queries['SELECT_ORDER_LEFTJOIN'] % (vals, locs, conds)
        print(query)
        return self.read(query)
    def select_order_asc(self, tables, *args, **kwargs):
        vals = ','.join([l for l in args])
        locs = ','.join(tables)
        conds = ' and '.join(['%s=?' % k for k in kwargs])
        subs = [kwargs[k] for k in kwargs]
        query = queries['SELECT_ORDER_ASC'] % (vals, locs, conds)
        return self.read(query, subs)
    def select_order_recent(self, tables, *args, **kwargs):
        vals = ','.join([l for l in args])
        locs = ','.join(tables)
        conds = ' and '.join(['%s=?' % k for k in kwargs])
        subs = [kwargs[k] for k in kwargs]
        query = queries['SELECT_ORDER_Recent'] % (vals, locs, conds)
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
    def searchbyname(self, tables, *args, **kwargs):
        vals = ','.join([l for l in args])
        locs = ','.join(tables)
        conds = ' and '.join(['%s like "%%%s%%"' % (k,kwargs[k]) for k in kwargs])
        query = queries['SELECT_SEARCH_NAME'] % (vals, locs, conds)
        #print(query)
        return self.read(query)
    def searchbykey(self, tables, *args, **kwargs):
        vals = ','.join([l for l in args])
        locs = ','.join(tables)
        conds = ' and '.join(['%s like "%%%s%%"' % (k,kwargs[k]) for k in kwargs])
        query = queries['SELECT_SEARCH_KEY'] % (vals, locs, conds)
        #print(query)
        return self.read(query)
        
class Table(DatabaseObject):

    def __init__(self, data_file, table_name, values):
        super(Table, self).__init__(data_file)
        self.create_table(table_name, values)
        self.table_name = table_name

    def select(self, *args, **kwargs):
        return super(Table, self).select([self.table_name], *args, **kwargs)
    def select_order(self, *args, **kwargs):
        return super(Table, self).select_order([self.table_name], *args, **kwargs)
    def select_order_asc(self, *args, **kwargs):
        return super(Table, self).select_order_asc([self.table_name], *args, **kwargs)
    def select_order_recent(self, *args, **kwargs):
        return super(Table, self).select_order_recent([self.table_name], *args, **kwargs)
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
	
    def searchbyname(self, *args, **kwargs):
        return super(Table, self).searchbyname([self.table_name], *args, **kwargs)
    def searchbykey(self, *args, **kwargs):
        return super(Table, self).searchbykey([self.table_name], *args, **kwargs)
    def select_order_leftjoin(self, *args, **kwargs):
        return super(Table, self).select_order_leftjoin([self.table_name], *args, **kwargs)

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
        results = self.select('zid', zid=username,
                              password=password)
        return len(results) > 0
    def searchbyname(self, *args, **kwargs):
        cursor = super(User, self).searchbyname(*args, **kwargs)
        results = cursor.fetchall()
        cursor.close()
        return results
class Friend(Table):

    def __init__(self, data_file):
        super(Friend, self).__init__(data_file, 'friend',
                                   ['mainzid TEXT', 'twozid TEXT'])
    def insert(self, *args):
        self.free(super(Friend, self).insert(*args))
    def select(self, *args, **kwargs):
        cursor = super(Friend, self).select(*args, **kwargs)
        results = cursor.fetchall()
        cursor.close()
        return results
class Posts(Table):

    def __init__(self, data_file):
        super(Posts, self).__init__(data_file, 'posts',
                                   ['zid TEXT', 'postid TEXT','latitude NUMERIC','longitude NUMERIC','message TEXT','createdate DATETIME'])
    def insert(self, *args):
        self.free(super(Posts, self).insert(*args))
    def select_order(self, *args, **kwargs):
        cursor = super(Posts, self).select_order(*args, **kwargs)
        results = cursor.fetchall()
        cursor.close()
        return results
    def select_order_recent(self, *args, **kwargs):
        cursor = super(Posts, self).select_order_recent(*args, **kwargs)
        results = cursor.fetchall()
        cursor.close()
        return results
    def select_order_leftjoin(self, *args, **kwargs):
        cursor = super(Posts, self).select_order_leftjoin(*args, **kwargs)
        results = cursor.fetchall()
        cursor.close()
        return results
    def searchbykey(self, *args, **kwargs):
        cursor = super(Posts, self).searchbykey(*args, **kwargs)
        results = cursor.fetchall()
        cursor.close()
        return results
class Comments(Table):

    def __init__(self, data_file):
        super(Comments, self).__init__(data_file, 'comments',
                                   ['postid TEXT', 'commentid TEXT','zid','message TEXT','createdate DATETIME'])
    def insert(self, *args):
        self.free(super(Comments, self).insert(*args))  
    def select_order(self, *args, **kwargs):
        cursor = super(Comments, self).select_order_asc(*args, **kwargs)
        results = cursor.fetchall()
        cursor.close()
        return results
class Replies(Table):

    def __init__(self, data_file):
        super(Replies, self).__init__(data_file, 'replies',
                                   ['commentid TEXT', 'replyid TEXT','zid','message TEXT','createdate DATETIME'])
    def insert(self, *args):
        self.free(super(Replies, self).insert(*args)) 
    def select_order(self, *args, **kwargs):
        cursor = super(Replies, self).select_order_asc(*args, **kwargs)
        results = cursor.fetchall()
        cursor.close()
        return results
	
