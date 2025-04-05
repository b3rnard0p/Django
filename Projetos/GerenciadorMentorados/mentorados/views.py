from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from .models import Mentorados, Navigators, DisponibilidadedeHorarios,Reuniao, Tarefa, Upload
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime
from datetime import timedelta
from .auth import valida_token
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@login_required
def mentorados(request): 
  if request.method == 'GET':
    navigators =  Navigators.objects.filter(user=request.user)
    mentorados = Mentorados.objects.filter(user=request.user)
    
    estagios_flat = [i[1] for i in Mentorados.estagio_choices]
    qtd_estagios = []
    for i, j in Mentorados.estagio_choices:
      x = Mentorados.objects.filter(estagio=i).filter(user=request.user).count()
      qtd_estagios.append(x)
    
    return render(request, 'mentorados.html', {'estagios': Mentorados.estagio_choices, 'navigators': navigators, 'mentorados':mentorados, 'estagios_flat': estagios_flat, 'qtd_estagios': qtd_estagios,})

  elif request.method == 'POST':
        nome = request.POST.get('nome')
        foto = request.FILES.get('foto')
        estagio = request.POST.get("estagio")
        navigator = request.POST.get('navigator')
        
        mentorado = Mentorados(
          nome=nome,
          foto=foto,
          estagio=estagio,
          navigator_id=navigator,
          user=request.user
       )
        
        mentorado.save()
        
        messages.add_message(request, constants.SUCCESS, 'Mentorado cadastrado com sucesso!')
        return redirect('mentorados')
      
@login_required
def reunioes(request):
    if request.method == 'GET':
        reunioes = Reuniao.objects.filter(
          data__mentor=request.user,
        )
        return render(request, 'reunioes.html', {'reunioes': reunioes})
    
    elif request.method == 'POST':
        data_str = request.POST.get('data')
        try:
            data_inicial = datetime.strptime(data_str, '%Y-%m-%dT%H:%M')
            
            conflitos = DisponibilidadedeHorarios.objects.filter(
                mentor=request.user,
                data_inicial__lt=data_inicial + timedelta(minutes=50),
                data_inicial__gte=data_inicial - timedelta(minutes=50),
                agendado=False
            )
            
            if conflitos.exists():
                messages.error(request, 'Já existe uma reunião nesse horário ou muito próxima!')
                return redirect('reunioes')
            
            novo_horario = DisponibilidadedeHorarios(
                data_inicial=data_inicial,
                mentor=request.user
            )
            novo_horario.save()
            
            messages.success(request, 'Horário disponível cadastrado com sucesso!')
            return redirect('reunioes')
            
        except ValueError:
            messages.error(request, 'Formato de data/horário inválido!')
            return redirect('reunioes')
          
def auth(request):
    if request.method == 'GET':
        return render(request, 'auth_mentorado.html')
    elif request.method == 'POST':
        token = request.POST.get('token')
        
        if not Mentorados.objects.filter(token=token).exists():
            messages.add_message(request, constants.ERROR, 'Token inválido!')
            return redirect('auth_mentorado')
        response = redirect('escolher_dia')
        response.set_cookie('auth_token', token, max_age=3600)
        return response
      
from django.utils import timezone

def escolher_dia(request):
    if not valida_token(request.COOKIES.get('auth_token')):
        return redirect('auth_mentorado')
  
    if request.method == 'GET':
        mentorado = valida_token(request.COOKIES.get('auth_token'))
        disponibilidades = DisponibilidadedeHorarios.objects.filter(
            data_inicial__gte=timezone.now(),
            agendado=False,
            mentor=mentorado.user
        )
        
        horarios_formatados = [
            {
                'dia_semana': data.data_inicial.strftime('%A'), 
                'mes': data.data_inicial.strftime('%B'), 
                'data_completa': data.data_inicial.strftime('%d-%m-%Y'),
                'id': data.id 
            }
            for data in disponibilidades
        ]
        
        return render(request, 'escolher_dia.html', {'horarios': horarios_formatados})
      
      
def agendar_reuniao(request):
    if not valida_token(request.COOKIES.get('auth_token')):
        return redirect('auth_mentorado')
    
    mentorado = valida_token(request.COOKIES.get('auth_token'))
    
    if request.method == 'GET':
            data = request.GET.get('data')
            data = datetime.strptime(data, '%d-%m-%Y')
            horarios = DisponibilidadedeHorarios.objects.filter(
                data_inicial__gte=data,
                data_inicial__lt=data + timedelta(days=1),
                agendado=False,
                mentor=mentorado.user
            )
            
            return render(request, 'agendar_reuniao.html', {
                'horarios': horarios,
                'tags': Reuniao.tag_choices
            })
            
    else:
            horario_id = request.POST.get('horario')
            tag = request.POST.get('tag')
            descricao = request.POST.get("descricao")
            
            reuniao = Reuniao(
                data_id=horario_id,
                mentorado=mentorado,
                tag=tag,
                descricao=descricao
            )
            reuniao.save()

            horario = DisponibilidadedeHorarios.objects.get(id=horario_id)
            horario.agendado = True
            horario.save()

            messages.add_message(request, constants.SUCCESS, 'Reunião agendada com sucesso.')
            return redirect('escolher_dia')
        
def tarefa(request, id):
    mentorado = Mentorados.objects.get(id=id)
    if mentorado.user != request.user:
        raise Http404()
    
    if request.method == 'GET':
        tarefas = Tarefa.objects.filter(mentorado=mentorado)
        videos = Upload.objects.filter(mentorado=mentorado)
        return render(request, 'tarefa.html', {'mentorado': mentorado, 'tarefas': tarefas, 'videos': videos})
    else:
        tarefa = request.POST.get('tarefa')
        
        tarefa = Tarefa(
            mentorado=mentorado,
            tarefa=tarefa,
        )
        tarefa.save()
        
        return redirect(f'/mentorados/tarefa/{id}')
    
def upload(request, id):
    mentorado = Mentorados.objects.get(id=id)
    if mentorado.user != request.user:
        raise Http404()
    video = request.FILES.get('video')
    upload = Upload(
        mentorado=mentorado,
        video=video
    )
    upload.save()
    return redirect(f'/mentorados/tarefa/{id}')
        
def tarefa_mentorado(request):
    mentorado = valida_token(request.COOKIES.get('auth_token'))
    if not mentorado:
        return redirect('auth_mentorado')
    
    if request.method == 'GET':
        videos = Upload.objects.filter(mentorado=mentorado)
        tarefas = Tarefa.objects.filter(mentorado=mentorado)
        return render(request, 'tarefa_mentorado.html', {'mentorado': mentorado, 'videos': videos, 'tarefas': tarefas})
    

@csrf_exempt
def tarefa_alterar(request, id):
    mentorado = valida_token(request.COOKIES.get('auth_token'))
    if not mentorado:
        return redirect('auth_mentorado')

    tarefa = Tarefa.objects.get(id=id)
    if mentorado != tarefa.mentorado:
        raise Http404()
    tarefa.realizada = not tarefa.realizada
    tarefa.save()

    return HttpResponse('teste')