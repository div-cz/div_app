
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import BasePermission
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework import mixins,viewsets,filters,status

from div_content.models import (Metaindex, Creator, Movie,Bookauthor,Charactermeta,Creatorrole,Tvshow,Book)

from django.db.models import Q
from django.utils.functional import cached_property
from django.conf import settings

from .pagination import NoCountPagination

###ADMIN only access to API

class IsSuperUser(BasePermission):
    def has_permission(self,request,view):
        return bool(request.user and request.user.is_superuser)


from rest_framework import mixins, viewsets, filters, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from django.db.models import Prefetch

class BaseViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    pagination_class = NoCountPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['url']
    # ordering_fields = '__all__'  # povolit řazení podle všech polí
    # ordering = ['pk']  # výchozí řazení podle 'pk'

    def get_queryset(self):
        queryset = super().get_queryset().order_by('pk')
        if self.action == 'list':
            serializer_class = self.get_serializer_class()
            meta = getattr(serializer_class, 'Meta', None)
            fields = getattr(meta, 'fields', [])
            model = self.queryset.model
            model_fields = [field.name for field in model._meta.fields]
            valid_fields = [field for field in fields if field in model_fields]
            queryset = queryset.only(*valid_fields)
        else:
            queryset = self.apply_select_related_and_prefetch_related(queryset)
        return queryset

    def apply_select_related_and_prefetch_related(self, queryset):
        return queryset

    def list(self, request, *args, **kwargs):
        self.validate_query_params(request.query_params)
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        self.validate_query_params(request.query_params)
        instance = self.get_object_custom(kwargs['pk'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def validate_query_params(self, params):
        valid_params = ['limit', 'offset', 'search', 'format']
        for param in params:
            if param not in valid_params:
                raise ValidationError({"detail": f"Invalid parameter: {param}"})

        # Validate offset and limit
        if 'offset' in params:
            try:
                offset = int(params['offset'])
                if offset < 0:
                    raise ValidationError({"detail": "Offset must be a non-negative integer."})
            except ValueError:
                raise ValidationError({"detail": "Offset must be an integer."})

        if 'limit' in params:
            try:
                limit = int(params['limit'])
                if limit <= 0:
                    raise ValidationError({"detail": "Limit must be a positive integer."})
                if limit > self.pagination_class.max_limit:  # Kontrola proti maximálnímu limitu
                    raise ValidationError({"detail": f"Limit exceeds the maximum limit of {self.pagination_class.max_limit}."})
            except ValueError:
                raise ValidationError({"detail": "Limit must be an integer."})

    def get_object_custom(self, pk):
        queryset = self.get_queryset()

        try:
            if pk.isdigit():
                obj = queryset.get(pk=pk)
            else:
                obj = queryset.get(url=pk)
        except queryset.model.DoesNotExist:
            raise NotFound({"detail": "Not found."})

        self.check_object_permissions(self.request, obj)
        return obj

    # def retrieve(self, request, *args, **kwargs):
    #     self.validate_query_params(request.query_params)
    #     instance = self.get_object_custom(kwargs['pk'])
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)









