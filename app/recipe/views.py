from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, mixins
from core.models import Tag, Ingredient
from recipe import serializers


class BaseRecipeAttributesViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin
):
    """Base viewset for user owned recipe attributes"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects scoped to the current authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by("-name")

    def perform_create(self, serializer):
        """Create a new recipe attribute"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttributesViewSet):
    """Manage tags in the database"""

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttributesViewSet):
    """Manage ingredients in the database"""

    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
