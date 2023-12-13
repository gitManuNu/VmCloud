from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from .models import (
    PlanillaUsuarios as PlU,
    VirtualMachineList as VMlist,
    Discos,
    Redes
    )
import requests
import json

#+--------------------------------------------------------------------------------------+

class PlanillaUsuarios(View):
    template = 'planilla_usuarios.html'
    model1 = PlU
    model2 = VMlist
    model3 = Discos
    model4 = Redes
    
    def get(self, request):
        return HttpResponse('<meta http-equiv="refresh" content="1;/Login/">')
    
    def post(self, request):
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
    model = PlU
    
    def get(self, request):
        return HttpResponse('ERROR: Page not found!')
    
    def post(self, request):
        usuario = request.POST['usuario']
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        dni = request.POST['dni']
        email = request.POST['email']
        ip = GetIp.obtener_ip_usuario(request)
        web_ip = GetIp.obtener_web_ip(request)
        clave = request.POST['clave']
        add_data = self.model(usuario=usuario,
                       nombre=nombre,
                       apellido=apellido,
                       dni=dni,
                       email=email,
                       ip=ip,
                       web_ip=web_ip,
                       clave=clave
                       )
        add_data.save()
        return HttpResponse(f'Estamos agregando sus datos... <meta http-equiv="refresh" content="1;/Mails/envio_registrado/?user={usuario}">')

class GeoIp(View):
    template = 'geoip.html'
    model = PlU
    redirect = '<meta http-equiv="refresh" content="1;/Login/">'
    
    def get(self, request):
        return HttpResponse(self.redirect)
    
    def post(self, request):
        api_url = "http://ip-api.com/json/"
        parametros = 'status,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as'
        data = {"fields":parametros}
        
        def ip_scraping(ip=""):
            res = requests.get(api_url+ip, data=data)
            api_json_res = json.loads(res.content)
            return api_json_res
        
        usuario = request.GET['user']
        orm = self.model.objects.get(usuario=f'{usuario}').web_ip
        nombre = 'NOMBRE: ' + str(self.model.objects.get(usuario=f'{usuario}').nombre)
        apellido = 'APELLIDO: ' + str(self.model.objects.get(usuario=f'{usuario}').apellido)
        dni = 'DNI: ' + str(self.model.objects.get(usuario=f'{usuario}').dni)
        lan = 'LAN: ' + str(self.model.objects.get(usuario=f'{usuario}').ip)
        ip = orm
        par = parametros.split(",")
        query = []
        query.append(nombre)
        query.append(apellido)
        query.append(dni)
        query.append(lan)
        for x in par:
            titulo = f'{x.upper()}'
            data_ip = f'{ip_scraping(ip)[x]}'
            objeto = f'{titulo}: {data_ip}'
            query.append(objeto)
        return render(request, self.template, {
            'query':query,
            'web_ip':ip,
            'user':usuario,
        })

class DeleteData(View):
    model = PlU
    template = 'Borrando.html'
    
    def get(self, request):
        try:
            a_borrar = request.GET['user']
            borrado = self.model.objects.get(usuario=f'{a_borrar}')
            borrado.delete()
        except:
            return HttpResponse(f'Ocurrio un error vuelva a intentarlo...')
        return render(request, self.template)