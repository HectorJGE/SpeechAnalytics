import unicodedata

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView, ListView, DeleteView, DetailView, UpdateView

from main.models import Texto, TablaCorrespondencias

import numpy as np
import re


class HomeView(View):
    template_name = "home.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class SubirTextoView(CreateView):
    model = Texto
    fields = ('texto',)
    success_url = reverse_lazy('lista.textos')
    template_name = 'subir_archivo.html'


class TextoDetailView(DetailView):
    model = Texto
    template_name = 'detalle_texto.html'
    context_object_name = 'texto'

    def separar_oradores(self):
        dialogos_orador_1 = re.findall(r"\[Orador 1\](.*?)\n(?=\[Orador 2\])", self.object.texto, re.DOTALL)
        dialogos_orador_2 = re.findall(r"\[Orador 2\](.*?)\n(?=\[Orador 1\])", self.object.texto, re.DOTALL)

        texto_orador_1 = ' '.join(dialogos_orador_1).strip()
        texto_orador_2 = ' '.join(dialogos_orador_2).strip()

        texto_orador_1 = texto_orador_1.replace('.', '').replace(',', '').replace('?', '').replace('!', '').replace('¿', '')
        texto_orador_2 = texto_orador_2.replace('.', '').replace(',', '').replace('?', '').replace('!', '').replace('¿', '')

        orador_1_palabras = texto_orador_1.split()
        orador_2_palabras = texto_orador_2.split()

        return orador_1_palabras, orador_2_palabras

    def analizar_palabras(self, palabras):
        total = 0
        palabras_positivas = []
        palabras_negativas = []
        palabras_prohibidas = []
        palabras_saludos = []
        palabras_despedidas = []
        palabras_identificacion = []
        palabras_neutras = []

        tabla_correspondencias = TablaCorrespondencias.objects.all()

        p_positivas = tabla_correspondencias.filter(token=0)
        p_negativas = tabla_correspondencias.filter(token=1)
        p_prohibidas = tabla_correspondencias.filter(token=2)
        saludos = tabla_correspondencias.filter(token=3)
        despedidas = tabla_correspondencias.filter(token=4)
        identificacion = tabla_correspondencias.filter(token=5)

        for palabra in palabras:
            if p_positivas.filter(lexema__iexact=palabra).exists():
                q = p_positivas.get(lexema__iexact=palabra)
                total += q.ponderacion
                palabras_positivas.append((palabra, q.ponderacion, q.get_token_display(), q.id))
            elif p_negativas.filter(lexema__iexact=palabra).exists():
                q = p_negativas.get(lexema__iexact=palabra)
                total += q.ponderacion
                palabras_negativas.append((palabra, q.ponderacion, q.get_token_display(), q.id))
            elif p_prohibidas.filter(lexema__iexact=palabra).exists():
                q = p_prohibidas.get(lexema__iexact=palabra)
                total += q.ponderacion
                palabras_prohibidas.append((palabra, q.ponderacion, q.get_token_display(), q.id))
            elif saludos.filter(lexema__iexact=palabra).exists():
                q = saludos.get(lexema__iexact=palabra)
                total += q.ponderacion
                palabras_saludos.append((palabra, q.ponderacion, q.get_token_display(), q.id))
            elif despedidas.filter(lexema__iexact=palabra).exists():
                q = despedidas.get(lexema__iexact=palabra)
                total += q.ponderacion
                palabras_despedidas.append((palabra, q.ponderacion, q.get_token_display(), q.id))
            else:
                palabras_neutras.append((palabra, 0, 'NEUTRO', None))

        texto_completo = " ".join(palabras).lower()

        for identificacion_obj in identificacion:
            if identificacion_obj.lexema.lower() in texto_completo:
                ponderacion = identificacion_obj.ponderacion
                total += ponderacion
                palabras_identificacion.append((identificacion_obj.lexema, ponderacion, identificacion_obj.get_token_display(), identificacion_obj.id))

        if palabras_positivas:
            palabra_positiva_max = max(palabras_positivas, key=lambda x: x[1])
        else:
            palabra_positiva_max = None

        if palabras_negativas:
            palabra_negativa_max = min(palabras_negativas, key=lambda x: x[1])
        else:
            palabra_negativa_max = None

        cant_pos = len(palabras_positivas)
        cant_neg = len(palabras_negativas) + len(palabras_prohibidas)
        palabras_rudas = len(palabras_prohibidas) > 0
        saludo = len(palabras_saludos) > 0
        despedidas = len(palabras_despedidas) > 0
        identificacion = len(palabras_identificacion) > 0

        tabla = palabras_positivas + palabras_negativas + palabras_prohibidas + palabras_saludos + palabras_despedidas + palabras_identificacion + palabras_neutras
        return tabla, total, palabra_positiva_max, palabra_negativa_max, cant_pos, cant_neg, palabras_rudas, saludo, despedidas, identificacion

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        orador_1, orador_2 = self.separar_oradores()
        tabla_1, ponderado_1, pal_pos_max_1, pal_neg_max_1, cant_pos_1, cant_neg_1, palabras_rudas_1, saludo_1, despedida_1, identificacion_1 = self.analizar_palabras(orador_1)
        tabla_2, ponderado_2, pal_pos_max_2, pal_neg_max_2, cant_pos_2, cant_neg_2, palabras_rudas_2, saludo_2, despedida_2, identificacion_2 = self.analizar_palabras(orador_2)

        ponderado = ponderado_1 + ponderado_2
        sentimiento = '<span class="badge text-bg-success">Positivo</span>' if ponderado > 0 else '<span class="badge text-bg-secondary">Neutro</span>' if ponderado >= 0 else '<span class="badge text-bg-danger">Negativo</span>  '
        context['indice_ponderado'] = ponderado
        context['sentimiento'] = sentimiento
        tabla = tabla_1 + tabla_2

        tabla_min = [(x[0].lower(), x[1], x[2].lower(), x[3]) for x in tabla]
        tabla_sin_repetidos = list(set(tabla_min))
        tabla_ordenada = sorted(tabla_sin_repetidos, key=lambda x: x[2])

        context['tabla'] = tabla_ordenada
        array_positividad = self.get_linear_positivity()
        array_posiciones = [i for i in range(len(array_positividad))]
        context['labels_linear_positivity'] = array_posiciones
        context['data_linear_positivity'] = array_positividad

        context['cant_palabras_pos'] = cant_pos_1 + cant_pos_2
        context['cant_palabras_neg'] = cant_neg_1 + cant_neg_2

        context['pal_pos_max_1'] = pal_pos_max_1[0]
        context['pal_pos_max_2'] = pal_pos_max_2[0]
        context['pal_neg_max_1'] = pal_neg_max_1[0]
        context['pal_neg_max_2'] = pal_neg_max_2[0]

        context['saludo_agente'] = self.get_span_color(saludo_1)
        context['saludo_cliente'] = self.get_span_color(saludo_2)
        context['despedida_agente'] = self.get_span_color(despedida_1)
        context['despedida_cliente'] = self.get_span_color(despedida_2)

        context['identificacion_cliente'] = self.get_span_color(identificacion_1 or identificacion_2)

        context['lenguaje_rudo'] = self.get_span_color(palabras_rudas_1 or palabras_rudas_2)

        return context

    def get_span_color(self, boolean):
        if boolean:
            r = '<span class="badge text-bg-success">Si</span>'
        else:
            r = '<span class="badge text-bg-danger">No</span>'
        return r

    def get_linear_positivity(self):
        texto = self.object.texto
        texto = texto.lower()
        texto = texto.replace('[orador 1]', "").replace('[orador 2]', "").replace('\n', "")
        eliminar = ".,?!¿¡"
        eliminar = str.maketrans("", "", eliminar)
        texto = texto.translate(eliminar)
        texto = texto.split()
        ponderacion_array = []
        for palabra in texto:
            lexema = TablaCorrespondencias.objects.filter(lexema__iexact=palabra).first()
            if lexema:
                ponderacion = lexema.ponderacion
                ponderacion_array.append(ponderacion)
        window_size = 5
        smoothed_scores = np.convolve(ponderacion_array, np.ones(window_size)/window_size, mode='valid')

        return smoothed_scores.tolist()


