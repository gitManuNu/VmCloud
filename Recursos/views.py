from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from Modelos.models import (
    PlanillaUsuarios as PlU,
    VirtualMachineList as VMlist,
    Discos,
    Redes
)
from django.utils import timezone
import datetime
import os
from time import sleep
import subprocess

#+---------------------------------------------------------------+

def CalcularIdDisco(vmname,usuario):
    vmname = f'{usuario}_{vmname}'
    Directorio = os.path.join('C:\\','Users','manuq','VirtualBox VMs',f'{vmname}',f'{vmname}_dk.vdi')
    comando = f'VBoxManage showmediuminfo disk "{Directorio}" | findstr /b "UUID:"'
    ShellResult = subprocess.check_output(comando, shell=True, text=True)
    comando = ShellResult.strip('\n').strip('UUID:').strip(' ')
    return comando

def CalcularValoresDisco(diskid,diskname):
    valores = []
    valores.append(diskid)
    valores.append(diskname)
    
    comando = f'VBoxManage showmediuminfo disk "{diskid}" | findstr /b "Capacity:"'
    ShellResult = subprocess.check_output(comando, shell=True, text=True)
    comando = ShellResult.strip('Capacity:').strip(' ').strip('\n').strip('').strip('MBytes').strip(' ')
    valores.append(comando)
    
    comando = f'VBoxManage showmediuminfo disk "{diskid}" | findstr /b "Size on disk:"'
    ShellResult = subprocess.check_output(comando, shell=True, text=True)
    comando = ShellResult.strip('Size on disk:').strip(' ').strip('\n').strip('').strip('MBytes').strip(' ')
    valores.append(comando)
    
    return valores

def CambiarNombreDisco(so,vmname,usuario):
    if so == 'Windows10_64':
        DiskName = "W10PRO"
    elif so == 'Ubuntu_64':
        DiskName = "Ubuntu"
    NombreDisco = f'{vmname}_dk'
    vmname = f'{usuario}_{vmname}'
    Directorio = os.path.join('C:\\','Users','manuq','VirtualBox VMs',f'{vmname}',f'{DiskName}-disk001.vdi')
    NuevoDir = os.path.join('C:\\','Users','manuq','VirtualBox VMs',f'{vmname}',f'{vmname}_dk.vdi')
    ModifyDisk = f'VBoxManage modifymedium disk "{Directorio}" --move="{NuevoDir}"'
    os.system(ModifyDisk)
    return NombreDisco

def ActualizarEspacioUsado():
    discos = Discos.objects.values_list('diskid', flat=True)
    for disco in discos:
        comando = f'VBoxManage showmediuminfo disk "{disco}" | findstr /b "Size on disk:"'
        ShellResult = subprocess.check_output(comando, shell=True, text=True)
        comando = ShellResult.strip('Size on disk:').strip(' ').strip('\n').strip('').strip('MBytes').strip(' ')
        actualizar = Discos.objects.get(diskid=f'{disco}')
        actualizar.uso = comando
        actualizar.save()

def CrearMaquinaVirtual(vmname,cpus,ram,vram,so,network,usuario):
    if so == 'Windows10_64':
        sistema = "W10PRO.ova"
    elif so == 'Ubuntu_64':
        sistema = "Ubuntu.ova"
        
    vmname = f'{usuario}_{vmname}'
    RutaOva = os.path.join('C:\\','Python','PY_DJANGO','VmCloud',f'{sistema}')
    CrearVm = f'VBoxManage import {RutaOva} --options=importtovdi --vsys=0 --vmname={vmname} --unit=0'
    RecursosVm = f'VBoxManage modifyvm "{vmname}" --cpus {cpus} --memory {ram} --vram {vram}'
    os.system(CrearVm)
    os.system(RecursosVm)
    CalcularId = f'vboxmanage showvminfo "{vmname}" | findstr /b "UUID"'
    ShellResult = subprocess.check_output(CalcularId, shell=True, text=True)
    comando = ShellResult.strip('\n').strip('UUID:').strip(' ')
    
    if network != None:
        netname = Redes.objects.get(id=network).nombre
        AddNtw = f'VBoxManage modifyvm "{vmname}" --nic1=natnetwork --nic-type1=82540EM --cable-connected1=on --nic-boot-prio1=1 --nat-network1="{usuario}_{netname}"'
        os.system(AddNtw)
    
    return comando

def CalcularEstadoVm(vmid):
    comando = f'VBoxManage debugvm {vmid} osdetect'
    try:
        subprocess.check_output(comando, shell=True, text=True)
        comando = 1
    except:
        comando = 0
    return comando

def ActualizarEstadoVm():
    vms = VMlist.objects.values_list('vmid',flat=True)
    for vm in vms:
        estado = CalcularEstadoVm(vm)
        actualizar = VMlist.objects.get(vmid=vm)
        actualizar.estado = estado
        actualizar.save()

