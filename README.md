# 🎮 Ahorcado — Videojuego en Python (Pygame)

Este es un juego del **Ahorcado** desarrollado en **Python + Pygame**.  
Incluye imágenes y archivos JSON para manejar palabras y puntuaciones.

Este documento explica paso a paso **cómo instalar y ejecutar el juego**, tanto en versión compilada como desde el código fuente.

---

# 🚀 Instalación

## ✔ Opción 1 — Ejecutar la versión ya compilada (recomendada)

Esta es la forma más sencilla para el usuario final:

1. Descarga la carpeta completa del juego desde la sección de **Releases**
2. Extrae el archivo `.zip`.
3. Abre la carpeta extraída. Deberías ver algo como:

```bash
Ahorcado/
│
├── main.exe
└── _internal/
```

4. **Haz doble clic en `main.exe`.**
5. ¡El juego iniciará automáticamente! 🎉

> **Nota:** No elimines ni muevas la carpeta `internal/`; son necesarios para el funcionamiento del juego.

---

## ✔ Opción 2 — Ejecutar el código fuente (para desarrolladores)

Si deseas modificar el juego o ejecutarlo directamente en Python:

### 1️⃣ Instala Python 3.10 o superior

Descarga desde:  
https://www.python.org/downloads/

Asegúrate de marcar:  
✔ **Add Python to PATH**

---

### 2️⃣ Instala dependencias

En una terminal ubicada dentro del proyecto ejecuta:

```bash
pip install pygame
```

### 3️⃣ Ejecuta el juego

En una terminal ubicada dentro del proyecto ejecuta:

```bash
python main.py
```

## 🛠 Cómo fue generado el ejecutable (.EXE)

El ejecutable se creó usando auto-py-to-exe (que utiliza PyInstaller internamente).

Para generar el ejecutable nuevamente:

```bash
pip install pygame
```

Configuración utilizada:

-   Script: main.py

-   One Directory (carpeta que contiene el exe y los recursos)

-   Additional Files incluidos:

    -   Carpeta assets/

    -   palabras.json

    -   puntuacion.json

    -   icono.ico

-   Icon: icono.ico

El resultado se ubica en:

```bash
/dist/main/
```

## 📁 Estructura del proyecto

```bash
Ahorcado/
│
├── main.py
├── palabras.json
├── puntuacion.json
├── README.md
├── assets/
│   ├── hangman0.png
│   ├── hangman1.png
│   ├── hangman2.png
│   ├── hangman3.png
│   ├── hangman4.png
│   ├── hangman5.png
│   ├── hangman6.png
│   ├── fondo_facil.jpg
│   ├── fondo_dificil.jpg
│   ├── fondo_hollow.png
│   └── nube.png
└── icono.ico
```

## 🧩 Créditos

-   Desarrollado por: Oscar David Macias Palomino y Juan Camilo Ruiz Osorio
-   Lenguaje: Python
-   Librería principal: Pygame

## ❓ Problemas o soporte

Si tienes dudas o encuentras errores, abre un issue o contáctame.

-   jruiz32@udi.edu.co

*   omacias1@udi.edu.co
