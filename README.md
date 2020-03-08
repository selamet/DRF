

## DRF

### Bazı Önemli Kavramlar:
* serializer --> Modele bağlı olarak otomatik fieldlar oluşturur. Database içeriisnde ki verileri Json ve XML formatına çevirir.
* Serializerler ModelSerializer ve normal serializer olarak ikiye ayırılır.


Başlamadan önce basit bir model yapısı oluşturalım.  
##### models.py
```python
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    title = models.CharField(max_length=120)
    content = models.TextField()
    draft = models.BooleanField(default=False)
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    slug = models.SlugField(unique=True, max_length=150, editable=False)

    def save(self, *args, **kwargs):
        if not self.id:  ## idsi yoksa ilk defa oluşturuluyordur bu yüzden self.created
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Post, self).save(*args, **kwargs)

```

#### Normal Serializer:

##### serializers.py
```python
from rest_framework import serializers
from models. import Post

class PostSerrializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    content = serializers.CharField(max_length=200)
```
#### ModelSerializer:

* model --> model
* fields --> çekmek istediğimiz fieldlar

##### serializers.py
```python
from rest_framework import serializers
from models import Post


class PostSerrializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            'title', 'content'
        ]

```

## Generic Views

#### ListAPIView
* Listeleme işlemini gerçekleştirir.

##### views.py
```python
from rest_framework.generics import ListAPIView
from models import Post
from serializers import PostSerrializer


class PostListAPIView(ListAPIView):
    queryset = Post.object.all()
    serializer_class = PostSerrializer
```


####   RetrieveAPIView
* Geriye tek bir model döndürür.
* lookup_field --> neye göre detay sayfasına gidilecek? ` pk`,  `slug` vs default değeri `pk`

##### views.py
```python
from rest_framework.generics import RetrieveAPIView
from models import Post
from serializers import PostSerrializer


class PostDetailAPIView(RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'slug'

```

#### DestroyAPIView & UpdateAPIView
* DestroyAPIView --> Silme işlemi gerçekleştirir
* UpdateAPIView --> Güncelleme işlemi gerçekleştirir.


##### views.py
```python
from rest_framework.generics import DestroyAPIView, UpdateAPIView,
from post.api.serializers import PostSerializer
from post.models import Post


class PostDeleteAPIView(DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'slug'


class PostUpdateAPIView(UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'slug'
```

 Serializere yeni bir serializer class'ı ekliyoruz
##### serializers.py

```python
class PostUpdateCreateSeralizer(serializers.ModelSerializer):
    class Meta:

        model = Post
    fields = ['title', 'content', 'image']

```
#### CreateAPIView:
* perform_create --> create işlemi gerçekleşeceği zaman tetiklenir mail gönderme celery worker bu kısımdan gönderebiliriz.

##### views.py
```python
from rest_framework.generics import CreateAPIView
from serializer import PostUpdateCreateSeralizer


class PostCreateAPIView(CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostUpdateCreateSeralizer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostUpdateAPIView(UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostUpdateCreateSeralizer
    lookup_field = 'slug'

    def perform_update(self, serializer):
	...
```

####  RetrieveUpdateAPIView
* update işleminde değerler fieldların içerisine yerleşmiş bir şekilde geriye döner.

##### views.py
```python
class PostUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostUpdateCreateSeralizer
    lookup_field = 'slug'

    def perform_update(self, serializer):
        serializer.save(modified_by=self.request.user)

```


## Url Dosyası:

* Bu aşamaya kadar yazmış olduğumuz viewların url tanımları

#### urls.py
```python
from django.urls import path, include
from post.api.views import PostListAPIView, PostDetailAPIView, PostDeleteAPIView, PostUpdateAPIView, PostCreateAPIView

app_name = 'post'

urlpatterns = [
    path('list', PostListAPIView.as_view(), name='list'),
    path('detail/<slug>', PostDetailAPIView.as_view(), name='detail'),
    path('update/<slug>', PostUpdateAPIView.as_view(), name='update'),
    path('delete/<slug>', PostDeleteAPIView.as_view(), name='delete'),
    path('create', PostCreateAPIView.as_view(), name='create'),
]

```

## Kullanıcı Yetkileri :

 * permissions_classes --> Kullanıcı yetkileri burada ayarlarını.

 ##### views.py
```python
from rest_framework.generics import CreateAPIView
from serializer import PostUpdateCreateSeralizer
from rest_framework.permissions import IsAuthenticated


class PostCreateAPIView(CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostUpdateCreateSeralizer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

```

### Custom Permissions :
* Kendi yazdığımız permissionslardır.
* BasePermission Classından türetilir
##### permissions.py

```python
from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    message = "You must be the owner of this object."

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_superuser
```
#### Custom Permissions Kullanımı :

