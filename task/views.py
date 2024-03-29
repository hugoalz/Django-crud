from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.

def home(request):
    return render(request, 'home.html')

#   modulo para registrase en la base de datos
def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
        'form': UserCreationForm
    })
        
    else:
        if request.POST['password1'] == request.POST['password2']:
            # register user
            try:
                user = User.objects.create_user(username= request.POST['username'], password= request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {
                'form': UserCreationForm,
                'error': "Este usuario ya existe"
                })  
        return render(request, 'signup.html', {
                'form': UserCreationForm,
                'error': "Password no coinciden"
                })   

@login_required    
def tasks(request):
    # de esta forma te trae todos los usuarios con tarea
   # tasks = Task.objects.all()
   
   # de esta forma te trae la consulta de solamente del usuaeio logeado
    tasks = Task.objects.filter(user= request.user, datecomplete__isnull= True)
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user= request.user, datecomplete__isnull= False).order_by('-datecomplete')
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def tasks_detail(request, task_id):
   if request.method == 'GET':
        # con el get_object_or_404 no tumba el servidor en caso de no encontrar la tarea 
        task = get_object_or_404(Task, pk= task_id, user= request.user)
        form = TaskForm(instance= task)
        return render(request, 'task_detail.html', {'task': task, 'form': form})
   else:
        try:
            task = get_object_or_404(Task, pk= task_id, user= request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {'task': task, 'form': form, 'error': "Ha ocurrido un error al actualizar"})

@login_required            
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk= task_id, user= request.user)
    if request.method == 'POST':
        task.datecomplete = timezone.now()
        task.save()
        return redirect('tasks')

@login_required 
def delete_task(request, task_id):
     task = get_object_or_404(Task, pk= task_id, user= request.user)
     if request.method == 'POST':
        task.delete()
        return redirect('tasks')

@login_required    
def created_tarea(request):
    if request.method == 'GET':
         return  render(request, 'created-task.html', {
        'form': TaskForm
        })
    else:
        try:
            form = TaskForm(request.POST)
            # manda solo los datos establecidos y no todos los del formulario
            new_task = form.save(commit=False)
            # la clase Task viene con user por eso se agrega a la tarea el user que genera la tarea
            new_task.user = request.user
            # Se manda a gurdar la tarea a la base de datos 
            new_task.save()
            # se redireciona la pagina despues de crear la tarea 
            return redirect('tasks')
        except ValueError:
             return  render(request, 'created-task.html', {
                'form': TaskForm,
                'error': "Favor de ingresar los datos correctamente"
                })
        
        

# modulo para cerrar sesion y mandar al home
@login_required
def signout(request):
    logout(request)
    return redirect('home')   

# modulo para iniciar sesion autentificando con la base de datos
def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
        'form': AuthenticationForm
    })
    else:
        user = authenticate(
            request, username= request.POST['username'], password= request.POST['password']
        )    
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': "Usuario o contraseñas son incorrectas"
            })
        else:
            login(request, user)
            return redirect('tasks')
        
