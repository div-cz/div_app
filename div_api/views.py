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
import jwt, datetime


@api_view(['POST'])
def RegisterView(request):
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

@api_view(['POST'])
def LoginView(request):
    email = request.data['email']
    password = request.data['password']
    user = User.objects.filter(email=email).first()

    if user is None:
        raise AuthenticationFailed('User not found')
    
    if not user.check_password(password):
        raise AuthenticationFailed('Incorrect password')
    
    payload = {
        'id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload,'8rhu*-wkdos', algorithm='HS256')
    response = Response()
    response.set_cookie(key="jwt", value=token, httponly=True)
    response.data = {
'       jwt': token
    }

    return response

@api_view(['GET'])
def UserView(request):

    token = request.COOKIES.get('jwt')

    if not token:
        raise AuthenticationFailed('Unauthenticated')
    
    try:
        payload = jwt.decode(token, '8rhu*-wkdos', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Unauthenticated') 

    user = User.objects.filter(id=payload['id']).first()
    serializer = UserSerializer(user)
    return Response(serializer.data)

@api_view(['GET'])
def LogoutView(request):
    response = Response()
    response.delete_cookie('jwt')
    response.data = {
        "message": "logout successfull"
    }
    return response

###MOVIES API Endpoints

@api_view(['GET'])
def MoviesGet(request):
    secret_key = request.headers.get('X-Secret-Key')
    if secret_key != settings.SECRET_KEY:
        return HttpResponseForbidden('Neplatný secret key')
    else:
        movies = Movie.objects.all()
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def MovieDetailGet(request, pk):
    secret_key = request.headers.get('X-Secret-Key')
    if secret_key != settings.SECRET_KEY:
        return HttpResponseForbidden('Neplatný secret key')
    else:
        try:
            movie = Movie.objects.get(pk=pk)
        except Movie.DoesNotExist:
            raise Http404("Film nebyl nalezen.")

        serializer = MovieSerializer(movie)
        return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAdminUser])
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

@api_view(['POST'])
@permission_classes([IsAdminUser])
def MovieCreate(request):
    serializer = MovieSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def MovieDelete(request,pk):
    try:
        movie = Movie.objects.get(pk=pk)
    except Movie.DoesNotExist:
        raise Http404("Film nebyl nalezen.")
    movie.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)