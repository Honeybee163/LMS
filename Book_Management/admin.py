from django.contrib import admin
from .models import MemberProfile,Book,Author,Category,BookCopy

# Register your models here.
admin.site.register(MemberProfile)
admin.site.register(Book)
admin.site.register(Author)
admin.site.register(Category)
admin.site.register(BookCopy)