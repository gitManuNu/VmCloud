from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from .models import (
    PlanillaUsuarios as PlU,
    VirtualMachineList as VMlist,
    Discos,
    Redes
    )
import requests

#+--------------------------------------------------------------------------------------+

class PlanillaUsuarios(View):
    template = 'planilla_usuarios.html'
    model1 = PlU
    model2 = VMlist
    model3 = Discos
    model4 = Redes
    
    def get(self, request):
        if 'usuario_id' not in request.session:
            return redirect('/Login/')
        
        usuarios = self.model1.objects.all()
        vms = self.model2.objects.all()
        dsk = self.model3.objects.all()
        ntw = self.model4.objects.all()
        return render(request, self.template,{
            'usuarios': usuarios,
            'count': usuarios.count(),
            'vms': vms,
            'dsk': dsk,
            'ntw': ntw
        })

class GetIp():
    def obtener_ip_usuario(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[-1].strip() 
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def obtener_web_ip(request):
        web_ip = requests.get('http://checkip.amazonaws.com').text.strip()
        return web_ip

class AddData(View):
    template = 'Add_data.html'
    model = PlU
    
    def get(self, request):
        if 'usuario_id' not in request.session:
            return redirect('/Login/')
    
    def post(self, request):
        usuario = request.POST['usuario']
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        email = request.POST['email']
        ip = GetIp.obtener_ip_usuario(request)
        web_ip = GetIp.obtener_web_ip(request)
        clave = request.POST['clave']
        add_data = self.model(usuario=usuario,
                       nombre=nombre,
                       apellido=apellido,
                       email=email,
                       ip=ip,
                       web_ip=web_ip,
                       clave=clave
                       )
        add_data.save()
        
        UsuarioSesion = self.model.objects.get(usuario=usuario, clave=clave)
        request.session['usuario_id'] = UsuarioSesion.id
        request.session['usuario_nombre'] = UsuarioSesion.usuario
        
        return render(request, self.template, {
            'usuario': usuario
        })
        

class DeleteData(View):
    model = PlU
    template = 'Borrando.html'
    
    def get(self, request):
        if 'usuario_id' not in request.session:
            return redirect('/Login/')
        
        try:
            a_borrar = request.GET['user']
            borrado = self.model.objects.get(usuario=f'{a_borrar}')
            borrado.delete()
        except:
            return HttpResponse(f'Ocurrio un error vuelva a intentarlo...')
        return render(request, self.template)