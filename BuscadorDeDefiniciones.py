"""
Buscador de Definiciones MULTI-API
Versión 2.0 - Soporta 6 APIs diferentes + selección manual
Autor: Asistente Profesional
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import os
import requests
from datetime import datetime
from difflib import get_close_matches
from threading import Thread
from functools import partial

# ==================== CONFIGURACIÓN DE APIs ====================

class ConfiguracionAPI:
    """Configuración centralizada de todas las APIs disponibles"""
    
    # Wordnik - Necesita registro gratuito
    WORDNIK_API_KEY = ""  # Obtén tu clave en https://www.wordnik.com/signup
    WORDNIK_URL = "https://api.wordnik.com/v4/word.json/{palabra}/definitions"
    
    # Glosbe - Necesita registro gratuito
    GLOSBE_API_KEY = ""   # Obtén en https://glosbe.com/api
    GLOSBE_URL = "https://glosbe.com/gapi/translate"
    
    # APIs que no requieren clave
    FREE_DICT_API = "https://api.dictionaryapi.dev/api/v2/entries/en/{palabra}"
    LINGUAROBOT_API = "https://api.linguarobot.io/v1/dictionary/{palabra}"
    MYMEMORY_API = "https://api.mymemory.translated.net/get?q={palabra}&langpair=en|es"
    
    @classmethod
    def tiene_clave_wordnik(cls):
        return cls.WORDNIK_API_KEY and cls.WORDNIK_API_KEY != ""
    
    @classmethod
    def tiene_clave_glosbe(cls):
        return cls.GLOSBE_API_KEY and cls.GLOSBE_API_KEY != ""


# ==================== CLASE PRINCIPAL DEL DICCIONARIO ====================

class DiccionarioMultiAPI:
    """
    Diccionario que soporta múltiples APIs y permite elegir cuál usar
    """
    
    def __init__(self):
        self.diccionario_local = {}
        self.historial = []
        self.favoritos = set()
        self.api_seleccionada = "auto"  # auto, wordnik, free_dict, linguarobot, glosbe, mymemory, local
        
        # Archivos de persistencia
        self.archivo_local = "diccionario_local.json"
        self.archivo_historial = "historial_busquedas.json"
        self.archivo_favoritos = "favoritos.json"
        
        # Estadísticas de APIs
        self.estadisticas_api = {
            "wordnik": 0,
            "free_dict": 0,
            "linguarobot": 0,
            "glosbe": 0,
            "mymemory": 0,
            "local": 0
        }
        
        self.cargar_diccionario_local()
        self.cargar_historial()
        self.cargar_favoritos()
    
    # ==================== PERSISTENCIA ====================
    
    def cargar_diccionario_local(self):
        """Carga el diccionario local desde JSON"""
        try:
            if os.path.exists(self.archivo_local):
                with open(self.archivo_local, 'r', encoding='utf-8') as f:
                    self.diccionario_local = json.load(f)
            else:
                # Diccionario inicial de ejemplo
                self.diccionario_local = {
                    "python": "Lenguaje de programación de alto nivel, interpretado y dinámico.",
                    "programacion": "Arte de escribir instrucciones para computadoras.",
                    "algoritmo": "Secuencia lógica de pasos para resolver un problema.",
                    "inteligencia artificial": "Simulación de procesos de inteligencia humana por máquinas.",
                    "machine learning": "Rama de IA que permite a sistemas aprender de datos."
                }
                self.guardar_diccionario_local()
        except Exception as e:
            print(f"Error cargando diccionario local: {e}")
            self.diccionario_local = {}
    
    def guardar_diccionario_local(self):
        """Guarda diccionario local"""
        try:
            with open(self.archivo_local, 'w', encoding='utf-8') as f:
                json.dump(self.diccionario_local, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando: {e}")
    
    def cargar_historial(self):
        try:
            if os.path.exists(self.archivo_historial):
                with open(self.archivo_historial, 'r', encoding='utf-8') as f:
                    self.historial = json.load(f)
        except:
            self.historial = []
    
    def guardar_historial(self):
        try:
            with open(self.archivo_historial, 'w', encoding='utf-8') as f:
                json.dump(self.historial[-200:], f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def cargar_favoritos(self):
        try:
            if os.path.exists(self.archivo_favoritos):
                with open(self.archivo_favoritos, 'r', encoding='utf-8') as f:
                    self.favoritos = set(json.load(f))
        except:
            self.favoritos = set()
    
    def guardar_favoritos(self):
        try:
            with open(self.archivo_favoritos, 'w', encoding='utf-8') as f:
                json.dump(list(self.favoritos), f, ensure_ascii=False, indent=2)
        except:
            pass
    
    # ==================== APIs DE DEFINICIONES ====================
    
    def buscar_wordnik(self, palabra):
        """Wordnik API - Soporta español e inglés"""
        if not ConfiguracionAPI.tiene_clave_wordnik():
            return None, "⚠️ API Key no configurada"
        
        try:
            url = ConfiguracionAPI.WORDNIK_URL.format(palabra=palabra)
            params = {
                'api_key': ConfiguracionAPI.WORDNIK_API_KEY,
                'sourceDictionaries': 'wiktionary,spanish',
                'limit': 3,
                'includeRelated': False
            }
            respuesta = requests.get(url, params=params, timeout=8)
            
            if respuesta.status_code == 200:
                datos = respuesta.json()
                if datos:
                    definicion = datos[0].get('text', '')
                    if definicion:
                        return definicion, "📖 Wordnik"
            return None, "No encontrado"
        except Exception as e:
            return None, f"Error: {str(e)[:50]}"
    
    def buscar_free_dictionary(self, palabra):
        """Free Dictionary API - Solo inglés, pero muy confiable"""
        try:
            url = ConfiguracionAPI.FREE_DICT_API.format(palabra=palabra)
            respuesta = requests.get(url, timeout=5)
            
            if respuesta.status_code == 200:
                datos = respuesta.json()
                if datos and len(datos) > 0:
                    definicion = datos[0]['meanings'][0]['definitions'][0]['definition']
                    return definicion, "🌐 Free Dictionary (EN)"
            return None, "No encontrado"
        except:
            return None, "Error de conexión"
    
    def buscar_linguarobot(self, palabra):
        """LinguaRobot API - Soporte multilingüe"""
        try:
            url = ConfiguracionAPI.LINGUAROBOT_API.format(palabra=palabra)
            respuesta = requests.get(url, timeout=5)
            
            if respuesta.status_code == 200:
                datos = respuesta.json()
                if 'definition' in datos:
                    return datos['definition'], "🤖 LinguaRobot"
                elif 'translations' in datos:
                    return datos['translations'][0], "🤖 LinguaRobot"
            return None, "No encontrado"
        except:
            return None, "Error"
    
    def buscar_glosbe(self, palabra):
        """Glosbe API - Diccionario multilingüe"""
        if not ConfiguracionAPI.tiene_clave_glosbe():
            return None, "⚠️ API Key no configurada"
        
        try:
            params = {
                'from': 'eng',
                'dest': 'spa',
                'format': 'json',
                'phrase': palabra,
                'pretty': 'true'
            }
            respuesta = requests.get(ConfiguracionAPI.GLOSBE_URL, params=params, timeout=5)
            
            if respuesta.status_code == 200:
                datos = respuesta.json()
                if 'tuc' in datos and len(datos['tuc']) > 0:
                    if 'phrase' in datos['tuc'][0]:
                        definicion = datos['tuc'][0]['phrase']['text']
                        return definicion, "📚 Glosbe"
            return None, "No encontrado"
        except:
            return None, "Error"
    
    def buscar_mymemory(self, palabra):
        """MyMemory API - Traducciones y definiciones contextuales"""
        try:
            url = ConfiguracionAPI.MYMEMORY_API.format(palabra=palabra)
            respuesta = requests.get(url, timeout=5)
            
            if respuesta.status_code == 200:
                datos = respuesta.json()
                if 'responseData' in datos and 'translatedText' in datos['responseData']:
                    traduccion = datos['responseData']['translatedText']
                    if traduccion and traduccion != palabra:
                        return f"Significado contextual: {traduccion}", "💾 MyMemory"
            return None, "No encontrado"
        except:
            return None, "Error"
    
    def buscar_local(self, palabra):
        """Búsqueda en diccionario local"""
        palabra_lower = palabra.lower().strip()
        definicion = self.diccionario_local.get(palabra_lower)
        if definicion:
            return definicion, "💿 Diccionario Local"
        return None, None
    
    # ==================== SELECCIÓN INTELIGENTE DE API ====================
    
    def buscar_con_api_seleccionada(self, palabra):
        """
        Busca usando la API seleccionada por el usuario
        """
        metodos = {
            "wordnik": self.buscar_wordnik,
            "free_dict": self.buscar_free_dictionary,
            "linguarobot": self.buscar_linguarobot,
            "glosbe": self.buscar_glosbe,
            "mymemory": self.buscar_mymemory,
            "local": self.buscar_local
        }
        
        if self.api_seleccionada in metodos:
            return metodos[self.api_seleccionada](palabra)
        return None, "API no válida"
    
    def buscar_automatico(self, palabra):
        """
        Búsqueda automática probando todas las APIs en orden de prioridad
        Prioriza APIs con español y buena calidad
        """
        # Orden de prioridad
        prioridad = [
            ("wordnik", self.buscar_wordnik),
            ("free_dict", self.buscar_free_dictionary),
            ("linguarobot", self.buscar_linguarobot),
            ("glosbe", self.buscar_glosbe),
            ("mymemory", self.buscar_mymemory),
            ("local", self.buscar_local)
        ]
        
        for nombre_api, metodo in prioridad:
            definicion, fuente = metodo(palabra)
            if definicion and "No encontrado" not in definicion:
                # Registrar estadística
                if nombre_api in self.estadisticas_api:
                    self.estadisticas_api[nombre_api] += 1
                return definicion, fuente
        
        return None, "No se encontró en ninguna fuente"
    
    def buscar(self, palabra, modo="auto"):
        """
        Método principal de búsqueda
        modo: 'auto', 'wordnik', 'free_dict', 'linguarobot', 'glosbe', 'mymemory', 'local'
        """
        self.api_seleccionada = modo
        
        if modo == "auto":
            definicion, fuente = self.buscar_automatico(palabra)
        else:
            definicion, fuente = self.buscar_con_api_seleccionada(palabra)
        
        if definicion and "No encontrado" not in definicion:
            self.agregar_historial(palabra, definicion, fuente)
            return definicion, fuente
        
        # Buscar sugerencias si no hay resultados
        sugerencias = self.buscar_aproximacion(palabra)
        if sugerencias:
            return None, f"No encontrado. ¿Quisiste decir: {', '.join(sugerencias[:3])}?"
        
        return None, "❌ Definición no encontrada en ninguna API"
    
    def buscar_aproximacion(self, palabra):
        """Busca palabras similares en diccionario local"""
        palabras_disponibles = list(self.diccionario_local.keys())
        coincidencias = get_close_matches(palabra.lower(), palabras_disponibles, n=5, cutoff=0.6)
        return coincidencias
    
    def agregar_historial(self, palabra, definicion, fuente):
        """Registra búsqueda en historial"""
        entrada = {
            "palabra": palabra,
            "definicion": definicion[:200] + "..." if len(definicion) > 200 else definicion,
            "fuente": fuente,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.historial.insert(0, entrada)
        self.guardar_historial()
    
    def obtener_historial(self):
        return self.historial
    
    def toggle_favorito(self, palabra):
        palabra_lower = palabra.lower().strip()
        if palabra_lower in self.favoritos:
            self.favoritos.remove(palabra_lower)
            resultado = False
        else:
            self.favoritos.add(palabra_lower)
            resultado = True
        self.guardar_favoritos()
        return resultado
    
    def es_favorito(self, palabra):
        return palabra.lower().strip() in self.favoritos
    
    def obtener_estadisticas(self):
        """Retorna estadísticas de uso de APIs"""
        total = sum(self.estadisticas_api.values())
        return self.estadisticas_api, total
    
    def agregar_definicion_local(self, palabra, definicion):
        palabra_lower = palabra.lower().strip()
        self.diccionario_local[palabra_lower] = definicion
        self.guardar_diccionario_local()
        return True
    
    def exportar_definiciones(self, formato="json"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if formato == "json":
            archivo = f"diccionario_exportado_{timestamp}.json"
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(self.diccionario_local, f, ensure_ascii=False, indent=2)
        else:
            archivo = f"diccionario_exportado_{timestamp}.txt"
            with open(archivo, 'w', encoding='utf-8') as f:
                f.write("DICCIONARIO EXPORTADO\n")
                f.write("="*50 + "\n\n")
                for palabra, definicion in sorted(self.diccionario_local.items()):
                    f.write(f"📌 {palabra.upper()}\n{definicion}\n{'-'*30}\n")
        
        return archivo


# ==================== INTERFAZ GRÁFICA PROFESIONAL ====================

class AplicacionMultiAPI:
    """Interfaz gráfica con selección de API"""
    
    def __init__(self):
        self.diccionario = DiccionarioMultiAPI()
        
        self.ventana = tk.Tk()
        self.ventana.title("Buscador Multi-API - Diccionarios en 6 Fuentes")
        self.ventana.geometry("1000x750")
        self.ventana.configure(bg='#f0f0f0')
        
        self.crear_widgets()
        self.configurar_eventos()
        
        # Mostrar advertencia si faltan claves
        self.verificar_configuracion_apis()
    
    def verificar_configuracion_apis(self):
        """Verifica qué APIs están configuradas"""
        mensajes = []
        if not ConfiguracionAPI.tiene_clave_wordnik():
            mensajes.append("• Wordnik: API key no configurada (opcional)")
        if not ConfiguracionAPI.tiene_clave_glosbe():
            mensajes.append("• Glosbe: API key no configurada (opcional)")
        
        if mensajes:
            aviso = "⚠️ Configuración opcional pendiente:\n" + "\n".join(mensajes)
            aviso += "\n\n💡 Las APIs sin clave siguen funcionando con límites reducidos"
            self.status_bar.config(text="Algunas APIs requieren configuración", foreground="orange")
            # No mostramos messagebox para no molestar, solo en barra de estado
    
    def crear_widgets(self):
        """Crea todos los elementos de la interfaz"""
        
        # Frame principal
        main_frame = ttk.Frame(self.ventana, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== SECCIÓN BÚSQUEDA =====
        frame_busqueda = ttk.LabelFrame(main_frame, text="🔍 Búsqueda", padding="10")
        frame_busqueda.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame_busqueda, text="Palabra:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, sticky=tk.W)
        
        self.entry_palabra = ttk.Entry(frame_busqueda, font=("Arial", 12), width=40)
        self.entry_palabra.grid(row=0, column=1, padx=5, sticky=tk.W+tk.E)
        
        # Selector de API
        ttk.Label(frame_busqueda, text="API a usar:", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=10, sticky=tk.W)
        
        self.api_seleccionada = tk.StringVar(value="auto")
        combo_apis = ttk.Combobox(frame_busqueda, textvariable=self.api_seleccionada, 
                                  values=[
                                      "auto (Automático - Recomendado)",
                                      "wordnik (Wordnik - Español/Inglés)",
                                      "free_dict (Free Dictionary - Inglés)",
                                      "linguarobot (LinguaRobot - Multilingüe)",
                                      "glosbe (Glosbe - Multilingüe)",
                                      "mymemory (MyMemory - Contextual)",
                                      "local (Diccionario Local)"
                                  ], width=35, state="readonly")
        combo_apis.grid(row=0, column=3, padx=5)
        
        self.btn_buscar = ttk.Button(frame_busqueda, text="🔍 BUSCAR", command=self.buscar, width=15)
        self.btn_buscar.grid(row=0, column=4, padx=10)
        
        frame_busqueda.columnconfigure(1, weight=1)
        
        # ===== PANEL DE CONTROL =====
        frame_controles = ttk.Frame(main_frame)
        frame_controles.pack(fill=tk.X, pady=(0, 10))
        
        botones = [
            ("⭐ Favoritos", self.mostrar_favoritos),
            ("📜 Historial", self.mostrar_historial),
            ("📊 Estadísticas", self.mostrar_estadisticas),
            ("➕ Agregar palabra", self.agregar_palabra),
            ("💾 Exportar", self.exportar_diccionario),
            ("ℹ️ Info APIs", self.mostrar_info_apis)
        ]
        
        for texto, comando in botones:
            ttk.Button(frame_controles, text=texto, command=comando).pack(side=tk.LEFT, padx=2)
        
        # ===== ÁREA DE RESULTADOS =====
        frame_resultados = ttk.LabelFrame(main_frame, text="📖 Definición", padding="10")
        frame_resultados.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.texto_definicion = scrolledtext.ScrolledText(frame_resultados, wrap=tk.WORD, 
                                                           font=("Arial", 11), height=12)
        self.texto_definicion.pack(fill=tk.BOTH, expand=True)
        
        # Configurar tags de formato
        self.texto_definicion.tag_config("titulo", font=("Arial", 16, "bold"), foreground="#2c3e50")
        self.texto_definicion.tag_config("fuente", font=("Arial", 9, "italic"), foreground="#7f8c8d")
        self.texto_definicion.tag_config("definicion", font=("Arial", 11), spacing1=5, spacing3=5)
        self.texto_definicion.tag_config("error", font=("Arial", 11), foreground="#e74c3c")
        
        # ===== SUGERENCIAS Y FAVORITOS =====
        frame_inferior = ttk.Frame(main_frame)
        frame_inferior.pack(fill=tk.BOTH, expand=True)
        
        # Sugerencias
        frame_sugerencias = ttk.LabelFrame(frame_inferior, text="💡 Palabras similares", padding="5")
        frame_sugerencias.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.lista_sugerencias = tk.Listbox(frame_sugerencias, font=("Arial", 10), height=6)
        self.lista_sugerencias.pack(fill=tk.BOTH, expand=True)
        
        # Favoritos
        frame_favoritos = ttk.LabelFrame(frame_inferior, text="⭐ Mis favoritos", padding="5")
        frame_favoritos.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.lista_favoritos = tk.Listbox(frame_favoritos, font=("Arial", 10), height=6)
        self.lista_favoritos.pack(fill=tk.BOTH, expand=True)
        
        # Barra de estado
        self.status_bar = ttk.Label(self.ventana, text="Listo - Selecciona una API o usa modo automático", 
                                    relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Cargar favoritos iniciales
        self.actualizar_lista_favoritos()
    
    def configurar_eventos(self):
        """Configura eventos de la interfaz"""
        self.entry_palabra.bind('<Return>', lambda e: self.buscar())
        self.lista_sugerencias.bind('<Double-Button-1>', lambda e: self.buscar_desde_lista(self.lista_sugerencias))
        self.lista_favoritos.bind('<Double-Button-1>', lambda e: self.buscar_desde_lista(self.lista_favoritos))
    
    def buscar(self):
        """Realiza la búsqueda con la API seleccionada"""
        palabra = self.entry_palabra.get().strip()
        if not palabra:
            messagebox.showwarning("Advertencia", "Ingresa una palabra para buscar")
            return
        
        # Obtener modo seleccionado
        seleccion = self.api_seleccionada.get()
        modo_map = {
            "auto (Automático - Recomendado)": "auto",
            "wordnik (Wordnik - Español/Inglés)": "wordnik",
            "free_dict (Free Dictionary - Inglés)": "free_dict",
            "linguarobot (LinguaRobot - Multilingüe)": "linguarobot",
            "glosbe (Glosbe - Multilingüe)": "glosbe",
            "mymemory (MyMemory - Contextual)": "mymemory",
            "local (Diccionario Local)": "local"
        }
        
        modo = modo_map.get(seleccion, "auto")
        
        self.status_bar.config(text=f"Buscando '{palabra}' con {modo}...")
        self.ventana.config(cursor="watch")
        
        # Buscar en hilo separado
        hilo = Thread(target=self._buscar_thread, args=(palabra, modo))
        hilo.daemon = True
        hilo.start()
    
    def _buscar_thread(self, palabra, modo):
        """Ejecuta la búsqueda en segundo plano"""
        definicion, fuente = self.diccionario.buscar(palabra, modo)
        
        self.ventana.after(0, self._actualizar_interfaz, palabra, definicion, fuente, modo)
        self.ventana.after(0, lambda: self.ventana.config(cursor=""))
    
    def _actualizar_interfaz(self, palabra, definicion, fuente, modo):
        """Actualiza la interfaz con los resultados"""
        self.texto_definicion.delete(1.0, tk.END)
        
        if definicion:
            # Mostrar definición encontrada
            self.texto_definicion.insert(tk.END, f"{palabra.upper()}\n", "titulo")
            self.texto_definicion.insert(tk.END, f"Fuente: {fuente} | Modo: {modo}\n\n", "fuente")
            self.texto_definicion.insert(tk.END, definicion, "definicion")
            
            # Botón de favorito temporal
            es_fav = self.diccionario.es_favorito(palabra)
            self.mostrar_boton_favorito(palabra, es_fav)
            
            self.status_bar.config(text=f"✓ Definición encontrada - {fuente}", foreground="green")
            
            # Buscar sugerencias
            sugerencias = self.diccionario.buscar_aproximacion(palabra)
            if sugerencias:
                self.actualizar_sugerencias(sugerencias)
        else:
            # Mostrar error
            self.texto_definicion.insert(tk.END, "❌ DEFINICIÓN NO ENCONTRADA\n\n", "titulo")
            self.texto_definicion.insert(tk.END, fuente, "error")
            self.status_bar.config(text=f"✗ {fuente}", foreground="red")
    
    def mostrar_boton_favorito(self, palabra, es_favorito):
        """Muestra botón flotante para favoritos"""
        frame_boton = ttk.Frame(self.ventana)
        frame_boton.place(relx=0.9, rely=0.3, anchor=tk.NE)
        
        texto = "★ Quitar de favoritos" if es_favorito else "☆ Agregar a favoritos"
        btn = ttk.Button(frame_boton, text=texto, 
                        command=lambda: self.toggle_favorito_con_ui(palabra, btn, frame_boton))
        btn.pack()
        
        # Auto-ocultar después de 4 segundos
        self.ventana.after(4000, frame_boton.destroy)
    
    def toggle_favorito_con_ui(self, palabra, boton, frame):
        """Alterna favorito y actualiza UI"""
        es_favorito = self.diccionario.toggle_favorito(palabra)
        texto = "★ Quitar de favoritos" if es_favorito else "☆ Agregar a favoritos"
        boton.config(text=texto)
        self.actualizar_lista_favoritos()
        
        if es_favorito:
            self.status_bar.config(text=f"⭐ '{palabra}' añadido a favoritos", foreground="blue")
        else:
            self.status_bar.config(text=f"☆ '{palabra}' eliminado de favoritos", foreground="orange")
        
        # Programar cierre del frame
        self.ventana.after(2000, frame.destroy)
    
    def actualizar_sugerencias(self, sugerencias):
        """Actualiza lista de sugerencias"""
        self.lista_sugerencias.delete(0, tk.END)
        for sug in sugerencias:
            self.lista_sugerencias.insert(tk.END, sug)
    
    def actualizar_lista_favoritos(self):
        """Actualiza lista de favoritos"""
        self.lista_favoritos.delete(0, tk.END)
        for palabra in sorted(self.diccionario.favoritos):
            self.lista_favoritos.insert(tk.END, palabra)
    
    def buscar_desde_lista(self, lista):
        """Busca palabra seleccionada en una lista"""
        seleccion = lista.curselection()
        if seleccion:
            palabra = lista.get(seleccion[0])
            self.entry_palabra.delete(0, tk.END)
            self.entry_palabra.insert(0, palabra)
            self.buscar()
    
    def mostrar_historial(self):
        """Muestra ventana de historial"""
        ventana = tk.Toplevel(self.ventana)
        ventana.title("Historial de búsquedas")
        ventana.geometry("700x500")
        
        texto = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, font=("Arial", 10))
        texto.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        historial = self.diccionario.obtener_historial()
        if not historial:
            texto.insert(tk.END, "No hay búsquedas en el historial")
        else:
            for i, entrada in enumerate(historial[:100], 1):
                texto.insert(tk.END, f"{i}. {entrada['palabra'].upper()}\n")
                texto.insert(tk.END, f"   📖 {entrada['definicion']}\n")
                texto.insert(tk.END, f"   🔍 {entrada['fuente']}\n")
                texto.insert(tk.END, f"   📅 {entrada['fecha']}\n")
                texto.insert(tk.END, "-"*60 + "\n")
        
        texto.config(state=tk.DISABLED)
    
    def mostrar_favoritos(self):
        """Muestra ventana de favoritos"""
        ventana = tk.Toplevel(self.ventana)
        ventana.title("Mis favoritos")
        ventana.geometry("500x400")
        
        frame = ttk.Frame(ventana, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="⭐ Palabras favoritas", font=("Arial", 12, "bold")).pack()
        
        lista = tk.Listbox(frame, font=("Arial", 11))
        lista.pack(fill=tk.BOTH, expand=True, pady=10)
        
        for palabra in sorted(self.diccionario.favoritos):
            lista.insert(tk.END, palabra)
        
        def buscar_favorito():
            selec = lista.curselection()
            if selec:
                palabra = lista.get(selec[0])
                self.entry_palabra.delete(0, tk.END)
                self.entry_palabra.insert(0, palabra)
                self.buscar()
                ventana.destroy()
        
        ttk.Button(frame, text="🔍 Buscar", command=buscar_favorito).pack()
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas de uso de APIs"""
        estadisticas, total = self.diccionario.obtener_estadisticas()
        
        ventana = tk.Toplevel(self.ventana)
        ventana.title("Estadísticas de APIs")
        ventana.geometry("500x450")
        
        texto = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, font=("Arial", 10))
        texto.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        texto.insert(tk.END, "📊 ESTADÍSTICAS DE USO DE APIs\n", ("titulo",))
        texto.insert(tk.END, "="*50 + "\n\n")
        
        if total == 0:
            texto.insert(tk.END, "Aún no hay búsquedas registradas.\n")
            texto.insert(tk.END, "¡Realiza tu primera búsqueda para ver estadísticas!")
        else:
            for api, count in sorted(estadisticas.items(), key=lambda x: x[1], reverse=True):
                porcentaje = (count / total) * 100
                texto.insert(tk.END, f"{api.upper()}\n")
                texto.insert(tk.END, f"   Búsquedas: {count} ({porcentaje:.1f}%)\n")
                texto.insert(tk.END, f"   {'█' * int(porcentaje/2)}{'░' * (50 - int(porcentaje/2))}\n\n")
            
            texto.insert(tk.END, f"\n📈 TOTAL DE BÚSQUEDAS: {total}\n")
        
        texto.insert(tk.END, "\n" + "="*50 + "\n")
        texto.insert(tk.END, "💡 Las estadísticas ayudan a ver qué API es más efectiva")
        
        # Configurar tags
        texto.tag_config("titulo", font=("Arial", 12, "bold"))
        texto.config(state=tk.DISABLED)
    
    def mostrar_info_apis(self):
        """Muestra información detallada de todas las APIs"""
        info = """
        📚 INFORMACIÓN DE APIs DISPONIBLES
        
        🌟 AUTO (Automático - Recomendado)
        • Prueba todas las APIs en orden de prioridad
        • Usa la primera que encuentre definición
        • Mejor relación calidad/velocidad
        
        📖 WORDNIK
        • Soporte: Español e Inglés
        • Calidad: Alta
        • Requiere: API key gratuita (https://www.wordnik.com/signup)
        • Límite: 1000 consultas/día
        
        🌐 FREE DICTIONARY API
        • Soporte: Inglés
        • Calidad: Media-Alta
        • Requiere: Sin clave
        • Límite: Sin límite
        
        🤖 LINGUAROBOT
        • Soporte: Multilingüe
        • Calidad: Media
        • Requiere: Sin clave
        • Límite: 10 consultas/hora
        
        📚 GLOSBE
        • Soporte: Multilingüe
        • Calidad: Media
        • Requiere: API key (https://glosbe.com/api)
        • Límite: 1000 consultas/día
        
        💾 MYMEMORY
        • Soporte: Contextual/Traducciones
        • Calidad: Media
        • Requiere: Sin clave
        • Límite: 1000 consultas/día
        
        💿 LOCAL
        • Soporte: Personalizado
        • Calidad: Definida por usuario
        • Requiere: Diccionario propio
        • Límite: Ilimitado
        
        ⚙️ CÓMO CONFIGURAR API KEYS:
        1. Edita el archivo del programa
        2. Busca "ConfiguracionAPI"
        3. Añade tus claves en WORDNIK_API_KEY y GLOSBE_API_KEY
        """
        
        ventana = tk.Toplevel(self.ventana)
        ventana.title("Información de APIs")
        ventana.geometry("600x550")
        
        texto = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, font=("Consolas", 10))
        texto.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        texto.insert(tk.END, info)
        texto.config(state=tk.DISABLED)
    
    def agregar_palabra(self):
        """Añade palabra al diccionario local"""
        ventana = tk.Toplevel(self.ventana)
        ventana.title("Agregar definición local")
        ventana.geometry("550x350")
        
        ttk.Label(ventana, text="Palabra:", font=("Arial", 10, "bold")).pack(pady=5)
        entry_palabra = ttk.Entry(ventana, font=("Arial", 11), width=50)
        entry_palabra.pack(pady=5)
        
        ttk.Label(ventana, text="Definición:", font=("Arial", 10, "bold")).pack(pady=5)
        texto_def = scrolledtext.ScrolledText(ventana, height=10, width=60)
        texto_def.pack(pady=5)
        
        def guardar():
            palabra = entry_palabra.get().strip()
            definicion = texto_def.get(1.0, tk.END).strip()
            
            if not palabra or not definicion:
                messagebox.showwarning("Advertencia", "Completa ambos campos")
                return
            
            self.diccionario.agregar_definicion_local(palabra, definicion)
            messagebox.showinfo("Éxito", f"✓ '{palabra}' agregada al diccionario local")
            ventana.destroy()
        
        ttk.Button(ventana, text="💾 Guardar", command=guardar).pack(pady=10)
    
    def exportar_diccionario(self):
        """Exporta diccionario local"""
        formato = messagebox.askquestion("Exportar", "¿Exportar como JSON? (No = TXT)")
        formato = "json" if formato == "yes" else "txt"
        
        archivo = self.diccionario.exportar_definiciones(formato)
        if archivo:
            messagebox.showinfo("Éxito", f"✅ Diccionario exportado a:\n{archivo}")
            self.status_bar.config(text=f"Exportado: {archivo}")
    
    def ejecutar(self):
        """Inicia la aplicación"""
        self.ventana.mainloop()


# ==================== PUNTO DE ENTRADA ====================

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║     BUSCADOR DE DEFINICIONES MULTI-API v2.0                  ║
    ║     Soporta 6 APIs diferentes + selección manual             ║
    ╚══════════════════════════════════════════════════════════════╝
    
    📋 APIs disponibles:
    1. Wordnik (Español/Inglés) - Requiere API key
    2. Free Dictionary (Inglés) - Sin clave
    3. LinguaRobot (Multilingüe) - Sin clave
    4. Glosbe (Multilingüe) - Requiere API key
    5. MyMemory (Contextual) - Sin clave
    6. Diccionario Local - Personalizable
    
    💡 Para usar Wordnik o Glosbe:
    - Edita ConfiguracionAPI.WORDNIK_API_KEY
    - Edita ConfiguracionAPI.GLOSBE_API_KEY
    - Regístrate gratis en sus sitios web
    
    🚀 Iniciando aplicación...
    """)
    
    app = AplicacionMultiAPI()
    app.ejecutar()
