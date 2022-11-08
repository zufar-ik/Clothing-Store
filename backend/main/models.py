from django.db import models


class User(models.Model):
    username = models.CharField(max_length=150, null=True)
    name = models.CharField(max_length=150, null=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=250)
    title = models.CharField(max_length=250)
    slug = models.SlugField()
    img = models.FileField(upload_to='img/category_img/')

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='cate')
    name = models.CharField(max_length=250)
    slug = models.SlugField()
    about = models.TextField()
    img = models.FileField(upload_to='img/product_img/')
    price = models.BigIntegerField()
    price_over = models.BigIntegerField()

    def __str__(self):
        return self.name


class Cart(models.Model):
    tg_id = models.CharField(max_length=250)
    name = models.CharField(max_length=250)
    price = models.BigIntegerField()
    size = models.CharField(max_length=50)
    count = models.IntegerField()

    def __str__(self):
        return self.name
