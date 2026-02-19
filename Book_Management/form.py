from .models import MemberProfile,Book,BorrowTransaction,FinePayment,Category,Author,BookCopy
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# Form for phone, address, role
class MemberProfileForm(forms.ModelForm):
    class Meta:
        model = MemberProfile
        fields = ['phone', 'address','department','roll_no']



class BookForm(forms.ModelForm):
    class Meta: 
        model=Book
        fields=['title','isbn','category','authors','publisher','publication_year','language','description']
        
        
class BorrowTransactionForm(forms.ModelForm):
    class Meta:
        model=BorrowTransaction
        fields=['member','status']
        
        
        
class FineForm(forms.ModelForm):
    """Form definition for Fine."""

    class Meta:
        """Meta definition for Fineform."""

        model = FinePayment
        fields =['amount','paid']


class CategoryForm(forms.ModelForm):
    class Meta:
        model=Category
        fields=['name','description']
        
        
class AuthorForm(forms.ModelForm):
    class Meta:
        model=Author
        fields=['name','bio','date_of_birth']
        
        
# Form for adding copies
class BookCopyForm(forms.ModelForm):
    class Meta:
        model=BookCopy
        fields=['book','barcode','shelf_location','status','condition']