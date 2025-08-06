from django.contrib import admin
from book.models import Author, Book, BorrowRecord, Category, Member

admin.site.register(Author)
admin.site.register(Book)
admin.site.register(BorrowRecord)
admin.site.register(Category)
admin.site.register(Member)
