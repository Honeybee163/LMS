from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .decorators import role_required
from django.core.paginator import Paginator
from .models import (
    BorrowTransaction,
    BookCopy,
    MemberProfile,
    Category,
    Author,
    FinePayment,
)
from .form import (
    UserForm,
    BookForm,
    BorrowTransactionForm,
    MemberProfileForm,
    FineForm,
    CategoryForm,
    AuthorForm,
    BookCopyForm,
)
import datetime






# register user
def register_user(request):
    if request.method == "POST":
        user_form = UserForm(request.POST)
        profile_form = MemberProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            return redirect("login")

    else:
        user_form = UserForm()
        profile_form = MemberProfileForm()

    return render(
        request,
        "auth/register.html",
        {"user_form": user_form, "profile_form": profile_form},
    )






# login view
def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            role = user.member_profile.role.strip()
            print(role)

            login(request, user)

        if role == "Member":
            return redirect("member_dashboard")
        elif role in ["Librarian", "Admin"]:
                return redirect("librarian_dashboard")

    else:
        form = AuthenticationForm()

    return render(request, "auth/login.html", {"form": form})






# logout view
def logout_user(request):
    logout(request)
    return redirect("login")









# show books that are available
@role_required(["Admin", "Librarian"])
@login_required
def available_books(request):
    category_filter = request.GET.get("category", "")
    author_filter = request.GET.get("author", "")
    q = request.GET.get("q", "")
    books = BookCopy.objects.filter(status="available")
    author = Author.objects.all()
    paginator=Paginator(books,6)
    page_number=request.GET.get("page")
    page_obj=paginator.get_page(page_number)
    # search by title,author name or isbn number
    if q:
        books = books.filter(
            Q(book__title__icontains=q)
            | Q(book__authors__name__icontains=q)
            | Q(book__isbn__icontains=q)
        )
    # filter by category
    if category_filter:
        books = books.filter(book__category__id=category_filter)

    # filter by author
    if author_filter:
        books = books.filter(book__authors__id=author_filter)

    categories = Category.objects.all()
    return render(
        request,
        "staff/available_books.html",
        {
            "books": books,
            "categories": categories,
            "category_filter": category_filter,
            "author": author,
            "author_filter": author_filter,
            "page_obj":page_obj,
        },
    )





# show all books of library
@login_required
@role_required(["Admin", "Librarian"])
def all_books(request):
    books = BookCopy.objects.all()
    author = Author.objects.all()
    category_filter = request.GET.get("category", "")
    availability = request.GET.get("availability", "")
    author_filter = request.GET.get("author", "")
    q = request.GET.get("q", "")

    
    # search by title,author name or isbn number
    if q:
        books = books.filter(
            Q(book__title__icontains=q)
            | Q(book__authors__name__icontains=q)
            | Q(book__isbn__icontains=q)
        )
    # filter by category
    if category_filter:
        books = books.filter(book__category__id=category_filter)
    # filter b availability
    if availability:
        books = books.filter(status=availability)
    # filter by author
    if author_filter:
        books = books.filter(book__authors__id=author_filter)

    categories = Category.objects.all()
    # Now paginate **after filtering**
    paginator = Paginator(books, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "staff/all_books.html",
        {
            "books": books,
            "categories": categories,
            "category_filter": category_filter,
            "availability": availability,
            "author": author,
            "author_filter": author_filter,
            "page_obj": page_obj,
        },
    )





# main page for both members and staff
def main(request):
    return render(request, "auth/main.html")









# borrow books by member
@login_required
@role_required(["Admin", "Librarian"])
def borrowing_book(request, book_name):
    members = MemberProfile.objects.filter(role="Member")
    name = request.GET.get("name", "")
    if name:
        members = members.filter(user__username__icontains=name)

    if request.method == "POST":
        form = BorrowTransactionForm(request.POST)

        if form.is_valid():
            data = form.save(commit=False)
            member_profile = data.member

            # Count currently borrowed books
            count_books = BorrowTransaction.objects.filter(
                member=member_profile, status="borrowed"
            ).count()

            if count_books >= 3:
                return render(
                    request,
                    "staff/borrowing_book.html",
                    {
                        "form": form,
                        "members": members,
                        "error": "This member already has 3 books issued.",
                    },
                )
            copy = BookCopy.objects.filter(
                book__title__iexact=book_name,
                status__iexact="available"
            ).first()
            

            if copy is None:
                return render(
                    request,
                    "staff/borrowing_book.html",
                    {
                        "form": form,
                        "members": members,
                        "error": "No available copy for this book.",
                    },
                )

            data.book_copy = copy
            data.due_date = datetime.date.today() + datetime.timedelta(days=15)
            data.status = "borrowed"
            data.save()

            copy.status = "unavailable"
            copy.save()

            return redirect("available_books")

    else:
        form = BorrowTransactionForm()

    return render(
        request,
        "staff/borrowing_book.html",
        {"form": form, "members": members, "search_name": name},
    )





