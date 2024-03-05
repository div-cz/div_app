#API calls 

api/movies [name='movie-list'] #GET
api/movie/<int:pk> [name='movie-detail-get'] #GET

api/movie/<int:pk>/edit [name='movie-detail-patch'] #PATCH
api/movie/create [name='movie-new'] #POST
api/movie/<int:pk>/delete [name='movie-delete'] #DELETE

#Authentication for Get 

X-Secret-Key = django-insecure-(7wns0c0f-zk&jpy02dw*^k9iv-q8dg4ofd36tz_+&!o^g3u+q

#Authentication for Update/Create/Delete

Registered user with privileges => User.is_staff = 1

