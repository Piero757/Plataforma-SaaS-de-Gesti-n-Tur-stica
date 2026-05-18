# 🚀 GUÍA DE INSTALACIÓN RÁPIDA DESDE USB (PC SERVIDOR)
Esta guía detalla los pasos exactos para instalar, configurar y desplegar el sistema local **TurismoERP** en la PC que actuará como Servidor, asegurando que se entregue una base de datos limpia (en blanco) para el cliente final, y conectando los celulares y demás computadoras de la red local.

---

### 📋 REQUISITO PREVIO EN LA COMPUTADORA DE TRABAJO (LAPTOP)
Antes de copiar la carpeta del proyecto a tu USB:
1. Asegúrate de que la carpeta del proyecto `Plataforma SaaS de Gestión Turística` esté completa (debe incluir la subcarpeta `venv`).
2. **Recomendación:** Puedes borrar el archivo `db.sqlite3` de tu laptop antes de copiar la carpeta al USB, o borrarlo directamente en la PC Servidor después de pegarlo.

---

### PASO 1: INSTALAR PYTHON EN LA PC SERVIDOR
En la computadora que funcionará como Servidor, abre el navegador y descarga Python:
*   **Enlace de descarga oficial:** https://www.python.org/downloads/ (se recomienda la versión estable 3.12.x).
*   Ejecuta el instalador descargado (`python-3.12.x-amd64.exe`).
*   ⚠️ **PASO CRÍTICO (MUY IMPORTANTE):** En la primera ventana del asistente, abajo del todo, debes marcar obligatoriamente la casilla que dice:
    `[✓] Add python.exe to PATH`
*   Haz clic en **"Install Now"** (Instalar ahora). Al finalizar, presiona **"Close"**.

---

### PASO 2: PEGAR EL PROYECTO DESDE TU USB
1. Conecta tu memoria USB en la PC Servidor.
2. Copia la carpeta completa del sistema (`Plataforma SaaS de Gestión Turística`).
3. Abre el explorador de archivos del servidor, ve al **Disco Local C:** y pega la carpeta allí.
4. Asegúrate de que la ruta final quede exactamente así:
   `C:\Plataforma SaaS de Gestión Turística` (con la carpeta `venv` adentro).

---

### PASO 3: LIMPIAR LA BASE DE DATOS E INICIAR DESDE CERO (CRÍTICO)
Para garantizar que tu cliente reciba un sistema limpio (en blanco), libre de tus registros y datos de prueba:

1.  **Eliminar Base de Datos Anterior:**
    *   Entra a `C:\Plataforma SaaS de Gestión Turística`.
    *   Busca el archivo **`db.sqlite3`** (si existe) y **bórralo** (elimínalo por completo).
2.  **Abrir Consola de Comandos (CMD):**
    *   Haz clic en la barra de direcciones superior del explorador de archivos de Windows (donde dice `C:\Plataforma SaaS de Gestión Turística`).
    *   Escribe **`cmd`** y presiona **Enter**. Se abrirá una ventana negra de comandos apuntando exactamente a tu carpeta.
3.  **Construir Estructura Nueva:**
    *   Escribe el siguiente comando y presiona **Enter**:
        ```cmd
        venv\Scripts\python manage.py migrate
        ```
    *   *El sistema creará un archivo `db.sqlite3` totalmente nuevo y generará todas las tablas en blanco al instante.*
4.  **Crear Usuario Administrador Oficial:**
    *   Escribe el siguiente comando y presiona **Enter**:
        ```cmd
        venv\Scripts\python manage.py createsuperuser
        ```
    *   La terminal te pedirá los datos del nuevo administrador para tu cliente:
        *   **Username:** Escribe el nombre de usuario (ejemplo: `admin`) y presiona Enter.
        *   **Email:** Déjalo en blanco y presiona Enter.
        *   **Password:** Escribe la contraseña y presiona Enter *(Nota: por seguridad no se verá lo que escribes, tú solo ingrésala)*.
        *   **Password (again):** Repite la misma contraseña y presiona Enter.

---

### PASO 4: CREAR EL BOTÓN DE ARRANQUE EN EL ESCRITORIO
Crearemos un acceso directo para que tu cliente inicie todo el sistema local con un simple doble clic:

1. Ve al escritorio de la PC Servidor.
2. Haz clic derecho en un espacio vacío -> **Nuevo** -> **Documento de texto**.
3. Abre el archivo de texto nuevo y pega este código exacto:
   ```bat
   @echo off
   title Iniciando Servidor TurismoERP...
   cd /d "C:\Plataforma SaaS de Gestión Turística"
   start /b venv\Scripts\python manage.py runserver 0.0.0.0:8000
   timeout /t 3 >nul
   start http://localhost:8000/
   exit
   ```
4. Haz clic en **Archivo** -> **Guardar como...**
5. En **Nombre**, escribe exactamente: `Iniciar_Sistema.bat` *(asegúrate de borrar el `.txt` final)*.
6. En **Tipo**, selecciona **Todos los archivos (*.*)**.
7. Guárdalo directamente en el Escritorio y borra el archivo de texto vacío original.

---

### PASO 5: HABILITAR EL PUERTO 8000 EN EL FIREWALL
Esto permite que los celulares y las demás computadoras se conecten a la PC Servidor sin que el Firewall de Windows bloquee la conexión:

1. Abre el menú inicio del servidor, busca **Panel de Control** y ábrelo.
2. Ve a **Sistema y seguridad** -> **Firewall de Windows Defender**.
3. Haz clic en **Configuración avanzada** (columna de la izquierda).
4. Selecciona **Reglas de entrada** (arriba a la izquierda) y haz clic en **Nueva regla...** (columna de la derecha).
5. Selecciona **Puerto** y haz clic en Siguiente.
6. Selecciona **TCP** y en "Puertos locales específicos" escribe: `8000`. Haz clic en Siguiente.
7. Selecciona **Permitir la conexión** y haz clic en Siguiente.
8. Deja las tres casillas marcadas (Dominio, Privado, Público) y haz clic en Siguiente.
9. Nómbralo **`TurismoERP`** y haz clic en **Finalizar**. Cierra todas las ventanas.

---

### PASO 6: OBTENER LA IP DEL SERVIDOR Y CONECTAR LAS OTRAS PC
1. En el Servidor, haz doble clic en tu nuevo icono del escritorio **`Iniciar_Sistema.bat`**. Verás que a los 3 segundos se abre automáticamente la aplicación web.
2. Abre la consola de comandos de Windows (`cmd`), escribe el comando `ipconfig` y presiona **Enter**.
3. Busca la línea que dice **Dirección IPv4** (por ejemplo: `192.168.1.15`). Anota esa IP.
4. **En las otras computadoras y celulares clientes (conectados al mismo Wi-Fi):**
   *   Abre el navegador (Google Chrome o Safari) y navega a la IP del servidor seguida del puerto `:8000`.
   *   **Ejemplo:** `http://192.168.1.15:8000/`
5. **Para guardarlo como Aplicación Nativa (PWA):**
   *   **En PC de escritorio clientes:** En Chrome, haz clic en los tres puntos de arriba a la derecha -> **Guardar y compartir** -> **Crear acceso directo...**, escribe el nombre "TurismoERP" y marca la casilla **"Abrir como ventana"**.
   *   **En Celulares (iPhone/Safari):** Presiona el botón **Compartir** -> **"Agregar a la pantalla de inicio"**.
   *   **En Celulares (Android/Chrome):** Presiona los tres puntos -> **"Agregar a la pantalla principal"** o **"Instalar aplicación"**.
