from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import *
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect
from django import forms

def index(request):
    Active=CreateListing.objects.filter(IsActive=True ,summary=True)
    category = Category.objects.all()
    return render(request, "auctions/index.html",{
        "listings": Active,
        "category": category,
    })
    
    


class BidForm(forms.Form):
    newBid = forms.FloatField(min_value=0, error_messages={'required': 'Please enter a valid bid amount.'})

def addBid(request, id):
    listing = CreateListing.objects.get(pk=id)
    form = BidForm(request.POST)

    if form.is_valid():
        bid = form.cleaned_data["newBid"]
        current_price = listing.price.bid if listing.price else 0
        starting_price = current_price or 0

        if float(bid) > starting_price:
            updateBid = Bid(user=request.user, bid=float(bid))
            updateBid.save()
            listing.price = updateBid
            listing.save()
            messages.success(request, "Your bid has been placed successfully!")
        else:
            messages.error(request, f"Your bid must be higher than the current price of {starting_price}.")
    else:
        messages.error(request, "Invalid bid amount. Please try again.")

    return HttpResponseRedirect(reverse("listing", args=(id,)))
        


def listing(request, id):
    listing = CreateListing.objects.get(pk=id)
    islistingTrue = request.user in listing.watchlist.all()
    allcomments = Comment.objects.filter(listing=listing)
    isOwner = request.user.username == listing.owner.username
    is_winner = request.user == (listing.price.user if listing.price else None)

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "islistingTrue": islistingTrue,
        "allcomments": allcomments,
        "isOwner": isOwner,
        "is_winner": is_winner
    })

    
    
    

def closeAuction(request, id):
    listing = get_object_or_404(CreateListing, pk=id)

    # Ensure only the owner can close the auction
    if request.user.username == listing.owner.username:
        listing.IsActive = False
        listing.save()
        messages.success(request, "Auction has been successfully closed.")
    else:
        messages.error(request, "You do not have permission to close this auction.")
    
    return redirect('listing', id=listing.id)
    
def displaywatchlist(request):
    user = request.user
    listing =user.listingWatchlist.all()
    return render(request,"auctions/watchlist.html",{
        "watchlist":listing
    } )
    
def addComment(request,id):
    user=request.user
    listingData = CreateListing.objects.get(pk=id)
    message  = request.POST["newComment"]
    
    Comment.objects.create(
        author=user,
        listing=listingData,
        message=message,
    )
    return HttpResponseRedirect(reverse("listing", args=(id,)))
    
    
    
def removeWatchlist(request,id):
    listing = CreateListing.objects.get(pk=id)
    user = request.user
    listing.watchlist.remove(user)
    return HttpResponseRedirect(reverse("listing", args=(id,)))


def addWatchlist(request,id):
    listing = CreateListing.objects.get(pk=id)
    user = request.user
    listing.watchlist.add(user)
    return HttpResponseRedirect(reverse("listing", args=(id,)))



def displeyCtegory(request):
        
    if request.method == "POST":
        selected_category = request.POST.get("category")  # Use get method to handle None case
        if selected_category == "Category":  # No category selected
            Active = CreateListing.objects.filter(IsActive=True, summary=True)
        else:
            category = Category.objects.get(CategoryName=selected_category)
            Active = CreateListing.objects.filter(IsActive=True, Category=category)
        category = Category.objects.all()
        return render(request, "auctions/index.html", {
            "listings": Active,
            "category": category,
        })


def Create_Listing(request):
    if request.method == "GET":
        category = Category.objects.all()
        return render(request, "auctions/create_listing.html", {"category": category})
    else:
        title = request.POST["title"]
        description = request.POST["description"]
        imgUrl = request.POST["imgurl"]
        price = request.POST["price"]  # Convert price to float
        category_id = request.POST["category"]
        category = Category.objects.get(pk=category_id)
        user = request.user
        
        bid_instance = Bid(
                bid=float(price),
                user=user
            )
        bid_instance.save()
        try:
            CreateListing.objects.create(
                owner=request.user,
                title=title,
                description=description,
                imgUrl=imgUrl,
                price=bid_instance,
                Category=category
                
            )
            return HttpResponseRedirect(reverse("index"))
        except IntegrityError:
            return render(request, "auctions/create_listing.html", {
                "message": "Listing with this title already exists."
            })
        except Exception as e:
            return render(request, "auctions/create_listing.html", {
                "message": str(e)
            })




def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
