#!/usr/bin python
#-*- coding: UTF-8 -*-
import urllib
import json

URL="https://api.douban.com/v2/book/"

def book_isbn(isbn):
    isbn=isbn.strip()

    if (len(isbn)==10 or len(isbn)==13) and isbn.isdigit():
        url=URL+"/isbn/"+isbn
        s=urllib.urlopen(url)
        ss=s.read()
        s.close()
        jss=json.loads(ss)
    else:
        return 'error'
    info=dict()
    if jss.has_key('title'):
        info['title']=jss['title']

    if jss.has_key('author'):
        info['author']=jss['author']

    if jss.has_key('pubdate'):
        info['pubdate']=jss['pubdate']

    if jss.has_key('price'):
        info['price']=jss['price']

    if jss.has_key('category'):
        info['category']=jss['category']

    if jss.has_key('summary'):
        info['summary']=jss['summary']



def book_search(qname):
    qname.strip()
    url=URL+"search?q="+qname
    s=urllib.urlopen(url)
    ss=s.read()
    s.close()
    jsss=json.loads(ss)
    jsss=jsss['books']
    infos=[]
    for jss in jsss:
        info=dict()
        if jss.has_key('title'):
            info['title']=jss['title']

        if jss.has_key('author'):
            if len(jss)<3:
                info['author']=';'.join(jss['author'])
            else:
                info['author']=';'.join(jss['author'][:3])

        if jss.has_key('pubdate'):
            info['pubdate']=jss['pubdate'].replace(u'年','-').replace(u'月','-').replace(u'日','')
            if info['pubdate'].count('-')<2:
                info['pubdate']+="-01"

        if jss.has_key('price'):
            info['price']=filter(lambda ch: ch in '0123456789.',jss['price'])

        if jss.has_key('category'):
            info['category']=jss['category']

        if jss.has_key('summary'):
            info['summary']=jss['summary']
        
        infos=infos+[info,]

    return infos
