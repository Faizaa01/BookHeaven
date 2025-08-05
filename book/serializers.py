from decimal import Decimal
from rest_framework import serializers
from django.contrib.auth import get_user_model
from book.models import Author, Book, BorrowRecord, Category, Member


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'category', 'availability_status']


class CategorySerializer(serializers.ModelSerializer):
    book_count = serializers.IntegerField(read_only=True, help_text="Return the number product in this category")

    class Meta:
        model = Category
        fields = ['id', 'name', 'book_count']

    

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'biography']


class MemberSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Member
        fields = ['id' ,'name', 'email', 'membership_date']


class BorrowRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorrowRecord
        fields = ['id', 'book', 'member', 'borrow_date', 'return_date']

    def validate(self, attrs):
        book = attrs.get('book')
        if not book.availability_status:
            raise serializers.ValidationError("This book is currently not available for borrowing.")
    
        return attrs


