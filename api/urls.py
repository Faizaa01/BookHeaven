from django.urls import path, include
from rest_framework_nested import routers
from book.views import AuthorViewSet, BookViewSet, BorrowRecordViewSet, MemberViewSet, CategoryViewSet


router = routers.DefaultRouter()
router.register('books', BookViewSet, basename='books')
router.register('categories', CategoryViewSet)
router.register('member', MemberViewSet, basename='members')
router.register('borrowrecords', BorrowRecordViewSet, basename='borrowrecords')
router.register('authors', AuthorViewSet)

urlpatterns = router.urls