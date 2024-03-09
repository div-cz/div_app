from rest_framework.response import Response
from rest_framework.decorators import api_view,  permission_classes 
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAdminUser
from div_content.models import Movie
from .serializers import MovieSerializer
from .serializers import UserSerializer
from django.contrib.auth.models import User
from rest_framework import status
from django.conf import settings
from django.http import Http404, HttpResponseForbidden
from django.contrib.auth.decorators import login_required

###MOVIES API Endpoints

@login_required
@api_view(['GET'])
def MoviesGet(request):
    movies = Movie.objects.all()
    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data)

@login_required
@api_view(['GET'])
def MovieDetailGet(request, pk):
    try:
        movie = Movie.objects.get(pk=pk)
    except Movie.DoesNotExist:
        raise Http404("Film nebyl nalezen.")
    serializer = MovieSerializer(movie)
    return Response(serializer.data)

@login_required
@api_view(['PATCH'])
def MovieDetailPatch(request, pk):
    try:
        movie = Movie.objects.get(pk=pk)
    except Movie.DoesNotExist:
        raise Http404("Film nebyl nalezen.")

    serializer = MovieSerializer(movie, data=request.data,partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
@api_view(['POST'])
def MovieCreate(request):
    serializer = MovieSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
@api_view(['DELETE'])
def MovieDelete(request,pk):
    try:
        movie = Movie.objects.get(pk=pk)
    except Movie.DoesNotExist:
        raise Http404("Film nebyl nalezen.")
    movie.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)