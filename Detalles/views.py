from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
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

#+--------------------------------------------------------------------------------+

def CambiarRed(vmid,network,usuario):
    RemoveNat = f'VBoxManage modifyvm "{vmid}" --nic1=none --nic-type1=82540EM --cable-connected1=off --nic-boot-prio1=1 --nat-network1=none'
    os.system(RemoveNat)
    if network != None:
        network = Redes.objects.get(id=network).nombre
        AddNtw = f'VBoxManage modifyvm "{vmid}" --nic1=natnetwork --nic-type1=82540EM --cable-connected1=on --nic-boot-prio1=1 --nat-network1="{usuario}_{network}"'
        os.system(AddNtw)
        
def ModificarVirtualMachine(vmid,cpus,ram,vram,network,usuario):
    CambiarRed(vmid,network,usuario)
    ModifyVM = f'VBoxManage modifyvm "{vmid}" --memory={ram} --vram={vram} --cpus={cpus}'
    os.system(ModifyVM)
    
def BorrarMaquinaVirtual(vmid):
    UnregisterVm = f'VBoxManage unregistervm {vmid} --delete --delete-all'
    os.system(UnregisterVm)

#+--------------------------------------------------------------------------------+

class DetallesVirtualMachines(View):
    template = 'DetalleVM.html'
    model1 = VMlist
    model2 = Discos
    model3 = Redes
    model4 = PlU
    
    def get(self, request):
        return HttpResponse('<meta http-equiv="refresh" content="1;/Login/">')
    
    def post(self, request):
        vmid = request.GET['vmid']
        diskid = request.GET['disco']
        ntwid = request.GET['network']
        usuario = request.GET['user']
        
        if diskid == '':
            diskid = 0
        if ntwid == '':
            ntwid = 0
        
        usuario_id = self.model4.objects.get(usuario=f'{usuario}').id
        vm = self.model1.objects.filter(vmid=vmid)
        dsk = self.model2.objects.filter(diskid=diskid)
        ntw_usada = self.model3.objects.filter(id=ntwid)
        ntw = self.model3.objects.exclude(id=ntwid).filter(usuario_id=usuario_id)
        estado = self.model1.objects.get(vmid=vmid).estado
        
        try:
            cpus = request.POST['cpus']
            ram = request.POST['ram']
            vram = request.POST['vram']
            network = request.POST['network']
            
            if network == "NULL":
                network = None
            
            ModificarVirtualMachine(vmid,cpus,ram,vram,network,usuario)
                
            actualizar = self.model1.objects.get(vmid=vmid)
            actualizar.cpus = cpus
            actualizar.ram = ram
            actualizar.vram = vram
            actualizar.network_id = network
            actualizar.save()
            
            return HttpResponse('<script>window.close()</script>')
            
        except:
            return render(request, self.template, {
                'vm': vm,
                'ntw_usada': ntw_usada,
                'dsk': dsk,
                'ntw': ntw,
                'estado': estado,
                'user': usuario,
                'diskid': diskid
            })

class DetallesDiscos(View):
    template = 'DetalleDK.html'
    model = Discos
    
    def get(self, request):
        return HttpResponse('<meta http-equiv="refresh" content="1;/Login/">')
    
    def post(self, request):
        diskid = request.GET['diskid']
        dsk = self.model.objects.filter(diskid=diskid)
        usuario = request.GET['user']
        
        try:
            size = request.POST['size']
            
            ModifyMedium = f'VBoxManage modifymedium disk "{diskid}" --resize={size}'
            os.system(ModifyMedium)
            
            actualizar = self.model.objects.get(diskid=diskid)
            actualizar.size = size
            actualizar.save()
            
            return HttpResponse('<script>window.close()</script>')
        
        except:
            return render(request, self.template, {
                'dsk': dsk,
                'user': usuario
            })
    
class DetallesRedes(View):
    template = 'DetalleNW.html'
    model = Redes
    
    def get(self, request):
        return HttpResponse('<meta http-equiv="refresh" content="1;/Login/">')
    
    def post(self, request):
        id = request.GET['id']
        ntw = self.model.objects.filter(id=id)
        netname = self.model.objects.get(id=id).nombre
        usuario = request.GET['user']
        
        try:
            network = request.POST['network']
            try:
                dhcp = request.POST['dhcp']
            except:
                dhcp = 'off'
            
            ModifyNat = f'VBoxManage natnetwork modify --dhcp={dhcp} --netname="{usuario}_{netname}" --network={network}'
            os.system(ModifyNat)
            
            actualizar = self.model.objects.get(id=id)
            actualizar.network = network
            actualizar.dhcp = dhcp
            actualizar.save()
            
            return HttpResponse('<script>window.close()</script>')
        
        except:
            return render(request, self.template, {
                'ntw': ntw,
                'user': usuario
            })
            
class Borrado(View):
    model1 = VMlist
    model2 = Discos
    model3 = Redes
    
    def get(self, request):
        return HttpResponse('<meta http-equiv="refresh" content="1;/Login/">')
    
    def post(self, request):
        usuario = request.GET['user']
        try:
            vm = request.GET['vmid']
        except:
            vm = None
        try:
            dk = request.GET['disco']
        except:
            dk = None
        try:
            nw = request.GET['id']
        except:
            nw = None
            
        if vm != None:
            BorrarMaquinaVirtual(vm)
            vm = self.model1.objects.get(vmid=vm)
            vm.delete()
        if dk != None:
            try:
                dk = self.model2.objects.get(diskid=dk)
                dk.delete()
            except:
                return HttpResponse('<h3>Hay maquinas virtuales utilizando este disco, primero debe eliminar las mismas para proceder con el borrado del disco!!</h3>')
        if nw != None:
            try:
                nw = self.model3.objects.get(id=nw)
                netname = nw.nombre
                nw.delete()
                print(f'{usuario}_{netname}')
                BorrarNat = f'VBoxManage natnetwork remove --netname "{usuario}_{netname}"'
                os.system(BorrarNat)
            except:
                return HttpResponse('<h3>Hay maquinas virtuales utilizando esta red, primero debe eliminar las mismas para proceder con el borrado de la red!!</h3>')
            
        return HttpResponse('<h2>Borrado satisfactorio!! Ya puede cerrar esta pestaña</h2>')

class EncendidoApagado(View):
    model = VMlist
    
    def get(self, request):
        return HttpResponse('<meta http-equiv="refresh" content="1;/Login/">')
    
    def post(self, request):
        vmid = request.GET['vmid']
        vm = self.model.objects.get(vmid=vmid)
        estado = vm.estado
        so = vm.so
        if so == 'Windows10_64':
            idany = 1755476869
        else:
            idany = 1958095200
        if estado == 1:
            vm.estado = 0
            vm.save()
            PowerOff = f'VBoxManage controlvm "{vmid}" poweroff'
            os.system(PowerOff)
            return HttpResponse('<h2>Equipo apagado satisfactoriamente, puede cerrar la pestaña</h2>')
        else:
            vm.estado = 1
            vm.save()
            StartVm = f'VBoxManage startvm "{vmid}" --type=headless'
            os.system(StartVm)
            return HttpResponse(f'<h2>Equipo encendido...<br>Inicie AnyDesk e ingrese el siguiente codigo: {idany}</h2>')