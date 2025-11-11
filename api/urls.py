from django.urls import path, include
from rest_framework_nested import routers
from book.views import AuthorViewSet, BookViewSet, BorrowRecordViewSet, MemberViewSet, CategoryViewSet, BookImageViewSet


router = routers.DefaultRouter()
router.register('books', BookViewSet, basename='books')
router.register('categories', CategoryViewSet)
router.register('member', MemberViewSet, basename='members')
router.register('borrowrecords', BorrowRecordViewSet, basename='borrowrecords')
router.register('authors', AuthorViewSet)

book_router = routers.NestedDefaultRouter(router, 'books', lookup='book')
book_router.register('images', BookImageViewSet, basename='book-images')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(book_router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]