##### views.py
```python
from rest_framework.generics import CreateAPIView
from serializer import PostUpdateCreateSeralizer
from rest_framework.permissions import IsAuthenticated
from post.api.permissions import IsOwner


class PostUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostUpdateCreateSeralizer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated, IsOwner]

    def perform_update(self, serializer):
        serializer.save(modified_by=self.request.user)
```

### has_permission && has_object_permission

* has_permission --> İlk önce koşul tanımaksızın burası çalışır. Post yapma olanağı tanımaz.
* has_object_permission --> Delete methoduyla işlem yaptığımız zaman çalışır

##### permissions.py
```python

from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    message = "You must be the owner of this object."

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_superuser
```

## Serializer Methodları:

* save(self, validated_data) --> create fonksiyonu mu yoksa update fonksiyonumu çalışacağına karar verir.
* create(self, validated_data) --> create işlemi yapıldığı zaman tetiklenir
* update (self, instance, validate_date) --> update işlemi tetikler
* validated_tittle(self, value) --> tittle a ait işlemleri burada gerçekleştiririz.
* validated(self,attrs) --> tüm fieldlar üzerinde çalışır

##### serializers.py
```python
from rest_framework import serializers
from post.models import Post

class PostUpdateCreateSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content']

    def create(self, validated_data):
        title = validated_data['title]
        ##return validated_data
        return Post.objects.create(user=self.context['request'].user, **validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.title = 'edited'
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance

    def validate_title(self, value):
        if value == 'deger'
            raise serializers.ValidationError('Bu değer girilemez.')
        return value

    def validate(self, attrs):
        if attrs['title'] == 'deger':
            attrs['title'] = 'gecersiz'
            raise serializers.ValidationError('Bu değer girilemez.')
        return attrs

```


### Search İşlemi && get_queryset(self):
* get_queryset(self) --> Bu method ile filtreleme yapabiliriz
* filter_backends -->  Kullanacağımız filtre yöntemi
* search_fields --> neye gore arama yapacağımızı belirtiriz
* OrderingFilter --> neye göre sıralayacağımızı belirtiriz
	*  ....../api/post/list?search=Lorem&ordering=title

##### views.py
```python
from rest_framework.filters import SearchFilter, OrderingFilter


class PostListAPIView(ListAPIView):
    serializer_class = PostSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'content']

    def get_queryset(self):
        queryset = Post.objects.filter(draft=False)
        return queryset
```

### Pagination

##### paginations.py

```python
from rest_framework.pagination import PageNumberPagination


class PostPagination(PageNumberPagination):
    page_size = 2
```
##### views.py
```python
from post.api.paginations import PostPagination


class PostListAPIView(ListAPIView):
    ...
    pagination_class = PostPagination

```

### Hyperlinked Identity
* slug yerine ana sayfada link döndürmemize olanak sağlar

##### serializers.py
```python
from rest_framework import serializers
from post.models import Post


class PostSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='namespace:name',
        lookup_field='slug'
    )

    class Meta:
        model = Post
        fields = ['username', 'title', 'content', 'url', 'created', ]
```

### Serializer Method Field

* Serializer kısmında gösterilen değer üzerinde değişiklik yapmaya olanak sağlar
* obj --> serialize edilen obje
* method_name --> method ismi girilmelidir
* get_username --> method_name gerek kalmadan işlemleri gerçekleştirir.
##### serializers.py	 
```python
from rest_framework import serializers
from post.models import Post


class PostSerializer(serializers.ModelSerializer):
    ...
    # username= serializers.SerializerMethodField(method_name='username_new')
    username = serializers.SerializerMethodField()
    ...

    def get_username(self, obj):
        return str(obj.user.username)

    def username_new(self, obj):
        return str(obj.user.username)

```

--- 

## Comment Modülü:

Yeni bir app oluşturup basit bir Model `comment` yapısı oluşturalım

* def children() --> yorumun altındaki yorumları bulmamızı sağlayacak
* def any_children() --> parent altında herhangi bir yorum olup olmadığını kontrol edicek
##### models.py
```python
class Comment(models.Model):  
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post')  
    content = models.TextField()  
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')  
    created = models.DateTimeField(editable=False)  
  
  
    def save(self, *args, **kwargs):  
        if not self.id:  
            self.created = timezone.now()  
  
        self.modified = timezone.now()  
        return super(Comment, self).save(*args, **kwargs)  
  
    def children(self):  
        return Comment.objects.filter(parent=self)  
  
    @property  
	def any_children(self):  
        return Comment.objects.filter(parent=self).exists()
``` 

Serializer dosyamızı da oluşturalım
* exclude --> girilen parametre hariç tüm fieldları listeler

