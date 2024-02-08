from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import AuthenticationFailed
from div_content.models import Movie
from .serializers import MovieSerializer
from .serializers import UserSerializer
from django.contrib.auth.models import User
import jwt, datetime

@api_view(['GET'])
def getData(request):
    movies = Movie.objects.all()
    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data)

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
