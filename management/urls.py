from django.conf.urls import url
from management import views

urlpatterns=[
        url(r'^$',views.index,name='homepage'),
        url(r'^signup/$',views.signup,name='signup'),
        url(r'^login/$',views.login,name='login'),
        url(r'^logout/$',views.logout,name='logout'),
        url(r'^set_password/$',views.set_password,name='set_password'),
        url(r'^add_book/$',views.add_book,name='add_book'),
        url(r'^view_book_list/$',views.view_book_list,name='view_book_list'),
        url(r'^detail/$',views.detail,name='detail'),
        url(r'^add_img/$',views.add_img,name='add_img'),
        url(r'^add_pdf/$',views.add_pdf,name='add_pdf'),
        url(r'^view_pdf/$',views.view_pdf,name='view_pdf'),
        url(r'^import_book/$',views.import_book,name='import_book'),
        url(r'^import_info/$',views.import_info,name='import_info'),
        ]
