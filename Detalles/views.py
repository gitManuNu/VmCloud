from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from Modelos.models import (
    PlanillaUsuarios as PlU,
    VirtualMachineList as VMlist,
    Discos,
    Redes
)
import os

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
    
    def dispatch(self, request, *args, **kwargs):
        if 'usuario_id' not in request.session:
            return redirect('/Login/')
        
        self.usuario = request.session.get('usuario_nombre')
        
        self.vmid = request.GET['vmid']
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        diskid = request.GET['disco']
        ntwid = request.GET['network']
        
        if diskid == '':
            diskid = 0
        if ntwid == '':
            ntwid = 0
        
        usuario_id = self.model4.objects.get(usuario=f'{self.usuario}').id
        vm = self.model1.objects.filter(vmid=self.vmid)
        dsk = self.model2.objects.filter(diskid=diskid)
        ntw_usada = self.model3.objects.filter(id=ntwid)
        ntw = self.model3.objects.exclude(id=ntwid).filter(usuario_id=usuario_id)
        estado = self.model1.objects.get(vmid=self.vmid).estado
        
        return render(request, self.template, {
            'vm': vm,
            'ntw_usada': ntw_usada,
            'dsk': dsk,
            'ntw': ntw,
            'estado': estado,
            'user': self.usuario,
            'diskid': diskid
        })
    
    def post(self, request):
        cpus = request.POST['cpus']
        ram = request.POST['ram']
        vram = request.POST['vram']
        network = request.POST['network']
            
        if network == "NULL":
            network = None
            
        ModificarVirtualMachine(self.vmid,cpus,ram,vram,network,self.usuario)
                
        actualizar = self.model1.objects.get(vmid=self.vmid)
        actualizar.cpus = cpus
        actualizar.ram = ram
        actualizar.vram = vram
        actualizar.network_id = network
        actualizar.save()
            
        return HttpResponse('<script src="/static/AlertaModificado.js/"></script>')
            

class DetallesDiscos(View):
    template = 'DetalleDK.html'
    model = Discos
    
    def dispatch(self, request, *args, **kwargs):
        if 'usuario_id' not in request.session:
            return redirect('/Login/')
                
        self.usuario = request.session.get('usuario_nombre')
        
        self.diskid = request.GET['diskid']
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        dsk = self.model.objects.filter(diskid=self.diskid)
        
        return render(request, self.template, {
            'dsk': dsk,
            'user': self.usuario
        })
        
    def post(self, request):
        size = request.POST['size']
            
        ModifyMedium = f'VBoxManage modifymedium disk "{self.diskid}" --resize={size}'
        os.system(ModifyMedium)
            
        actualizar = self.model.objects.get(diskid=self.diskid)
        actualizar.size = size
        actualizar.save()
            
        return HttpResponse('<script src="/static/AlertaModificado.js/"></script>')
        
class DetallesRedes(View):
    template = 'DetalleNW.html'
    model = Redes
    
    def dispatch(self, request, *args, **kwargs):
        if 'usuario_id' not in request.session:
            return redirect('/Login/')
                
        self.usuario = request.session.get('usuario_nombre')
        self.id = request.GET['id']
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        ntw = self.model.objects.filter(id=self.id)
        
        return render(request, self.template, {
            'ntw': ntw,
            'user': self.usuario
        })
        
    def post(self, request):
        netname = self.model.objects.get(id=self.id).nombre
        network = request.POST['network']
        try:
            dhcp = request.POST['dhcp']
        except:
            dhcp = 'off'
            
        ModifyNat = f'VBoxManage natnetwork modify --dhcp={dhcp} --netname="{self.usuario}_{netname}" --network={network}'
        os.system(ModifyNat)
            
        actualizar = self.model.objects.get(id=self.id)
        actualizar.network = network
        actualizar.dhcp = dhcp
        actualizar.save()
            
        return HttpResponse('<script src="/static/AlertaModificado.js/"></script>')
            
class Borrado(View):
    model1 = VMlist
    model2 = Discos
    model3 = Redes
    
    def dispatch(self, request, *args, **kwargs):
        if 'usuario_id' not in request.session:
            return redirect('/Login/')
        
        self.usuario = request.session.get('usuario_nombre')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self):
        return redirect('/VMCloud/Resources/')
    
    def post(self, request):
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
                return HttpResponse('<script src="/static/AlertaBorradoDisco.js"></script>')
        if nw != None:
            try:
                nw = self.model3.objects.get(id=nw)
                netname = nw.nombre
                nw.delete()
                BorrarNat = f'VBoxManage natnetwork remove --netname "{self.usuario}_{netname}"'
                os.system(BorrarNat)
            except:
                return HttpResponse('<script src="/static/AlertaBorradoRed.js"></script>')
            
        return HttpResponse('<script src="/static/Borrado.js"></script>')

class EncendidoApagado(View):
    model = VMlist
    
    def dispatch(self, request, *args, **kwargs):
        if 'usuario_id' not in request.session:
            return redirect('/Login/')
        
        self.vmid = request.GET['vmid']
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self):
        return redirect('/VMCloud/Resources/')
    
    def post(self, request):
        vm = self.model.objects.get(vmid=self.vmid)
        estado = vm.estado
        so = vm.so
        if so == 'Windows10_64':
            idany = 1755476869
        else:
            idany = 1958095200
        if estado == 1:
            vm.estado = 0
            vm.save()
            PowerOff = f'VBoxManage controlvm "{self.vmid}" poweroff'
            os.system(PowerOff)
            return HttpResponse('<script src="/static/Apagado.js"></script>')
        else:
            vm.estado = 1
            vm.save()
            StartVm = f'VBoxManage startvm "{self.vmid}" --type=headless'
            os.system(StartVm)
            return HttpResponse('<script src="/static/Encendido.js"></script>')