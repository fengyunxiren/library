#!/usr/bin python
#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test,login_required
from django.contrib.auth.models import User
from django.contrib import auth
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from management.models import MyUser,Book,Img,Pdf
from django.core.urlresolvers import reverse
from management.utils import permission_check
import os
import magic
from management.douban import book_search

import urllib
from io import BytesIO
from django.core.files import File

# Create your views here.
def index(request):
    user=request.user if request.user.is_authenticated() else None
    content={
            'active_menu':'homepage',
            'user':user,
            }
    return render(request,'management/index.html',content)

def signup(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('homepage'))
    state=None
    if request.method=='POST':
        password=request.POST.get('password','')
        repeat_password=request.POST.get('repeat_password','')
        if password == '' or repeat_password=='':
            state='empty'
        elif password!=repeat_password:
            state='repeat_error'
        else:
            username=request.POST.get('username','')
            if User.objects.filter(username=username):
                state='user_exist'
            else:
                new_user=User.objects.create_user(username=username,password=password,email=request.POST.get('email',''))
                new_user.save()
                new_my_user=MyUser(user=new_user,nickname=request.POST.get('nickname',''))
                new_my_user.save()
                state='success'
    content={
                'active_menu':'homepage',
                'state':state,
                'user':None,
                }
    return render(request,'management/signup.html',content)


def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('homepage'))
    state=None
    if request.method=='POST':
        username=request.POST.get('username','')
        password=request.POST.get('password','')
        user=auth.authenticate(username=username,password=password)
        if user is not None:
            auth.login(request,user)
            return HttpResponseRedirect(reverse('homepage'))
        else:
            state='not_exist_or_password_error'

    content={
            'active_menu':'homepage',
            'state':state,
            'user':None,
            }
    return render(request,'management/login.html',content)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('homepage'))


@login_required
def set_password(request):
    user=request.user
    state=None
    if request.method=='POST':
        old_password=request.POST.get('old_password','')
        new_password=request.POST.get('new_password','')
        repeat_password=request.POST.get('repeat_password','')
        if user.check_password(old_password):
            if not new_password:
                state='empty'
            elif new_password!=repeat_password:
                state='repeat_error'
            else:
                user.set_password(new_password)
                user.save()
                state='success'
        else:
            state='password_error'

    content={
            'user':user,
            'active_menu':'homepage',
            'state':state,
            }
    return render(request,'management/set_password.html',content)


@user_passes_test(permission_check)
def add_book(request):
    user=request.user
    state=None
    if request.method=='POST':
        new_book=Book(
                name=request.POST.get('name',''),
                author=request.POST.get('author',''),
                category=request.POST.get('category',''),
                price=request.POST.get('price',0),
                publish_date=request.POST.get('publish_date',''),
                summary=request.POST.get('summary','')
                )
        new_book.save()
        state='success'

    content={
                'user':user,
                'active_menu':'add_book',
                'state':state,
            }
    return render(request,'management/add_book.html',content)


def view_book_list(request):
    user=request.user if request.user.is_authenticated() else None
    category_list=Book.objects.values_list('category',flat=True).distinct()
    query_category=request.GET.get('category','all')
    if(not query_category) or Book.objects.filter(category=query_category).count() is 0:
        query_category = 'all'
        book_list=Book.objects.all()
    else:
        book_list=Book.objects.filter(category=query_category)

    if request.method=='POST':
        keyword=request.POST.get('keyword','')
        book_list=Book.objects.filter(name__contains=keyword)
        query_category='all'

    paginator=Paginator(book_list,15)
    page=request.GET.get('page')
    try:
        book_list=paginator.page(page)
    except PageNotAnInteger:
        book_list=paginator.page(1)
    except EmptyPage:
        book_list=paginator.page(paginator.num_pages)


    content={
            'user':user,
            'active_menu':'view_book',
            'category_list':category_list,
            'query_category':query_category,
            'book_list':book_list,
            }
    return render(request,'management/view_book_list.html',content)

def detail(request):
    user=request.user if request.user.is_authenticated() else None
    book_id=request.GET.get('id','')
    if book_id=='':
        return HttpResponseRedirect(reverse('view_book_list'))
    try:
        book=Book.objects.get(pk=book_id)
    except Book.DoesNotExist:
        return HttpResponseRedirect(reverse('view_book_list'))

    content={
            'user':user,
            'active_menu':'view_book',
            'book':book,
            }
    return render(request,'management/detail.html',content)


