from django.shortcuts import get_object_or_404

from rest_framework import filters, mixins
from rest_framework.viewsets import (GenericViewSet, ModelViewSet,
                                     ReadOnlyModelViewSet)

from posts.models import Comment, Follow, Group, Post
from .pagination import PostPagination
from .permissions import AuthenticatedOnly, OwnerOrReadOnly
from .serializers import (CommentSerializer, FollowerSerializer,
                          GroupSerializer, PostSerializer)


class ListCreateViewSet(mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        GenericViewSet
                        ):
    """View-set для вывода списка и создания объекта."""
    pass


class PostViewSet(ModelViewSet):
    """View-set для постов."""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PostPagination
    permission_classes = (OwnerOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# Не получиться наследоваться от ListCreateViewSet,
# так как по условию нельзя создать группу через api
class GroupViewSet(ReadOnlyModelViewSet):
    """View-set для групп."""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(ModelViewSet):
    """View-set для комментариев."""
    serializer_class = CommentSerializer
    permission_classes = (OwnerOrReadOnly,)

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(post=post_id)

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        serializer.save(
            author=self.request.user,
            post=post
        )


class FollowViewSet(ListCreateViewSet):
    """View-set для подписок."""
    serializer_class = FollowerSerializer
    permission_classes = (AuthenticatedOnly,)
    filter_backends = (filters.SearchFilter,)

    search_fields = ('user__username', 'following__username')

    def get_queryset(self):
        return Follow.objects.filter(
            user=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )
