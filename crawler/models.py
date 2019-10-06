from __future__ import unicode_literals


from djongo import models
from django import forms
import json
from django.contrib.postgres.fields import ArrayField


# Create your models here.
class Student(models.Model): # Collection name => "DB name_class name"
    # Auto updated when data is inserted
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    # Auto updated when data is altered
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    # Documents
    name = models.CharField(max_length=20, null=True)
    age = models.IntegerField(default=10, null=True)
    roll_number = models.CharField(max_length=20, null=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.TextField()
    date = models.DateField()
    url = models.TextField()
    content = models.TextField()

    class Meta:
        abstract = True


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'date', 'url', 'content')


class Num(models.Model):
    num = models.IntegerField()
    url = models.TextField()
    class Meta:
        abstract = True


class NumForm(forms.ModelForm):
    class Meta:
        model = Num
        fields = ('num', 'url')

class Url(models.Model):
    url = models.TextField()


class RawData(models.Model):

    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)
    site = models.CharField(max_length=20, null=False)
    board = models.ArrayModelField(model_container=Post, model_form_class=PostForm)
    post_num = models.ArrayModelField(model_container=Num, model_form_class=NumForm)
    #gallery_url = models.ListField(models.CharField(max_length=50, blank=True))

    #stringArr = ArrayField(models.CharField(max_length=10, blank=True),size=8)


    def __str__(self):
        return self.site

    #def post_num(self, x):
     #   self.foo = json.dumps(x)

    #def post_num(self):
     #   return json.loads(self.foo)

