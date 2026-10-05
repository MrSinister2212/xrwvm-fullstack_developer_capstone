from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging

from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review

logger = logging.getLogger(__name__)


@csrf_exempt
def login_user(request):
    if request.method != 'POST':
        return JsonResponse({"status": 405, "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"status": 400, "message": "Invalid JSON"}, status=400)

    username = data.get('userName', '')
    password = data.get('password', '')
    user = authenticate(username=username, password=password)

    if user is not None:
        login(request, user)
        return JsonResponse({
            "userName": username,
            "status": "Authenticated",
            "firstName": user.first_name,
            "lastName": user.last_name,
        })

    return JsonResponse({
        "userName": username,
        "status": "Unauthenticated",
    }, status=401)


@csrf_exempt
def logout_request(request):
    logout(request)
    return JsonResponse({"userName": "", "status": "Logged out"})


@csrf_exempt
def registration(request):
    if request.method != 'POST':
        return JsonResponse({"status": 405, "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"status": 400, "message": "Invalid JSON"}, status=400)

    username = data.get('userName', '').strip()
    password = data.get('password', '')
    first_name = data.get('firstName', '').strip()
    last_name = data.get('lastName', '').strip()
    email = data.get('email', '').strip()

    if not all([username, password, first_name, last_name, email]):
        return JsonResponse({"status": 400, "message": "All fields are required"}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({"userName": username, "error": "Already Registered"}, status=409)

    user = User.objects.create_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        password=password,
        email=email,
    )
    login(request, user)
    return JsonResponse({
        "userName": username,
        "status": "Authenticated",
        "firstName": first_name,
        "lastName": last_name,
    })


def get_dealerships(request, state="All"):
    endpoint = "/fetchDealers" if state == "All" else f"/fetchDealers/{state}"
    dealerships = get_request(endpoint)
    if dealerships is None:
        dealerships = []
    return JsonResponse({"status": 200, "dealers": dealerships})


def get_dealer_reviews(request, dealer_id):
    if not dealer_id:
        return JsonResponse({"status": 400, "message": "Bad Request"}, status=400)

    reviews = get_request(f"/fetchReviews/dealer/{dealer_id}") or []
    for review in reviews:
        response = analyze_review_sentiments(review.get('review', ''))
        review['sentiment'] = response.get('sentiment', 'neutral')

    return JsonResponse({"status": 200, "reviews": reviews})


def get_dealer_details(request, dealer_id):
    if not dealer_id:
        return JsonResponse({"status": 400, "message": "Bad Request"}, status=400)

    dealership = get_request(f"/fetchDealer/{dealer_id}") or []
    return JsonResponse({"status": 200, "dealer": dealership})


@csrf_exempt
def add_review(request):
    if request.method != 'POST':
        return JsonResponse({"status": 405, "message": "Method not allowed"}, status=405)

    if request.user.is_anonymous:
        return JsonResponse({"status": 403, "message": "Unauthorized"}, status=403)

    try:
        data = json.loads(request.body or "{}")
        result = post_review(data)
        return JsonResponse({"status": 200, "result": result})
    except Exception as exc:
        logger.exception("Error posting review: %s", exc)
        return JsonResponse({"status": 401, "message": "Error in posting review"}, status=401)


def get_cars(request):
    if CarMake.objects.count() == 0:
        initiate()

    cars = [
        {"CarModel": model.name, "CarMake": model.car_make.name}
        for model in CarModel.objects.select_related('car_make').all()
    ]
    return JsonResponse({"CarModels": cars})
