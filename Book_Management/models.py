from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.
class MemberProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='member_profile')
    role=models.CharField(max_length=100,default='Member',choices=(('Member','Member'),('Admin','Admin'),('Librarian','Librarian')))
    membership_id=models.UUIDField(default=uuid.uuid4,editable=False)
    phone=models.CharField(max_length=100)
    address=models.CharField(max_length=100)
    is_active=models.BooleanField(default=True)
    joined_date=models.DateField(auto_now_add=True)
    roll_no=models.CharField(max_length=100,null=True)
    department=models.CharField(max_length=100,null=True)
    
    
    def __str__(self):
        return self.user.username
    
    
    
# Author
class Author(models.Model):
    name=models.CharField(max_length=100)
    bio=models.TextField(max_length=1000,blank=True,null=True)
    date_of_birth=models.DateField(blank=True,null=True)
    
    def __str__(self):
        return self.name



# Category
class Category(models.Model):
    name=models.CharField(max_length=100)
    description=models.TextField(max_length=1000,blank=True,null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"
    

# Book
class Book(models.Model):
    title=models.CharField(max_length=100)
    isbn=models.CharField(max_length=100,unique=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    authors=models.ManyToManyField(Author)
    publisher=models.CharField(max_length=100)
    publication_year=models.IntegerField()
    language=models.CharField(max_length=100)
    description=models.TextField(max_length=1000,blank=True,null=True)
    def __str__(self):
        return self.title

# BookCopy (barcode, condition, status)
class BookCopy(models.Model):
    book=models.ForeignKey(Book,on_delete=models.CASCADE)
    barcode=models.CharField(max_length=100,unique=True)
    shelf_location=models.CharField(max_length=100)
    status=models.CharField(max_length=100,choices=(('available','available'),('unavailable','unavailable')))
    condition=models.CharField(max_length=100,choices=(('good','good'),('medium','medium'),('bad','bad')))
    added_at=models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.book.title
    
    class Meta:
        verbose_name_plural = "Book Copies"
    
    
    

class BorrowTransaction(models.Model):
    member=models.ForeignKey(MemberProfile,on_delete=models.CASCADE)
    book_copy=models.ForeignKey(BookCopy,on_delete=models.CASCADE)
    borrowed_at=models.DateField(auto_now_add=True)
    due_date=models.DateField()
    returned_at=models.DateField(blank=True,null=True)
    status=models.CharField(max_length=100,choices=(('borrowed','borrowed'),('returned','returned')))
    
    def __str__(self):
        return self.book_copy.book.title
    
    
    


class FinePayment(models.Model):
    borrow_transaction=models.OneToOneField(BorrowTransaction,on_delete=models.CASCADE)
    amount=models.IntegerField()
    paid=models.BooleanField(default=False)
    paid_at=models.DateField(blank=True,null=True,auto_now_add=True)
    
    def __str__(self):
        return self.borrow_transaction.book_copy.book.title