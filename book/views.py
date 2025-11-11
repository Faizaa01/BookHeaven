from rest_framework import status
from django.utils import timezone
from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from book.models import Author, Book, BorrowRecord, Member, Category, BookImage
from book.serializers import AuthorSerializer, BookSerializer, BorrowRecordSerializer, CategorySerializer, MemberSerializer, BookImageSerializer
from book.paginations import DefaultPagination

class BookViewSet(ModelViewSet):
    queryset = Book.objects.select_related('author', 'category').all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'author', 'availability_status']
    pagination_class = DefaultPagination
    search_fields = ['title', 'author__name']
    ordering_fields = ['availability_status', 'title']

    def get_permissions(self):
        if self.action in ['create', 'update_status', 'destroy']:
            return [IsAdminUser()]
        if self.action in ['borrow', 'return_book']:
            return [IsAuthenticated()]
        return [AllowAny()]

    @action(detail=True, methods=['post'], url_path='borrow')
    def borrow(self, request, pk=None):
        book = self.get_object()
        member = request.user.member

        if BorrowRecord.objects.filter(book=book, member=member, status="BORROWED").exists():
            return Response({"error": "You already borrowed this book"}, status=status.HTTP_400_BAD_REQUEST)
        if not book.availability_status:
            return Response({"error": "Book is currently not available"}, status=status.HTTP_400_BAD_REQUEST)

        borrow_record = BorrowRecord.objects.create(
            book=book,
            member=member,
            status='BORROWED'
        )

        book.availability_status = False
        book.save()
        serializer = BorrowRecordSerializer(borrow_record)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='return', permission_classes=[IsAuthenticated])
    def return_book(self, request, pk=None):
        book = self.get_object()
        member = request.user.member

        try:
            borrow_record = BorrowRecord.objects.get(book=book, member=member, status='BORROWED')
        except BorrowRecord.DoesNotExist:
            return Response({"error": "You have no active borrow for this book"}, status=status.HTTP_404_NOT_FOUND)
        BorrowRecord.objects.create(
            book=book,
            member=member,
            status='RETURNED',
            borrow_date=borrow_record.borrow_date,
            return_date=timezone.now()
        )

        book.availability_status = True
        book.save()
        serializer = BorrowRecordSerializer(borrow_record)
        return Response(serializer.data, status=status.HTTP_200_OK)



class BookImageViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = BookImageSerializer

    def get_queryset(self):
        return BookImage.objects.filter(book_id=self.kwargs.get('book_pk'))
    
    def perform_create(self, serializer):
        serializer.save(book_id=self.kwargs.get('book_pk'))



class AuthorViewSet(ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def get_permissions(self):
        if self.action in ['create', 'update_status', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        if Author.objects.filter(name__iexact=request.data.get('name')).exists():
            return Response({"detail": "Author with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)


class BorrowRecordViewSet(ModelViewSet):
    serializer_class = BorrowRecordSerializer 
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return BorrowRecord.objects.none()

        user = self.request.user
        if not user.is_authenticated:
            return BorrowRecord.objects.none()
        if user.is_staff:
            return BorrowRecord.objects.select_related('book', 'member', 'member__user')
        return BorrowRecord.objects.select_related('book', 'member', 'member__user').filter(member__user=user)



class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.annotate(book_count=Count('books')).all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['create', 'update_status', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]

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
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save()
