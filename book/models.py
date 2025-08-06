from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=100)
    biography = models.TextField()

    def __str__(self):
        return self.name
    

class Book(models.Model):
    title = models.CharField(max_length=200, help_text="The title of the book.")
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='books')
    isbn = models.CharField(max_length=13, unique=True, help_text="Unique 10 or 13-digit ISBN.")
    availability_status = models.BooleanField(default=True, help_text="True if available for borrowing.")

    def __str__(self):
        return self.title


class Member(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    membership_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class BorrowRecord(models.Model):
    BORROWED = 'Borrowed'
    RETURNED = 'Returned'
    STATUS_CHOICES = [
    ('BORROWED', 'Borrowed'),
    ('RETURNED', 'Returned'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='BORROWED')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records')
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.member} borrowed {self.book}"


