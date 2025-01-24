from django.contrib import admin
from auctions.models import User,CreateListing,Category,Comment,Bid

# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(CreateListing)
admin.site.register(Comment)
admin.site.register(Bid)