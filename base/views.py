from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .models import Room, Topic
from .forms import RoomForm
from django.contrib import messages


# Create your views here.
def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username or password is incorrect")

    context = {}
    return render(request, 'base/login_signup.html', context)


def logout_user(request):
    request.session.flush()
    return redirect('home')


def home(request):
    q = request.GET.get('q')

    if q:
        rooms = Room.objects.filter(
            Q(topic__name__icontains=q)
            | Q(name__icontains=q)
            | Q(description__icontains=q)
        )
    else:
        rooms = Room.objects.all()

    room_count = rooms.count()
    topics = Topic.objects.all()
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    context = {'room': room}
    return render(request, 'base/room.html', context)


@login_required(login_url='login')
def create_room(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)


def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)


def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('home')

    context = {'obj': room}
    return render(request, 'base/delete.html', context)