##### serializers.py
```python
from comment.models import Comment  
  
  
class CommentCreateSerializer(ModelSerializer):  
    class Meta:  
        model = Comment  
        exclude = ['created', ] 
  
  def validate(self, attrs):  
        if (attrs["parent"]):  
            if attrs['parent'].post != attrs['post']:  
                raise serializers.ValidationError('Yanlış birşeyler var')  
        return attrs
``` 

#### Comment Create View
###### views.py 

```python
class CommentCreateAPIView(CreateAPIView):  
    queryset = Comment.objects.all()  
    serializer_class = CommentCreateSerializer  
  
    def perform_create(self, serializer):  
        serializer.save(user=self.request.user)
```


#### İç içe yorum listeleme
* fields = '__all__'   --> tüm fieldları listeler
* get_replies --> datayı Serializer e gönderiyoruz daha sonra serialize edilmiş halini geriye döndürüyoruz. Bu şekilde yorumlar iç içe bir şekilde listelenme işlemi gerçekleştiriyor.

##### serializers.py

```python
class CommentListSerializer(ModelSerializer):  
    replies = SerializerMethodField()  
    user = UserSerializer()  
    post = PostCommentSerialize()  
  
    class Meta:  
        model = Comment  
        fields = '__all__'  
  # depth = 1 # Tüm verileri getirir  
  
  def get_replies(self, obj):  
        if obj.any_children:  
            return CommentListSerializer(obj.children(), many=True).data

``` 


##### views.py

```python
class CommentListAPIView(ListAPIView):  
    serializer_class = CommentListSerializer  
  
    def get_queryset(self):  
        return  Comment.objects.filter(parent=None)
``` 

### Posta özgü yorumlar 

* Hem postu hemde posta
* .......ap/comment/deneme?q=5
* ?q= 5' I back ende yollarız.  Erişmek için: `self.request.GET.get("q")`
* Bu şekilde 5 nolu id ye sahip olan yorumları döndürürüz.

##### post.views.py

```python
class CommentListAPIView(ListAPIView):  
    serializer_class = CommentListSerializer  
    pagination_class = CommentPagination  
  
    def get_queryset(self):  
        queryset = Comment.objects.filter(parent=None)  
        query = self.request.GET.get("q")  
        if query:  
            queryset = Comment.objects.filter(post=query)  
        return queryset
```

### İç İçe Serializer

* depth = 1 --> ForeignKey le bağlı olan tüm verilerin içeriğini açar, parola dahil. 

##### post.serializers.py
```python
class CommentListSerializer(ModelSerializer):  
    replies = SerializerMethodField()  
  
    class Meta:  
        model = Comment  
        fields = '__all__'  
    	depth = 1 
```

* Bir diğer yol, daha güvenli
```python

class UserSerializer(ModelSerializer):  
    class Meta:  
        model = User  
        fields = ('last_name', 'first_name', 'id', 'email')

class CommentListSerializer(ModelSerializer):  
    replies = SerializerMethodField()  
	user = UserSerializer()
	
    class Meta:  
        model = Comment  
        fields = '__all__'  
    	
```

### Mixins

* Yazdığımız viewların sadece kendi işlemini (delete, create gibi) değil extra olarak başka işleri de yapmamıza olanak sağlar.


##### comment.views.py

```python
from rest_framework.mixins import DestroyModelMixin, UpdateModelMixin

class CommentDeleteAPIView(DestroyAPIView, UpdateModelMixin, RetrieveModelMixin):  
    queryset = Comment.objects.all()  
    serializer_class = CommentDeleteUpdateSerializer  
    lookup_field = 'pk'  
	permission_classes = [IsOwner]  
  
    def put(self, request, *args, **kwargs):  
        return self.update(request, *args, **kwargs)
        
    def delete(self, request, *args, **kwargs):  
        get self.retrieve(request, *args, **kwargs)    
``` 

## Üyelik İşlemleri

* JWT kullanırız. JWT bir authorization token yöntemi. 
* Bir linke istek yapalır ve bu linkin headerında bulunan authorization kısmına token yazılıp sunucuya gönderilir. 
* access token --> Kısa ömürlü 5dk
* refresh token --> 24 saat sürer 
* refresh token sayesinde yeni access token alınır. Refresh token sunucuya gönderilir ve o bize yeni access token döndürür.
* refresh token süresi son bulursa kullanıcının yeniden giriş yapması gerekir.
* JWT üç kısımdan oluşur
	```
	xxxxx.yyyyy.zzzzz
	header.payload.signature
	
	header = eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9 
	payload = eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTQzODI4NDMxLCJqdGkiOiI3ZjU5OTdiNzE1MGQ0NjU3OWRjMmI0OTE2NzA5N2U3YiIsInVzZXJfaWQiOjF9 
	signature = Ju70kdcaHKn1Qaz8H42zrOYk0Jx9kIckTn9Xx7vhikY
	```
