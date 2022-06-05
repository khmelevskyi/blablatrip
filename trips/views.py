from django.shortcuts import render, redirect
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Trip, City
from .forms import TripForm, UpdateTripForm
from users.models import Passenger, Driver, Profile
from .filters import TripFilter


def add_trip(request):
    userDriver = Driver.objects.filter(user=request.user)
    if len(userDriver) == 0:
        messages.success(
            request, ('У вас наразі немає водіїв. Додайте нового, щоб продовжити.'))
        return redirect('add-driver', -1)
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = TripForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                tripPK = form.save().pk
                trip = Trip.objects.get(pk=tripPK)
                trip.places_left = trip.num_of_places
                trip.save()
                return redirect('trip-details', tripPK)
        else:
            form = TripForm(request.user)
        return render(request, 'trips/add_trip.html', {'form': form})
    else:
        messages.success(
            request, ('Потрібно увійти, щоб додати поїздку.'))
        return redirect('login')


def my_trips(request):
    if request.user.is_authenticated:
        tripsAsPassenger = Trip.objects.filter(
            passengers__user=request.user).order_by('start_date_and_time')
        tripsAsDriver = Trip.objects.filter(
            driver__user=request.user).order_by('start_date_and_time')
        user_profiles = Profile.get_user_profiles_count_str(request.user)
        if len(tripsAsPassenger | tripsAsDriver) > 0:
            return render(request, 'trips/my_trips.html',
                          {
                              'tripsAsPassenger': tripsAsPassenger if len(Trip.objects.filter(passengers__user=request.user)) > 0 else None,
                              'tripsAsDriver': tripsAsDriver if len(Trip.objects.filter(driver__user=request.user)) > 0 else None,
                              'user_profiles': user_profiles
                          })
        else:
            messages.success(
                request, ('Здається, наразі у Вас немає поїздок.'))
            return render(request, 'trips/my_trips.html', {'tripsAsPassenger': None, 'tripsAsDriver': None, 'user_profiles': None})
    else:
        messages.success(
            request, ('Потрібно увійти, щоб побачити свої поїздки.'))
        return redirect('login')


def trip_free_place(request, trip_id):
    if request.user.is_authenticated:
        trip = Trip.objects.get(pk=trip_id)
        if request.method == "POST":
            if request.POST.get('deleteUserPassenger'):
                trip.passengers.remove(request.POST.get('deleteUserPassenger'))
                trip.places_left += 1
                trip.save()
                messages.success(request, ("Місце було успішно звільнене"))
                return redirect('my-trips')
        else:
            if len(trip.passengers.all().filter(user=request.user)) <= 0:
                messages.success(
                    request, ('You are not holding place in this trip'))
                return redirect('my-trips')
            elif len(trip.passengers.all().filter(user=request.user)) == 1:
                trip.passengers.remove(
                    trip.passengers.all().filter(user=request.user)[0])
                trip.places_left += 1
                trip.save()
                messages.success(request, ("Місце було успішно звільнене"))
                return redirect('my-trips')
            else:
                activePassengers = trip.passengers.all()
                userPassengers = Passenger.objects.filter(
                    user=request.user) & activePassengers
                return render(request, 'trips/trip_details.html', {
                    'trip': trip,
                    'passengers': activePassengers,
                    'userPassengers': userPassengers,
                    'deleteUserPassanger': True
                })
    else:
        messages.success(
            request, ('Потрібно увійти, щоб звільнити місце'))
        return redirect('login')


def delete_trip(request, trip_id):
    if request.user.is_authenticated:
        trip = Trip.objects.get(pk=trip_id)
        if trip.driver.user == request.user:
            trip.delete()
            messages.success(
                request, ('Поїздка була успішно видалена'))
            return redirect('my-trips')
        else:
            messages.success(
                request, ('Ця поїздка не належить Вам!'))
            return redirect('my-trips')
    else:
        messages.success(
            request, ('Потрібно увійти, щоб видалити поїздку'))
        return redirect('login')


def trip_details(request, trip_id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            trip = Trip.objects.get(pk=trip_id)
            activePassengers = trip.passengers.all()
            userPassengers = Passenger.objects.filter(
                user=request.user)
            userPassengers = userPassengers.exclude(id__in=activePassengers)
            if request.POST.get('userPassenger'):
                trip.passengers.add(request.POST.get('userPassenger'))
                trip = Trip.objects.get(pk=trip_id)
                trip.places_left = trip.places_left - 1
                trip.save()
                messages.success(request, ("Пасажир був успішно доданий"))
                return render(request, 'trips/trip_details.html', {'trip': trip, 'passengers': activePassengers})
            else:
                if len(userPassengers) == 0:
                    return redirect('add-passenger', trip_id)
                else:
                    messages.success(request, ("Виберіть пасажира"))
                    return render(request, 'trips/trip_details.html', {
                        'trip': trip,
                        'passengers': activePassengers,
                        'userPassengers': userPassengers,
                        'showSelection': True
                    })
        else:
            messages.success(
                request, ('Потрібно увійти, щоб забронювати місце'))
            return redirect('login')
    else:
        trip = Trip.objects.get(pk=trip_id)
        activePassengers = trip.passengers.all()
        return render(request, 'trips/trip_details.html', {'trip': trip, 'passengers': activePassengers})


def active_trips(request):
    trips = Trip.objects.filter(
        start_date_and_time__gte=timezone.now(), places_left__gt=0).order_by('start_date_and_time')
    tripFilter = TripFilter(request.GET, queryset=trips)
    trips = tripFilter.qs
    paginator = Paginator(trips, 2)
    page = request.GET.get('page')
    tripsForPage = paginator.get_page(page)
    all_users_profiles = Profile.get_all_users_count_str()
    all_active_trips = Trip.get_all_trips_count_str()
    if request.GET.get('showFilter') == 'Filter':
        return render(request, 'trips/active_trips.html', {'trips': trips, 'filter': tripFilter, 'tripsForPage': tripsForPage, 'showFilter': True})
    return render(
        request,
        'trips/active_trips.html',
        {'trips': trips, 'filter': tripFilter, 'tripsForPage': tripsForPage, 'all_users_profiles': all_users_profiles, 'all_active_trips': all_active_trips}
    )


def update_trip(request, trip_id):
    if request.user.is_authenticated:
        trip = Trip.objects.get(pk=trip_id)
        if trip.driver.user == request.user:
            if request.method == 'POST':
                form = UpdateTripForm(
                    request.user, request.POST, instance=trip)
                if form.is_valid():
                    form.save()
                    return redirect('trip-details', trip_id)
            else:
                form = UpdateTripForm(request.user, instance=trip)
            return render(request, 'trips/update_trip.html', {'trip': trip, 'form': form})
        else:
            messages.success(
                request, ('Ця поїздка не належить Вам!'))
            return redirect('my-trips')
    else:
        messages.success(
            request, ('Потрібно увійти, щоб оновити дані про поїздку'))
        return redirect('login')


def home(request):
    return render(request, 'trips/home.html', {})


def load_cities(request):
    country_id = request.GET.get('country_id')
    if country_id == '':
        cities = City.objects.none()
        return render(request, 'trips/city_ddl.html', {'cities': cities})
    else:
        cities = City.objects.filter(country_id=country_id)
        return render(request, 'trips/city_ddl.html', {'cities': cities})
