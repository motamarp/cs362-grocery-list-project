from django.http import HttpResponse

def index(request):
    return HttpResponse("tester")

# Create your views here.
