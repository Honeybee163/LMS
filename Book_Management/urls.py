from . import views
from django.urls import path


urlpatterns=[
    path('',views.main,name='main'),
    path('librarian_dashboard',views.all_books,name='librarian_dashboard'),
    path('member_dashboard/',views.member_dashboard,name='member_dashboard'),
    path('register/',views.register_user,name='register'),
    path('login/',views.login_user,name='login'),
    path('logout/',views.logout_user,name='logout'),
    path('books_issued_by_members/',views.books_issued_by_members,name='books_issued_by_members'),
    path('add_category/',views.add_category,name='add_category'),
    path('add_author/',views.add_author,name='add_author'),
    path('add_copies/',views.add_copies,name='add_copies'),
    path('book_overdue/',views.book_overdue,name='book_overdue'),
    path('book_late/<str:book_name>/',views.calculate_days_late,name='calculate_days_late'),
    path('add_book/',views.add_new_book,name='add_book'),
    path('borrow_book/<str:book_name>/',views.borrowing_book,name='borrowing_book'),
    path('member_dashboard/',views.member_dashboard,name='member_dashboard'),
    path('available_books/',views.available_books,name='available_books'),
    path('return_book/<str:book_name>/',views.return_book,name='return_book'),
]