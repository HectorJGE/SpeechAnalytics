import re

from django.db import models
from django.utils.html import format_html


class Texto(models.Model):
    texto = models.TextField()

    def get_text_formatted(self):
        formatted_text = self.texto

        # Reemplazar etiquetas [Orador 1] y [Orador 2] con formato HTML
        formatted_text = re.sub(
            r'\[Orador 1\]',
            '<span style="color: #ffe082; font-weight: bold;">[Orador 1]</span>',
            formatted_text
        )
        formatted_text = re.sub(
            r'\[Orador 2\]',
            '<span style="color: #ff5722; font-weight: bold;">[Orador 2]</span>',
            formatted_text
        )

        return format_html(formatted_text)

class TablaCorrespondencias(models.Model):
    TOKEN_CHOICES = (
        (0, 'POSITIVO'),
        (1, 'NEGATIVO'),
        (2, 'PROHIBIDO'),
        (3, 'SALUDO'),
        (4, 'DESPEDIDA'),
        (5, 'IDENTIFICACION'),
    )

    lexema = models.CharField(max_length=100, unique=True)
    token = models.IntegerField(choices=TOKEN_CHOICES, blank=True)
    ponderacion = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.lexema} - {self.token} ({self.ponderacion})"
