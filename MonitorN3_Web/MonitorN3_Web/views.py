from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.timezone import now

def login_views(request):
    error_message = None  # Inicializa la variable de error
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect("index")
        else:
            error_message = "Usuario o contraseña incorrectos. Vuelva a intentarlo."

    return render(request, "login.html", {"error": error_message})

@login_required(login_url='/login/')
def logout_views(request):
    logout(request)
    return redirect("login")

@login_required(login_url='/login/')
def index(request):
    return render(request, 'index.html')

@login_required(login_url='/login/')
def base_context(request):
    return {'time': now().timestamp()}