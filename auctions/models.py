from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    CategoryName = models.CharField(max_length=64, null=False)

    def __str__(self):
        return f"ID-{self.id}:{self.CategoryName}"


class Bid(models.Model):
    bid = models.FloatField(default=0.00)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
   

class CreateListing(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True,null=True)
    title = models.CharField(max_length=64,null=False)
    description = models.TextField()
    summary = models.CharField(max_length=100,null=True)
    imgUrl = models.CharField(max_length=900)
    price = models.ForeignKey(Bid, on_delete=models.CASCADE, blank=True,null=True)
    
    IsActive = models.BooleanField(default=True)
    Category = models.ForeignKey(Category,on_delete=models.CASCADE,null=False)
    watchlist = models.ManyToManyField(User,related_name="listingWatchlist")
    def __str__(self):
        return f"{self.id}-{self.title}"
    
    
class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True,null=True)
    listing = models.ForeignKey(CreateListing, on_delete=models.CASCADE, blank=True,null=True)
    message  = models.CharField(max_length=200)
    
    def __str__(self):
        return f"{self.author} comment on {self.listing}"
     
     
