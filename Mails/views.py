from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.mail import send_mail
from Modelos.models import (PlanillaUsuarios as PlU, TokenRecuperacionTemp as TrTemp)
from VmCloud.settings import EMAIL_HOST_USER as frommail, HOST_USADO as host
import uuid
import datetime
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.views import View

#+------------------------------------------------------------------------------------+

class AdminEnvios(View):
    template = 'envios.html'
    model = PlU
    
    def get(self, request):
        usuario = request.GET['user']
        usermail = str(self.model.objects.get(usuario=f'{usuario}').email)
        return render(request, self.template, {
            'usermail': usermail,
        })

class DatosEnvio(View):
    template = 'datos_envio.html'
    
    def get(self, request):
        return HttpResponse('ERROR: PAGE NOT FOUND')
    
    def post(self, request):
        usermail = request.POST['email']
        header = request.POST['asunto']
        body = request.POST['mensaje']
        try:
            send_mail(header,body,frommail,[usermail])
            envio = True
        except:
            envio = False
        return render(request, self.template, {
            'usermail': usermail,
            'header': header,
            'body': body,
            'envio':envio,
            })

class WelcomeMail(View):
    template = 'registrado.html'
    model = PlU
    
    def get(self, request):
        if 'usuario_id' not in request.session:
            return redirect('/Login/')
        
        user = request.GET['user']
        usermail = str(self.model.objects.get(usuario=f'{user}').email)
        nombre = str(self.model.objects.get(usuario=f'{user}').nombre)
        apellido = str(self.model.objects.get(usuario=f'{user}').apellido)
        clave = str(self.model.objects.get(usuario=f'{user}').clave)
        try:
            html = render_to_string(self.template, {
                'nombre': nombre,
                'apellido': apellido,
                'user': user,
                'clave': clave
            })
            email = EmailMessage('VmCloud: Usuario dado de alta satisfactoriamente.', 
                                html, 
                                frommail, 
                                to=[usermail]
                                )
            email.content_subtype = "html"
            email.send()
            return HttpResponse('<script src="/static/AlertaMailEnviado.js"></script>')
        except:
            return HttpResponse('<script src="/static/AlertaMailFallo.js"></script>')

class RebootEmail(View):
    template = 'reboot_psw_email.html'
    model = PlU
    
    def get(self, request):
        return render(request, self.template)
    
    def post(self, request):
        email = request.POST['email']
        try:
            val_eml = str(self.model.objects.get(email=f'{email}').email)
        except:
            val_eml = '0'
        return render(request, self.template,{
            'val_eml':val_eml
        })

class RebootSend(View):
    template = 'cuerpo_reboot.html'
    model_plu = PlU
    model_token = TrTemp
    
    def get(self, request):
        usermail = request.GET['email']
        usuario = str(self.model_plu.objects.get(email=f'{usermail}').usuario)
        cod_temp = uuid.uuid4()
        add_token = self.model_token(
            usuario = usuario,
            token = cod_temp,
            fecha_gen = datetime.datetime.now(),
            usado = 0
        )
        add_token.save()
        try:
            html = render_to_string(self.template,{
                'cod_temp':cod_temp,
                'host':host
            })
            email = EmailMessage('Recuperacion de contraseñas...', 
                                html, 
                                frommail, 
                                to=[usermail]
                                )
            email.content_subtype = "html"
            email.send()
            return HttpResponse('<script src="/static/AlertaMailEnviado.js"></script>')
        except:
            return HttpResponse('<script src="/static/AlertaMailFallo.js"></script>')