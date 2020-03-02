
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
		if not self.id: ## idsi yoksa ilk defa oluşturuluyordur bu yüzden self.created
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

### Serializere yeni bir serializer class'ı ekliyoruz
##### serializers.py

```python
class PostUpdateCreateSeralizer(serializers.ModelSerializer):
	class Meta:
	model = Post
	fields = ['title', 'content', 'image']
```
#### CreateAPIView:
* perform_create --> create işlemi gerçekleşeceği zaman tetiklenir mail gönderme celery worker bu kısımdan gönderebiliriz.
```python
from  rest_framework.generics  import CreateAPIView
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

	def perform_update(self,serializer):
		...
```

####  RetrieveUpdateAPIView
* update işleminde değerler fieldların içerisine yerleşmiş bir şekilde geriye döner.

```python
class PostUpdateAPIView(RetrieveUpdateAPIView):
	queryset = Post.objects.all()
	serializer_class = PostUpdateCreateSeralizer
	lookup_field = 'slug'

	def perform_update(self, serializer):
		serializer.save(modified_by=self.request.user)
```