# show all books borrowed by member
@login_required
@role_required(["Member"])
def member_dashboard(request):
    user = request.user.id
    member_profile = MemberProfile.objects.get(user_id=user)

    borrowed_books = BorrowTransaction.objects.filter(
        member=member_profile
    ).select_related("book_copy__book")

    data = []

    for transaction in borrowed_books:
        # check overdue
        if (
            transaction.status == "borrowed"
            and transaction.due_date < datetime.date.today()
        ):
            display_status = "Overdue"
        else:
            display_status = transaction.status.capitalize()

        # check fine
        fine_amount = 0
        fine_paid = "No Fine"

        try:
            fine = FinePayment.objects.get(borrow_transaction=transaction)
            fine_amount = fine.amount
            fine_paid = "Paid" if fine.paid else "Unpaid"
        except FinePayment.DoesNotExist:
            fine_amount = 0
            fine_paid = "No Fine"

        data.append(
            {
                "title": transaction.book_copy.book.title,
                "borrowed_at": transaction.borrowed_at,
                "due_date": transaction.due_date,
                "status": display_status,
                "fine_amount": fine_amount,
                "fine_paid": fine_paid,
            }
        )

    return render(request, "member/member_dashboard.html", {"borrowed_books": data})







# show book each member issued
@login_required
@role_required(["Admin", "Librarian"])
# show all borrowed books
def books_issued_by_members(request):
    books = BorrowTransaction.objects.filter(status="borrowed")
    name = request.GET.get("name", "")
    if name:
        books = books.filter(member__user__username__icontains=name)
    today = datetime.date.today()
    return render(
        request,
        "staff/book_issued_by_members.html",
        {"books": books, "today": today, "name": name},
    )






# return book
@login_required
@role_required(["Admin", "Librarian"])
def return_book(request, book_name):
    transaction = BorrowTransaction.objects.filter(
        book_copy__book__title=book_name, status="borrowed"
    ).last()

    if transaction is None:
        messages.error(request, f"No borrowed transaction found for '{book_name}'.")
    else:
        transaction.returned_at = datetime.date.today()
        transaction.status = "returned"
        transaction.save()

        copy = transaction.book_copy
        copy.status = "available"
        copy.save()

        messages.success(request, f"Book '{book_name}' returned successfully.")

    # Redirect back to the same page
    return redirect(request.META.get("HTTP_REFERER", "books_issued_by_members"))










# show all books overdue
@login_required
@role_required(["Admin", "Librarian"])
def book_overdue(request):
    books = BorrowTransaction.objects.filter(
        Q(status="borrowed") & Q(due_date__lt=datetime.date.today())
    )
    name = request.GET.get("name", "")
    if name:
        books = books.filter(member__user__username__icontains=name)
    today = datetime.date.today()
    return render(
        request,
        "staff/book_overdue.html",
        {"books": books, "today": today, "name": name},
    )








# Fine calculation function:
# calculate days late
# store fine in model OR calculate dynamically
@login_required
@role_required(["Admin", "Librarian"])
def calculate_days_late(request, book_name):
    book = BorrowTransaction.objects.filter(
        book_copy__book__title=book_name, status="borrowed"
    ).last()

    if not book:
        messages.error(request, "No Borrow Record Found")

    days_late = (datetime.date.today() - book.due_date).days

    if days_late < 0:
        days_late = 0

    fine = days_late * 10

    # return fine,borrow status become returned,
    if request.method == "POST":
        fine_form = FineForm(request.POST)
        if fine_form.is_valid():
            f = fine_form.save(commit=False)
            f.amount = fine
            f.borrow_transaction = book
            f.save()
            book.status = "returned"
            book.returned_at = datetime.date.today()
            book.save()
            messages.error(request, "Fine Paid Successfully")
            return redirect(request.META.get("HTTP_REFERER", "staff/fine.html"))
    else:
        fine_form = FineForm(initial={"amount": fine})
    return render(request, "staff/fine.html", {"fine_form": fine_form})




# add new book
@login_required
@role_required(["Admin", "Librarian"])
def add_new_book(request):
    
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("add_book")
    else:
        form = BookForm()
    return render(request, "staff/add_book.html", {"form": form})








# add category
@login_required
@role_required(["Admin", "Librarian"])
def add_category(request):
    categories=Category.objects.all()
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("add_category")
    else:
        form = CategoryForm()
    return render(request, "staff/add_category.html", {"form": form,'categories':categories})








# add author
@login_required
@role_required(["Admin", "Librarian"])
def add_author(request):
    authors=Author.objects.all()
    if request.method == "POST":
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("add_author")
    else:
        form = AuthorForm()
    return render(request, "staff/add_author.html", {"form": form,"authors":authors})























# add copies of a book
@login_required
@role_required(["Admin", "Librarian"])
def add_copies(request):
    if request.method == "POST":
        form = BookCopyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("add_copies")
    else:
        form = BookCopyForm()
    return render(request, "staff/add_copies.html", {"form": form})