@user_passes_test(permission_check)
def add_img(request):
    user=request.user
    state=None
    if request.method=='POST':
        try:
            new_img=Img(
                    name=request.POST.get('name',''),
                    description=request.POST.get('description',''),
                    img=request.FILES.get('img',''),
                    book=Book.objects.get(id=request.POST.get('book',''))
                    )
            new_img.save()
        except Book.DoesNotExist as e:
            state='error'
            print(e)
        else:
            state='success'


    content={
            'user':user,
            'state':state,
            'book_list':Book.objects.all(),
            'active_menu':'add_img',
            }
    return render(request,'management/add_img.html',content)

@user_passes_test(permission_check)
def add_pdf(request):
    user=request.user
    state=None
    if request.method=='POST':
        try:
            new_pdf=Pdf(
                    name=request.POST.get('name',''),
                    descriptions=request.POST.get('description',''),
                    pdf=request.FILES.get('pdf',''),
                    book=Book.objects.get(id=request.POST.get('book',''))
                    )
            new_pdf.save()
        except Book.DoesNotExist as e:
            state='error'
            print(e)
        else:
            state=judgeAndTransform(new_pdf)
            #state='success'

    content={
            'user':user,
            'state':state,
            'book_list':Book.objects.all(),
            'active_menu':'add_pdf',
            }
    return render(request,'management/add_pdf.html',content)

def view_pdf(request):
    user=request.user if request.user.is_authenticated() else None
    book_id=request.GET.get('id','')
    if book_id=='':
        return HttpResponseRedirect(reverse('view_book_list'))
    try:
        book=Book.objects.get(pk=book_id)
        pdf=Pdf.objects.get(book=book)
    except Book.DoesNotExist:
        return HttpResponseRedirect(reverse('view_book_list'))
    except Pdf.DoesNotExist:
        return HttpResponseRedirect(reverse('view_book_list'))

    content={
            'user':user,
            'active_menu':'view_pdf',
            'pdf':pdf,
            }
    return render(request,'management/view_pdf.html',content)

@user_passes_test(permission_check)
def import_book(request):
    user=request.user if request.user.is_authenticated() else None
    list_search=[]
    jud=0
    if request.method=='POST':
        query_name=request.POST.get('query_search','')
        query_name=query_name.encode("utf-8")
        list_search=book_search(query_name)
        jud=1
    content={
            'user':user,
            'active_menu':'import_book',
            'list_search':list_search,
            'jud':jud
            }
    return render(request,'management/import_book.html',content)

@user_passes_test(permission_check)
def import_info(request):
    user=request.user if request.user.is_authenticated() else None
    state=None
    if request.method=='POST':
        books=request.POST.getlist('search','')
        for book in books:
            book=eval(book)
            book_name=book['title']
            book_author=book['author']
            book_price=book['price']
            book_pubdate=book['pubdate']
            book_sum=book['summary']
            if book['category']:
                book_category=book['category']
            else:
                book_category=u'导入图书'
            try:
                new_book=Book(
                        name=book_name,
                        author=book_author,
                        price=book_price,
                        category=book_category,
                        publish_date=book_pubdate,
                        summary=book_sum
                        )
                new_book.save()
                state='success'
            except:
                state='error'
            else:
                if book.has_key('image'):
                    book_image=book['image']
                    try:
                        book_this=Book.objects.get(name=book_name)
                        filename=os.path.basename(book_image)
                        response=urllib.urlopen(book_image)
                        io=BytesIO(response.read())
                        new_pimg=Img()
                        new_pimg.book=book_this
                        new_pimg.name=book_this.name
                        new_pimg.description=book_this.category
                        new_pimg.img.save(filename,File(io))
                        new_pimg.save()
                    except Exception,ex:
                        print Exception,":",ex

    content={
            'user':user,
            'active_menu':'import_info',
            'state':state,
            }
    return render(request,'management/import_info.html',content)

        


def judgeAndTransform(pdf):
    p_path=pdf.pdf.path
    p_name=pdf.pdf.name
    s=magic.from_file(p_path).split(',')[0]
    if s!='PDF document':
        try:
            os.system("soffice --convert-to --headless pdf --outdir '%s' '%s'" % (os.path.dirname(p_path),p_path))
        except:
            return 'error'
        else:
            name=u','.join(p_name.split('.')[:-1])+'.pdf'
            pdf.pdf.name=name
            pdf.save()
            os.system("rm -rf '%s'" % p_path)
            return 'success'
    else:
        return 'success'



