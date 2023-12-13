from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from Modelos.models import (
    PlanillaUsuarios as PlU, 
    TokenRecuperacionTemp as TrTemp
)

#+-------------------------------------------------------------------------------+

class Login(View):
    template = 'Login.html'
    model = PlU
    
    def get(self, request):
        return render(request, self.template)
    
    def post(self, request):
        usuario = request.POST['usuario']
        clave = request.POST['clave']
        try:
            val_psw = str(self.model.objects.get(usuario=f'{usuario}').clave)
        except:
            val_psw = ''
        return render(request, self.template, {
            'clave': clave,
            'val_psw': val_psw,
            'usuario':usuario
        })

class Register(View):
    template = 'Register.html'
    model = PlU
    
    def get(self, request):
        return render(request, self.template)
    
    def post(self, request):
        usuario = request.POST['usuario']
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        dni = request.POST['dni']
        email = request.POST['email']
        clave = request.POST['clave']
        clave1 = request.POST['clave1']
        try:
            val_usr = str(self.model.objects.get(usuario=f'{usuario}').usuario)
        except:
            val_usr = '0'
        try:
            val_eml = str(self.model.objects.get(email=f'{email}').email)
        except:
            val_eml = '0'
        try:
            val_dni = str(self.model.objects.get(dni=f'{dni}').dni)
        except:
            val_dni = '0'
        return render(request, self.template, {
            'usuario': usuario,
            'nombre': nombre,
            'apellido':apellido,
            'dni':dni,
            'email':email,
            'clave':clave,
            'clave1':clave1,
            'val_usr':val_usr,
            'val_eml':val_eml,
            'val_dni':val_dni,
            'error': '1'
        })

class RebootPass(View):
    template = 'reboot_psw.html'
    model_plu = PlU
    model_token = TrTemp
    
    def get(self, request):
        return render(request, self.template)
    
    def post(self, request):
        token = request.GET['user']
        usuario = self.model_token.objects.get(token=f'{token}').usuario
        caducado = self.model_token.objects.get(token=f'{token}').usado
        if caducado != 1:
            clave_new = request.POST['clave_new']
            clave_conf = request.POST['clave_conf']
            if clave_new == clave_conf:
                cambio = self.model_plu.objects.get(usuario=f'{usuario}')
                cambio.clave = clave_conf
                cambio.save()
                expired = self.model_token.objects.get(token=f'{token}')
                expired.usado = 1
                expired.save()
            return render(request, self.template,{
                'clave_new':clave_new,
                'clave_conf':clave_conf,
                'usuario':usuario
            })
        else:
            return HttpResponse('Codigo de restablecimiento caducado')
        
class GeoIpLogin(View):
    template = 'GeoIpLogin.html'
    model = PlU
    
    def get(self, request):
        return render(request, self.template)
    
    def post(self, request):
        usuario = 'admin'
        clave = request.POST['clave']
        user_ip = request.GET['user']
        try:
            val_psw = str(self.model.objects.get(usuario=f'{usuario}').clave)
        except:
            val_psw = ''
        return render(request, self.template, {
            'clave': clave,
            'val_psw': val_psw,
            'usuario':user_ip
        })