#+---------------------------------------------------------------+

DirVBox = os.path.join('C:\\','Program Files','Oracle','VirtualBox')
os.chdir(DirVBox)

class index(View):
    template = 'index.html'
    
    def get(self, request):
        return render(request, self.template)
    
class Recursos(View):
    template = 'VMs.html'
    model1 = VMlist
    model2 = Discos
    model3 = Redes
    model4 = PlU
    
    def get(self, request):
        return HttpResponse('<meta http-equiv="refresh" content="1;/Login/">')
    
    def post(self, request):
        user = request.GET['user']
        url = '/VMCloud/'
        urlusr = f'?user={user}'
        urlVM = f'{url}Add_VM/{urlusr}'
        urlDK = f'{url}Add_Dsk/{urlusr}'
        urlNW = f'{url}Add_NAT/{urlusr}'
        
        ActualizarEspacioUsado()
        ActualizarEstadoVm()
        
        UserId = self.model4.objects.get(usuario=user).id
        
        vms = self.model1.objects.filter(usuario_id=UserId).order_by('fecha')
        dsk = self.model2.objects.filter(usuario_id=UserId).order_by('fecha')
        net = self.model3.objects.filter(usuario_id=UserId).order_by('fecha')
        
        return render(request, self.template,{
            'user':user,
            'vms':vms,
            'dsk':dsk,
            'net':net,
            'urlVM':urlVM,
            'urlDK':urlDK,
            'urlNW':urlNW
        })

class AddVirtualMachines(View):
    template = 'AddVM.html'
    model1 = PlU
    model2 = VMlist
    model3 = Discos
    model4 = Redes
    
    def get(self, request):
        return HttpResponse('<meta http-equiv="refresh" content="1;/Login/">')
    
    def post(self, request):
        usuario = request.GET['user']
        usuario_id = str(self.model1.objects.get(usuario=f'{usuario}').id)
        redes = self.model4.objects.filter(usuario_id=usuario_id)
        try:
            vmname = request.POST['vmname']
            cpus = request.POST['cpus']
            ram = request.POST['ram']
            vram = request.POST['vram']
            so = request.POST['so']
            network = request.POST['network']
            fecha = datetime.datetime.now(tz=timezone.utc)
            
            if network == "NULL":
                network = None
                
            try:
                val_vm_usr = str(self.model2.objects.get(vmname=vmname).usuario_id)
                if val_vm_usr == usuario_id:
                    return HttpResponse(f'El nombre de VM ({vmname}) ya está en uso')
            except:
                pass
            
            vmid = CrearMaquinaVirtual(vmname,cpus,ram,vram,so,network,usuario)
            diskname = CambiarNombreDisco(so,vmname,usuario)
            diskid = CalcularIdDisco(vmname,usuario)
            ValoresDisco = CalcularValoresDisco(diskid,diskname)
            
            grabar = self.model3(
                diskid=ValoresDisco[0],
                nombre=ValoresDisco[1],
                size=ValoresDisco[2],
                uso=ValoresDisco[3],
                usuario_id=usuario_id,
                fecha=fecha
            )
            grabar.save()
            
            grabar = self.model2(
                vmname=vmname,
                cpus=cpus,
                ram=ram,
                vram=vram,
                so=so,
                disco_id=diskid,
                network_id=network,
                fecha=fecha,
                vmid=vmid,
                usuario_id=usuario_id
            )
            grabar.save()
            return HttpResponse('<script>window.close()</script>')
        except:
            return render(request, self.template, {
                'redes':redes
            })

class AddNetwork(View):
    template = 'AddNW.html'
    model1 = PlU
    model2 = Redes
    
    def get(self, request):
        return HttpResponse('<meta http-equiv="refresh" content="1;/Login/">')
    
    def post(self, request):
        try:
            nombre = request.POST['nombre']
            network = request.POST['network']
            try:
                dhcp = request.POST['dhcp']
            except:
                dhcp = 'off'
            usuario = request.GET['user']
            usuario_id = str(self.model1.objects.get(usuario=f'{usuario}').id)
            fecha = datetime.datetime.now(tz=timezone.utc)
            
            NatAdd = f'VBoxManage natnetwork add --enable --netname="{usuario}_{nombre}" --network={network} --dhcp={dhcp} --ipv6=on'
            os.system(NatAdd)
            
            sleep(2)
            
            grabar = self.model2(
                nombre=nombre,
                network=network,
                dhcp=dhcp,
                usuario_id=usuario_id,
                fecha=fecha
            )
            grabar.save()
            return HttpResponse('<script>window.close()</script>')
        except:
            return render(request, self.template)