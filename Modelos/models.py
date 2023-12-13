from django.db import models

# Create your models here.

class PlanillaUsuarios(models.Model):
    usuario = models.CharField(max_length=20,verbose_name='usuario')
    nombre = models.CharField(max_length=60,verbose_name='nombre')
    apellido = models.CharField(max_length=60,verbose_name='apellido')
    dni = models.IntegerField(verbose_name='dni')
    email = models.EmailField(max_length=255,verbose_name='email')
    ip = models.CharField(max_length=15,verbose_name='ip')
    web_ip = models.CharField(max_length=15,verbose_name='web_ip')
    clave = models.CharField(max_length=255,verbose_name='clave')
    
    def __str__(self):
        return '%s, %s, %s, %s, %s, %s, %s, %s' % (
            self.usuario,
            self.nombre,
            self.apellido,
            self.dni,
            self.email,
            self.ip,
            self.web_ip,
            self.clave
            )

class TokenRecuperacionTemp(models.Model):
    usuario = models.CharField(max_length=20,verbose_name='usuario')
    token = models.CharField(max_length=50,verbose_name='token')
    fecha_gen = models.DateTimeField(verbose_name='fecha_gen')
    usado = models.SmallIntegerField(verbose_name='usado')
    
    def __str__(self):
        return '%s, %s' % (
            self.usuario,
            self.token,
            self.fecha_gen,
            self.usado
            )

class Discos(models.Model):
    diskid = models.CharField(max_length=40,primary_key=True,verbose_name='diskid')
    nombre = models.CharField(max_length=60,verbose_name='nombre')
    size = models.BigIntegerField(verbose_name='size')
    uso = models.BigIntegerField(verbose_name='uso',null=True)
    usuario = models.ForeignKey(PlanillaUsuarios,on_delete=models.PROTECT,verbose_name='usuario')
    fecha = models.DateTimeField(verbose_name='fecha')
    
    def __str__(self):
        return '%s, %s, %s, %s, %s' % (
            self.diskid,
            self.nombre,
            self.size,
            self.uso,
            self.fecha
        )

class Redes(models.Model):
    nombre = models.CharField(max_length=60,verbose_name='nombre')
    network = models.CharField(max_length=30,verbose_name='network')
    dhcp = models.CharField(max_length=3,verbose_name='dhcp',default=1)
    usuario = models.ForeignKey(PlanillaUsuarios,on_delete=models.PROTECT,verbose_name='usuario')
    fecha = models.DateTimeField(verbose_name='fecha')
    
    def __str__(self):
        return '%s, %s, %s, %s, %s' % (
            self.nombre,
            self.network,
            self.dhcp,
            self.fecha
        )

class VirtualMachineList(models.Model):
    vmid = models.CharField(max_length=40,primary_key=True,verbose_name='vmid')
    vmname = models.CharField(max_length=30,verbose_name='vmname')
    cpus = models.IntegerField(verbose_name='cpus')
    ram = models.IntegerField(verbose_name='ram')
    vram = models.IntegerField(verbose_name='vram')
    so = models.CharField(max_length=60,verbose_name='SO')
    disco = models.ForeignKey(Discos,on_delete=models.PROTECT,verbose_name='disco',null=True)
    network = models.ForeignKey(Redes,on_delete=models.PROTECT,verbose_name='network',null=True)
    usuario = models.ForeignKey(PlanillaUsuarios,on_delete=models.PROTECT,verbose_name='usuario')
    fecha = models.DateTimeField(verbose_name='fecha')
    estado = models.SmallIntegerField(null=False,default=0,verbose_name='estado')
    
    def __str__(self):
        return '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s' % (
            self.vmid,
            self.vmname,
            self.cpus,
            self.ram,
            self.vram,
            self.so,
            self.disco,
            self.network,
            self.fecha,
            self.estado
            )