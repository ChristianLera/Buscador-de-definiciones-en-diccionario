# Buscador de Definiciones Multi-API

**Versión 2.0**  
Un diccionario multilingüe con soporte para **6 APIs diferentes** y selección manual de fuente.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Características

- 🔍 **6 APIs integradas**:
  - Wordnik (Español/Inglés)
  - Free Dictionary API (Inglés)
  - LinguaRobot (Multilingüe)
  - Glosbe (Multilingüe)
  - MyMemory (Contextual/Traducciones)
  - Diccionario Local personalizable

- 🤖 **Modo automático** que prueba todas las APIs en orden de prioridad
- ⭐ **Favoritos** para guardar palabras importantes
- 📜 **Historial** de búsquedas con fechas
- 📊 **Estadísticas** de uso por API
- 💾 **Diccionario local editable** (persistente en JSON)
- 🔄 **Sugerencias** para palabras similares
- 📤 **Exportación** a JSON/TXT

## 📋 Requisitos

- **Python 3.7 o superior**
- **Conexión a Internet** (para APIs externas)
- Librería `requests`

## 🚀 Ejecución Rápida

### Windows (Batch)
```batch
ejecutar.bat
```

### Windows (PowerShell)
```powershell
.\ejecutar.ps1
```

### Manual
```bash
# 1. Instalar dependencia (solo la primera vez)
pip install requests

# 2. Ejecutar
python BuscadorDeDefiniciones.py
```

## ⚙️ Configuración de APIs (Opcional)

Algunas APIs requieren registro gratuito. Sin claves, funcionan con límites reducidos.

### Wordnik (Recomendada para español)
1. Regístrate en [Wordnik](https://www.wordnik.com/signup)
2. Obtén tu API Key
3. Edita el archivo `BuscadorDeDefiniciones.py` y añade:

```python
WORDNIK_API_KEY = "tu_clave_aqui"
```

### Glosbe
1. Regístrate en [Glosbe API](https://glosbe.com/api)
2. Añade tu clave en:

```python
GLOSBE_API_KEY = "tu_clave_aqui"
```

## 🎮 Uso

1. **Selecciona una API** del menú desplegable (o usa "Auto")
2. **Escribe una palabra** y presiona "BUSCAR" o Enter
3. **Resultados**: Definición, fuente, sugerencias
4. **Favoritos**: Botón flotante para guardar palabras
5. **Historial**: Accede desde el panel superior

## 📁 Estructura de Archivos

```
BuscadorDeDefiniciones/
│
├── BuscadorDeDefiniciones.py   # Programa principal
├── ejecutar.bat                # Ejecutar en Windows (Batch)
├── ejecutar.ps1                # Ejecutar en Windows (PowerShell)
├── README.md                   # Documentación
│
├── diccionario_local.json      # Se crea automáticamente
├── historial_busquedas.json    # Se crea automáticamente
└── favoritos.json              # Se crea automáticamente
```

## 🔧 Solución de Problemas

| Problema | Solución |
|----------|----------|
| "Python no está instalado" | Descarga Python desde python.org |
| "No module named requests" | Ejecuta: `pip install requests` |
| APIs no responden | Espera unos segundos o cambia de API |
| Error SSL | `pip install --upgrade certifi` |

## 📊 APIs Disponibles

| API | Idioma | Requiere clave | Límite |
|-----|--------|----------------|--------|
| Wordnik | Español/Inglés | Sí (gratis) | 1000/día |
| Free Dictionary | Inglés | No | Ilimitado |
| LinguaRobot | Multilingüe | No | 10/hora |
| Glosbe | Multilingüe | Sí (gratis) | 1000/día |
| MyMemory | Contextual | No | 1000/día |
| Local | Personalizado | No | Ilimitado |

## 🛠️ Personalización

### Añadir al diccionario local
Usa el botón **"➕ Agregar palabra"** en la interfaz.

### Cambiar prioridad de APIs
Edita el método `buscar_automatico()` en `DiccionarioMultiAPI`.

## 📜 Licencia

MIT License - Libre para uso personal y comercial.

## 👤 Autor

**Christian Lera**

---

⭐ ¿Te gusta? ¡Dale una estrella al repositorio!