* signature `header` ve `payload` kısımlarının base64 le şifrelenmiş halini ve settings dosyasında bulunan `SECRET_KEY` 'den oluşuyor.

* Kütüphaneyi kurmak için:
	```
	pip install djangorestframework_simplejwt
	```
##### settings.py

```python
REST_FRAMEWORK  =  {  'DEFAULT_AUTHENTICATION_CLASSES':  [
  'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
```

##### urls.py
```python
from  django.urls  import  path  from  rest_framework_simplejwt  import  views  as  jwt_views

  urlpatterns  =  [  # Your URLs... 
   path('api/token/',  jwt_views.TokenObtainPairView.as_view(),  name='token_obtain_pair'),
   path('api/token/refresh/',  jwt_views.TokenRefreshView.as_view(),  name='token_refresh'),  
   ]
``` 

* JWT Token süresini değiştirmek için

##### settings.py

```python
SIMPLE_JWT ={
	'ACCES_TOKEN_LIFETIME' : timedelta(minutes=15)
}
``` 


## Signal Kullanımı 

* receiver --> tetikleme kısmında rol alır.
* @receiver(post_save, sender=User)  --> User modelinde herhangi bir post_save işlemi olursa bu kısım tetiklenecektir.

```python
from django.db.models.signals import post_save  
from django.dispatch import receiver  
  
  
class Profile(models.Model):  
    user = models.OneToOneField(User, on_delete=models.CASCADE)  
    note = models.CharField(max_length=200)  
    twitter = models.CharField(max_length=200)  
  
    def __str__(self):  
        return self.user.username  
  
  
@receiver(post_save, sender=User)  
def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
        Profile.objects.create(user=instance)  
    instance.profile.save()

```  

### Profile Update

* validated_data.pop('profile') --> sadece profilin bulunduğu bilgileri çekeriz.
* raise_exception=True --> hata varsa hatayı fırlatır
* super(UserSerializer, self).update(instance, validated_data) --> Kullanıcı bilgilerini kayıt eder.
#####  account.seriarlizers.py
```python

class ProfileSerializer(ModelSerializer):  
    class Meta:  
        model = Profile  
        fields = ('id', 'note', 'twitter')  
  
  
class UserSerializer(ModelSerializer):  
    profile = ProfileSerializer()  
  
    class Meta:  
        model = User  
        fields = ('id', 'first_name', 'last_name', 'profile')  
  
    def update(self, instance, validated_data):  
        profile = validated_data.pop('profile')  
        profile_serializer = ProfileSerializer(instance=instance.profile, data=profile)  
        profile_serializer.is_valid(raise_exception=True)  
        profile_serializer.save()  
        return super(UserSerializer, self).update(instance, validated_data)
```


##### account.views.py

```python
class ProfileView(RetrieveUpdateAPIView):  
    permission_classes = (IsAuthenticated,)  
    serializer_class = UserSerializer  
    queryset = User.objects.all()  
  
    def get_object(self):  
        queryset = self.get_queryset()  
        obj = get_object_or_404(queryset, id=self.request.user.id)  
        return obj  
  
    def perform_update(self, serializer):  
        serializer.save(user=self.request.user)

```

### Password Chance:

* validate_password --> girilen parolanın güçlü olup olmadığını kontrol eder.
##### account.serializers.py

```python
class ChangePasswordSerializer(Serializer):  
    old_password = serializers.CharField(required=True)  
    new_password = serializers.CharField(required=True)  
  
    def validate_new_password(self, value):  
        validate_password(value)  
        return value
``` 
 ##### account.views.py

* get_object --> giriş yapan kullanıcıyı geriye döndürür.
* put --> update işleminde tetiklenir.
* self.object.check_password(old_password) --> eski parola doğru mu?
* update_session_auth_hash(request, self.object) --> login işlemi gerçekleştirir.
```python
class UpdatePassword(APIView):  
    permission_classes = (IsAuthenticated,)  
  
    def get_object(self):  
        return self.request.user  
  
    def put(self, request, *args, **kwargs):  
        self.object = self.get_object()  
  
        serializer = ChangePasswordSerializer(data=request.data)  
        if serializer.is_valid():  
            old_password = serializer.data.get('old_password')  
            if not self.object.check_password(old_password):  
                return Response({'old_password': 'wrong_password'}, status=status.HTTP_400_BAD_REQUEST)  
  
            self.object.set_password(serializer.data.get('new_password'))  
            self.object.save()  
            update_session_auth_hash(request, self.object)
		    return Response(status=status.HTTP_204_NO_CONTENT)  
  
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```