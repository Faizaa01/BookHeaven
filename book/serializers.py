from decimal import Decimal
from django.conf import settings
from rest_framework import serializers
from django.contrib.auth import get_user_model
from book.models import Author, Book, BorrowRecord, Category, Member, BookImage

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    book_count = serializers.IntegerField(read_only=True, help_text="Return the number book in this category")

    class Meta:
        model = Category
        fields = ['id', 'name', 'book_count']

    

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'biography']


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(), write_only=True, source='author')
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), write_only=True, source='category')

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn','author_id', 'category', 'category_id','availability_status']


class BookImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    class Meta:
        model = BookImage
        fields = ['id', 'image']


class MemberSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    name = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Member
        fields = ['id' , 'user', 'name', 'email', 'membership_date']


class BorrowRecordSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    member = MemberSerializer(read_only=True)
    book = BookSerializer(read_only=True)

    class Meta:
        model = BorrowRecord
        fields = ['id', 'book', 'member', 'borrow_date', 'return_date', 'status']

    def validate(self, attrs):
        book = attrs.get('book')
        if not book.availability_status:
            raise serializers.ValidationError("This book is currently not available for borrowing.")
        return attrs

