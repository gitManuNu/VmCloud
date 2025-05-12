from django.shortcuts import render, redirect
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
        if 'usuario_id' not in request.session:
            return redirect('/Login/')
        
        usuario = request.session.get('usuario_nombre')
        
        url = '/VMCloud/'
        urlVM = f'{url}Add_VM/'
        urlDK = f'{url}Add_Dsk/'
        urlNW = f'{url}Add_NAT/'
        
        ActualizarEspacioUsado()
        ActualizarEstadoVm()
        
        DatosUsuario = self.model4.objects.get(usuario=usuario)
        UserId = DatosUsuario.id
        UserName = DatosUsuario.nombre
        UserLname = DatosUsuario.apellido
        bienvenida = f'{UserName} {UserLname}'
        
        vms = self.model1.objects.filter(usuario_id=UserId).order_by('fecha')
        dsk = self.model2.objects.filter(usuario_id=UserId).order_by('fecha')
        net = self.model3.objects.filter(usuario_id=UserId).order_by('fecha')
        
        return render(request, self.template,{
            'user':usuario,
            'vms':vms,
            'dsk':dsk,
            'net':net,
            'urlVM':urlVM,
            'urlDK':urlDK,
            'urlNW':urlNW,
            'wlcm':bienvenida
        })

class AddVirtualMachines(View):
    template = 'AddVM.html'
    model1 = PlU
    model2 = VMlist
    model3 = Discos
    model4 = Redes
    
    def dispatch(self, request, *args, **kwargs):
        if 'usuario_id' not in request.session:
            return redirect('/Login/')
        
        self.usuario = request.session.get('usuario_nombre')
        
        self.usuario_id = str(self.model1.objects.get(usuario=f'{self.usuario}').id)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        redes = self.model4.objects.filter(usuario_id=self.usuario_id)
        return render(request, self.template, {
            'redes':redes
        })
        
    def post(self, request):
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
            val_vm_usr = str(self.model2.objects.get(vmname=vmname, usuario_id=self.usuario_id).usuario_id)
            if val_vm_usr == self.usuario_id:
                return HttpResponse(
                    f"""
                    <script>
                        window.alert('Ya usaste el nombre [{vmname}] para una VM.')
                        window.location.replace('/VMCloud/Resources/')
                    </script>
                    """
                )
        except:
            pass
            
        vmid = CrearMaquinaVirtual(vmname,cpus,ram,vram,so,network,self.usuario)
        diskname = CambiarNombreDisco(so,vmname,self.usuario)
        diskid = CalcularIdDisco(vmname,self.usuario)
        ValoresDisco = CalcularValoresDisco(diskid,diskname)
            
        grabar = self.model3(
            diskid=ValoresDisco[0],
            nombre=ValoresDisco[1],
            size=ValoresDisco[2],
            uso=ValoresDisco[3],
            usuario_id=self.usuario_id,
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
            usuario_id=self.usuario_id
        )
        grabar.save()
        return HttpResponse('<script src="/static/AltaRecurso.js"></script>')

class AddNetwork(View):
    template = 'AddNW.html'
    model1 = PlU
    model2 = Redes
    
    def dispatch(self, request, *args, **kwargs):
        if 'usuario_id' not in request.session:
            return redirect('/Login/')
        
        self.usuario = request.session.get('usuario_nombre')
        
        self.usuario_id = str(self.model1.objects.get(usuario=f'{self.usuario}').id)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        return render(request, self.template)
    
    def post(self, request):
        nombre = request.POST['nombre']
        network = request.POST['network']
        try:
            dhcp = request.POST['dhcp']
        except:
            dhcp = 'off'
        
        fecha = datetime.datetime.now(tz=timezone.utc)
            
        NatAdd = f'VBoxManage natnetwork add --enable --netname="{self.usuario}_{nombre}" --network={network} --dhcp={dhcp} --ipv6=on'
        os.system(NatAdd)
            
        sleep(2)
            
        grabar = self.model2(
            nombre=nombre,
            network=network,
            dhcp=dhcp,
            usuario_id=self.usuario_id,
            fecha=fecha
        )
        grabar.save()
        return HttpResponse('<script src="/static/AltaRecurso.js"></script>')