# hola_mundo

Proyecto Django 5.2.17 con una vista de bienvenida y el panel de administración. En el **login del admin** se pueden elegir **Español** e **English** con pestañas; el resto de la interfaz del admin usa las traducciones oficiales de Django.

---

## Estructura del proyecto

```
hola_mundo/
├── manage.py                 # Punto de entrada de comandos Django
├── db.sqlite3                # Base de datos local
├── .venv/                    # Entorno virtual (Python 3.11)
├── templates/
│   └── admin/
│       └── login.html        # Login del admin (plantilla personalizada)
├── hola/                     # Aplicación principal
│   ├── views.py              # Vista "hola" de la raíz
│   ├── admin.py
│   ├── models.py
│   ├── apps.py
│   └── tests.py
└── web_project/              # Configuración del proyecto
    ├── settings.py
    ├── urls.py
    ├── wsgi.py
    └── asgi.py
```

---

## Qué se modificó (detalle)

Esta sección describe **solo los cambios** hechos para el selector de idioma en el login del admin. El resto del proyecto (vista `hola`, SQLite, apps por defecto) se mantiene.

### 1. `web_project/settings.py`

#### Middleware `LocaleMiddleware`

Se insertó `django.middleware.locale.LocaleMiddleware` **después** de `SessionMiddleware` y **antes** de `CommonMiddleware`.

Ese orden es el que exige Django: el idioma se lee de la cookie de sesión/idioma y se activa en cada petición **antes** de que se resuelvan URLs y plantillas.

Sin este middleware, `set_language` guardaría la cookie pero el admin seguiría en el idioma por defecto.

#### Plantillas del proyecto

```python
'DIRS': [BASE_DIR / 'templates'],
```

Django busca primero en `templates/` (raíz del repo). Así, `templates/admin/login.html` **reemplaza** el login por defecto de `django.contrib.admin` sin tocar el paquete instalado.

#### Procesador de contexto i18n

```python
'django.template.context_processors.i18n',
```

Expone en las plantillas variables como `LANGUAGE_CODE` y `LANGUAGES`. El login también usa `{% get_current_language %}` del tag `i18n`.

#### Idiomas admitidos

| Ajuste | Valor | Efecto |
|--------|--------|--------|
| `LANGUAGE_CODE` | `'es'` | Idioma por defecto si no hay cookie |
| `LANGUAGES` | `('es', 'Español')`, `('en', 'English')` | Únicos idiomas que `set_language` acepta |
| `USE_I18N` | `True` | Traducciones activas (ya venía así) |

Django trae catálogos para el admin en español e inglés. No hace falta generar archivos `.po` propios para traducir Usuario, Contraseña, Iniciar sesión, etc.

---

### 2. `web_project/urls.py`

Se añadió la vista oficial de cambio de idioma:

```python
from django.views.i18n import set_language

path("i18n/setlang/", set_language, name="set_language"),
```

- **Método:** solo `POST` (las pestañas envían un formulario).
- **Campos:** `language` (`es` o `en`) y `next` (URL a la que volver, el propio login).
- **Efecto:** valida el código contra `LANGUAGES`, escribe la cookie `django_language` y redirige a `next`.
- **Nombre de URL:** `set_language`, usado en la plantilla con `{% url 'set_language' %}`.

Rutas que no cambiaron:

| Ruta | Vista |
|------|--------|
| `/` | `hola.views.hola` |
| `/admin/` | Admin de Django |

---

### 3. `templates/admin/login.html` (archivo nuevo)

Copia del login estándar del admin, con estas adiciones:

#### Pestañas de idioma

Dos formularios `POST` encima del formulario de usuario/contraseña:

1. **Español** → `language=es`
2. **English** → `language=en`

Cada uno incluye:

- `{% csrf_token %}` (obligatorio)
- `next` = `{{ request.get_full_path }}` para volver al login (incluye `?next=/admin/` si venía de ahí)
- clase CSS `active` y `aria-selected` según `{% get_current_language as LANGUAGE_CODE %}`

Al pulsar una pestaña:

1. El navegador hace `POST /i18n/setlang/`
2. Django guarda `django_language`
3. Responde `302` hacia el login
4. El login se vuelve a pintar ya traducido (título, etiquetas, botón)

#### Estilos (`.lang-tabs`)

Pestañas a ancho completo, borde inferior y color de acento del admin (`--link-fg`) en la pestaña activa. Compatibles con el tema claro/oscuro del admin.

#### Textos del formulario

Siguen usando `{% translate %}` / `{% blocktranslate %}`. Django elige el catálogo según el idioma activo; no hay cadenas hardcodeadas en español o inglés salvo los nombres de las pestañas (**Español** / **English**), que se dejan fijos a propósito.

---

## Flujo del cambio de idioma

```
Usuario pulsa "English"
        │
        ▼
POST /i18n/setlang/  (language=en, next=/admin/login/?next=/admin/)
        │
        ▼
LocaleMiddleware + cookie django_language=en
        │
        ▼
Redirect GET /admin/login/?next=/admin/
        │
        ▼
Login en inglés (Username, Password, Log in)
```

La cookie persiste en el navegador: al recargar o entrar otra vez al admin, se mantiene el último idioma elegido.

---

## Requisitos

- Python 3.11 (el del entorno `.venv`)
- Django 5.2.17 (ya instalado en `.venv`)

---

## Comandos para levantar el proyecto

Todos se ejecutan desde la raíz del repositorio: `/home/gabriel/hola_mundo`.

### 1. Entrar al directorio

```bash
cd ~/hola_mundo
```

### 2. Activar el entorno virtual

```bash
source .venv/bin/activate
```

El prompt debería mostrar `(.venv)`. Para salir después:

```bash
deactivate
```

Si el entorno no existiera, crearlo e instalar Django:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install "Django==5.2.17"
```

### 3. Aplicar migraciones (primera vez o si cambia el esquema)

```bash
python manage.py migrate
```

Crea/actualiza `db.sqlite3` (usuarios, sesiones, admin, etc.).

### 4. Crear un superusuario (para entrar al admin)

Solo hace falta una vez, si aún no hay usuario:

```bash
python manage.py createsuperuser
```

Pide nombre de usuario, email (opcional) y contraseña.

### 5. Arrancar el servidor de desarrollo

```bash
python manage.py runserver
```

Queda escuchando en:

- Inicio: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Admin / login: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

Para pararlo: `Ctrl+C`.

Otro puerto o interfaz:

```bash
python manage.py runserver 0.0.0.0:8000
python manage.py runserver 8080
```

### 6. Comprobar que Django está bien configurado (opcional)

```bash
python manage.py check
```

---

## Uso del login bilingüe

1. Abrir [http://127.0.0.1:8000/admin/login/](http://127.0.0.1:8000/admin/login/).
2. Por defecto se ve en **español** (`LANGUAGE_CODE = 'es'`).
3. Pulsar **English** o **Español**.
4. Iniciar sesión con el superusuario.

Tras el login, el resto del admin también respeta el idioma de la cookie.

---

## Notas

- `DEBUG = True` y `ALLOWED_HOSTS = []` sirven para desarrollo local (`localhost` / `127.0.0.1`). No usar este servidor en producción.
- `SECRET_KEY` está en `settings.py` como la generó `startproject`; en un despliegue real debe ser secreta y no versionarse.
- No se añadieron archivos de traducción propios: se usan los de `django.contrib.admin`.
- `runserver` recarga solo al cambiar código; si el servidor ya estaba en marcha, las pestañas deberían verse al refrescar el navegador.
