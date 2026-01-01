from django.db import models
from django.contrib.auth.models import User


class AuditoriaLog(models.Model):
    # 🔎 Usuario que realizó la acción (puede ser null si es automático)
    usuario = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='auditorias'
    )

    # 📌 Acción realizada
    ACCIONES = [
        ('CREAR', 'Crear'),
        ('EDITAR', 'Editar'),
        ('ELIMINAR', 'Eliminar'),
        ('LOGIN', 'Inicio de sesión'),
        ('LOGOUT', 'Cierre de sesión'),
        ('ACCEDER', 'Acceso a módulo'),
        ('VENTA', 'Registro de factura'),
    ]
    accion = models.CharField(max_length=20, choices=ACCIONES)

    # 🗂️ Sobre qué modelo y registro se actuó
    modelo_afectado = models.CharField(max_length=100)  # Ej: "Factura"
    registro_id = models.PositiveIntegerField(null=True, blank=True)  # Ej: ID de factura

    # 📝 Contenido anterior y nuevo (JSON o texto)
    cambios_antes = models.JSONField(null=True, blank=True)
    cambios_despues = models.JSONField(null=True, blank=True)

    # 🌐 Información adicional
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)  # navegador, dispositivo

    # 🕒 Fecha del evento
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Auditoría del Sistema'

    def __str__(self):
        return f"{self.accion} — {self.modelo_afectado} (ID:{self.registro_id}) — {self.fecha.strftime('%d/%m/%Y %H:%M')}"
