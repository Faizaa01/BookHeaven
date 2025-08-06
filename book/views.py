from rest_framework import status
from django.db.models import Count
from rest_framework.response import Response
from book.paginations import DefaultPagination
# from drf_yasg.utils import swagger_auto_schema
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from book.models import Author, Book, BorrowRecord, Member, Category
from book.serializers import AuthorSerializer, BookSerializer, BorrowRecordSerializer, CategorySerializer, MemberSerializer, UpdateBorrowRecordSerializer



class BookViewSet(ModelViewSet):
    queryset = Book.objects.select_related('author', 'category').all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    pagination_class = DefaultPagination
    search_fields = ['title', 'author__name', 'category__name']
    ordering_fields = ['availability_status']
    def get_permissions(self):
        if self.action in ['create', 'update_status', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        if Book.objects.filter(title=request.data.get('title')).exists():
            return Response({"detail": "Book already exists."}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)



class AuthorViewSet(ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def get_permissions(self):
        if self.action in ['create', 'update_status', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        if Author.objects.filter(name__iexact=request.data.get('name')).exists():
            return Response({"detail": "Author with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)


class BorrowRecordViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['update']:
            return UpdateBorrowRecordSerializer
        return BorrowRecordSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return BorrowRecord.objects.none()

        user = self.request.user
        if user.is_staff:
            return BorrowRecord.objects.select_related('book', 'member', 'member__user')
        return BorrowRecord.objects.select_related('book', 'member', 'member__user').filter(member__user=user)   

    def perform_create(self, serializer):
        member = self.request.user.member
        book = serializer.validated_data.get('book')

        if not book.availability_status:
            raise ValidationError("This book is currently not available for borrowing.")
        if BorrowRecord.objects.filter(book=book, member=member, return_date__isnull=True).exists():
            raise ValidationError("You have already borrowed this book and not returned it yet.")

        book.availability_status = False
        book.save()
        serializer.save(member=member)

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.return_date:
            if not instance.book.availability_status:
                instance.book.availability_status = True
                instance.book.save()
            instance.status = 'RETURNED'
            instance.save()


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.annotate(book_count=Count('books')).all() 
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['create', 'update_status', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        if Category.objects.filter(name__iexact=request.data.get('name')).exists():
            return Response({"detail": "Category with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)



class MemberViewSet(ModelViewSet):
    queryset = Member.objects.select_related('user').all()
    serializer_class = MemberSerializer
    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save()
