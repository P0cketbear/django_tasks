from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm
from django.contrib import messages


# Create your views here.
def login_page(request):

    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username or password is incorrect")

    context = {'page': page}
    return render(request, 'base/login_signup.html', context)


def logout_user(request):
    request.session.flush()
    return redirect('home')


def register_user(request):

    if request.user.is_authenticated:
        return redirect('home')
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if User.objects.filter(username=request.POST.get('username').lower()).exists():
            messages.error(request, "Username is taken")
            return redirect('register')

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/login_signup.html', context)


def home(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)
    ).order_by('-updated')

    messages = Message.objects.filter(Q(room__topic__name__icontains=q)).order_by(
        '-created'
    )

    room_count = rooms.count()
    topics = Topic.objects.all()
    context = {
        'rooms': rooms,
        'topics': topics,
        'room_count': room_count,
        'room_messages': messages,
    }
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()

    if request.method == "POST":
        Message.objects.create(
            user=request.user, room=room, body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {
        'participants': participants,
        'room': room,
        'room_messages': messages,
    }
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


@login_required(login_url='login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    if room.host != request.user:
        return redirect('home')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    if room.host != request.user:
        return redirect('home')

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    context = {'obj': room}
    return render(request, 'base/delete.html', context)


@login_required(login_url='login')
def delete_message(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return redirect('room', pk=message.room.id)

    if request.method == 'POST':
        message.delete()
        return redirect('room', pk=message.room.id)

    context = {'obj': message}
    return render(request, 'base/delete.html', context)