class BorrarTextoView(View):
    def post(self, request, *args, **kwargs):
        texto = Texto.objects.get(pk=kwargs['pk'])
        texto.delete()
        return HttpResponseRedirect(reverse_lazy('lista.textos'))


class ListaTextosView(ListView):
    model = Texto
    template_name = 'lista_textos.html'
    context_object_name = 'textos'


class TablaCorrespondenciasCreateView(CreateView):
    model = TablaCorrespondencias
    fields = ['lexema', 'token', 'ponderacion']
    template_name = 'tabla_correspondencias_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['pk_texto'] = self.request.GET.get('pk_texto')
        return context

    def get_success_url(self):
        pk_texto = self.request.GET.get('pk_texto')
        return reverse('detalle.texto', kwargs={'pk': pk_texto})

    def get_initial(self):
        initial = super().get_initial()
        lexema = self.request.GET.get('lexema', '')
        token = self.request.GET.get('token', '')
        ponderacion = self.request.GET.get('ponderacion', '')

        if lexema:
            initial['lexema'] = lexema
        if token:
            initial['token'] = token
        if ponderacion:
            initial['ponderacion'] = ponderacion

        return initial


class TablaCorrespondenciasUpdateView(UpdateView):
    model = TablaCorrespondencias
    fields = ['lexema', 'token', 'ponderacion']
    template_name = 'tabla_correspondencias_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['pk_texto'] = self.request.GET.get('pk_texto')
        return context

    def get_success_url(self):
        pk_texto = self.request.GET.get('pk_texto')
        return reverse('detalle.texto', kwargs={'pk': pk_texto})


class TablaCorrespondenciasDeleteView(DeleteView):
    model = TablaCorrespondencias
    template_name = 'tabla_correspondencias_confirm_delete.html'

    def get_success_url(self):
        pk_texto = self.request.GET.get('pk_texto')
        return reverse('detalle.texto', kwargs={'pk': pk_texto})

