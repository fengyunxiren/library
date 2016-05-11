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
            info['pubdate']=info['pubdate'].replace('.','-')
            if info['pubdate'].count('-')==0:
                if len(info)==10:
                    info['pubdate']=info['pubdate'][:3]+'-'+info['pubdate'][4:5]+'-'+info['pubdate'][6:]
                else:
                    info['pubdate']="1970-07-01"
            elif info['pubdate'].count('-')==1:
                info['pubdate']+='-01'
                



        if jss.has_key('price'):
            info['price']=filter(lambda ch: ch in '0123456789.',jss['price'])

        if jss.has_key('tags'):
            for categorys in jss['tags']:
                category=categorys['name']
                if category != info['title'] and not(category in info['author']):
                    info['category']=category
                    break
                else:
                    info['category']=u'其它'

        if jss.has_key('summary'):
            info['summary']=jss['summary']

        infos+=[info,]
        
    return infos
