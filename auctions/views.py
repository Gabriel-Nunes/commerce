from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponseForbidden

from django.shortcuts import render, redirect
from django.urls import reverse
import os
from .models import AuctionListing, User, Bid, Comment, Watchlist
from .forms import AuctionListingForm

from django.contrib import messages
from django.contrib.messages import constants

from django.core.exceptions import ObjectDoesNotExist

def index(request):
    active_listings = AuctionListing.objects.filter(active=True).all()
    
    return render(request, "auctions/index.html", context={'active_listings': active_listings})

@login_required(login_url='auctions/login.html')
def create_listing(request):
    if request.method == "GET":
        return render(request, "auctions/create_listing.html", {
            'form': AuctionListingForm()
        })
    if request.method == "POST":
        form = AuctionListingForm(request.POST, request.FILES)
        if form.is_valid():
            new_listing = form.save(commit=False)
            new_listing.author = request.user
            new_listing.current_price = new_listing.starting_bid
            new_listing.save()
            return redirect(f"/listing_view/{new_listing.id}/")
        for error in form.errors.values():
            messages.add_message(request=request, level=constants.ERROR, message=error)

@login_required(login_url='auctions/login.html')
def edit_listing(request, id):
    if request.method == 'GET':
        new_listing = AuctionListing.objects.get(id=id)
        assert new_listing.author == request.user, HttpResponseForbidden()
        form = AuctionListingForm(initial={
            'product': new_listing.product,
            'photo': new_listing.photo,
            'description': new_listing.description,
            'starting_bid': new_listing.starting_bid
        })
        return render(request, "auctions/edit_listing.html", {'form': form, 'id':id})

    if request.method == 'POST':
        listing = AuctionListing.objects.get(id=id)
        assert listing.author == request.user, HttpResponseForbidden()
        listing.product = request.POST.get('product')
        listing.categorie = request.POST.get('categorie')
        listing.starting_bid = request.POST.get('starting_bid')
        listing.description = request.POST.get('description')
        listing.current_winner = listing.current_winner
        if len(request.FILES) == 0:
            listing.photo = listing.photo
        else:
            os.remove(listing.photo.path)
            listing.photo = request.FILES.get('photo')
        listing.save()
        messages.add_message(request, constants.SUCCESS, message="Listing updated.")
        return redirect(f'/listing_view/{listing.id}/')

def set_bid(request, id):
    if request.method == 'POST':
        bid = request.POST.get('bid')
        listing = AuctionListing.objects.get(id=id)
        if float(bid) <= listing.current_price:
            messages.add_message(request, constants.ERROR, message="Bid has to be greater than current price.")
            return redirect(f'/listing_view/{listing.id}/')
        listing.current_price = bid
        listing.current_winner = request.user
        listing.save()
        messages.add_message(request, constants.SUCCESS, message="Your bid has been placed!")
        return redirect(f"/listing_view/{listing.id}")

def listing_view(request, id):
    listing = AuctionListing.objects.get(id=id)
    comments = Comment.objects.filter(auction_listing=listing).order_by('date')
    try:
        watchlist = Watchlist.objects.get(user=request.user.id)
        if listing in watchlist.auction_listings.all():
            watchlisted = True
        else:
            watchlisted = False
    except ObjectDoesNotExist:
        watchlisted = False

    return render(request, "auctions/view.html", {
        'listing': listing,
        'comments': comments,
        'watchlisted': watchlisted,
    })

def close_auction(request, id):
    if request.method == 'GET':
        listing = AuctionListing.objects.get(id=id)
        if listing.author == request.user and listing.active == True:
            listing.active = False
            listing.save()
            return redirect(f"/listing_view/{listing.id}")

def comment(request, id):
    if request.method == 'POST':
        listing = AuctionListing.objects.get(id=id)
        text = request.POST.get("comment")
        new_comment = Comment()
        new_comment.text = text
        new_comment.auction_listing = listing
        new_comment.author = request.user
        new_comment.save()
        return redirect(f"/listing_view/{listing.id}")

@login_required
def my_wins(request):
    if request.method == 'GET':
        winned_auctions = AuctionListing.objects.filter(active=False, current_winner=request.user)
        return render(request, "auctions/my_wins.html", {'winned_auctions': winned_auctions})

@login_required(login_url='auctions/login.html')
def watchlist(request):
    if request.method == 'GET':
        if not request.GET.get('listing_id'):
            watchlist = Watchlist.objects.get(user=request.user)
            return render(request, "auctions/watchlist.html", {'watchlist': watchlist})

        listing = AuctionListing.objects.get(id=request.GET.get('listing_id'))
        watchlist = Watchlist.objects.filter(user=request.user.id)[0]
        if watchlist:
            # If listing already in watchlist, remove listing from watchlist
            if listing in watchlist.auction_listings.all():
                watchlist.auction_listings.remove(listing)
                watchlist.save()
                return render(request, "auctions/view.html", {
                    'listing': listing,
                    'watchlisted': False,
                })    

            watchlist.auction_listings.add(listing)
            watchlist.save()
            return render(request, "auctions/view.html", {
                'listing': listing,
                'watchlisted': True,
                })
        auction_listings = AuctionListing.objects.filter(id=request.GET.get('listing_id'))
        watchlist = Watchlist.objects.create(user=request.user)
        watchlist.auction_listings.set(auction_listings)
        watchlist.save()
        return render(request, "auctions/view.html", {
                'listing': listing,
                'watchlisted': True,
                })

@login_required(login_url='auctions/login.html')
def view_watchlist(request):
    watchlist = Watchlist.objects.get(user=request.user.id)
    return render(request, 'auctions/watchlist.html', {
        'listings': watchlist.auction_listings.all(),
    })

def categories(request):
    categories = [j for (i, j) in AuctionListing.categories_choices]
    return render(request, 'auctions/categories.html', {
        'categories': categories,
    })

def category_list(request, category: str):
    listings = AuctionListing.objects.filter(categorie=category)
    return render(request, 'auctions/category_view.html', {
        'listings': listings
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
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))

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
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")
