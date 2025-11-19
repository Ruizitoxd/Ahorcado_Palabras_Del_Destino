🎮 Ahorcado — Videojuego en Python (Pygame)

Este es un juego del Ahorcado desarrollado en Python + Pygame.
Incluye imágenes, sonidos (si aplica), y archivos JSON para manejar palabras y puntuaciones.

Este documento explica paso a paso cómo instalar y ejecutar el juego en cualquier computador, incluso si el usuario no tiene Python instalado.

🚀 Instalación
✔ Opción 1 — Ejecutar la versión ya compilada (recomendada)

Esta es la forma más sencilla para el usuario final.

Descarga la carpeta completa del juego desde la sección de releases (o donde la compartas).

Extrae el archivo .zip (clic derecho → Extraer aquí).

Abre la carpeta extraída. Dentro encontrarás algo como:

Ahorcado/
│
├── main.exe
├── puntuacion.json
├── palabras.json
├── icono.ico
│
└── assets/
├── fondo_facil.jpg
├── fondo_dificil.jpg
├── hangman0.png
├── hangman1.png
├── ...

Haz doble clic en main.exe

¡El juego se abrirá inmediatamente! 🎉

Nota: No elimines ni muevas la carpeta assets/ o los archivos .json, porque el juego los necesita para funcionar.

✔ Opción 2 — Ejecutar el código fuente (para desarrolladores)

Si quieres ejecutar o modificar el código Python original:

1️⃣ Instala Python 3.10 o superior

Descargar desde:
https://www.python.org/downloads/

Asegúrate de marcar:
✔ Add Python to PATH

2️⃣ Instala dependencias

Abre una terminal dentro del proyecto y ejecuta:

pip install pygame

3️⃣ Ejecuta el juego

En la misma terminal:

python main.py

🛠 Cómo fue generado el .EXE (información técnica)

El ejecutable fue creado usando auto-py-to-exe (que internamente usa PyInstaller).

Para reproducir la compilación:

pip install auto-py-to-exe
auto-py-to-exe

Configuración usada:

Script: main.py

One Directory (carpeta con el exe dentro)

Additional Files:

assets/

palabras.json

puntuacion.json

icono.ico

Icono: icono.ico

Esto genera una carpeta en:

/dist/main/

Para distribución se comparte esa carpeta completa.

📁 Estructura del proyecto
Ahorcado/
│
├── main.py
├── palabras.json
├── puntuacion.json
├── README.md
│
├── assets/
│ ├── hangman0.png
│ ├── hangman1.png
│ ├── hangman2.png
│ ├── fondo_facil.jpg
│ ├── fondo_dificil.jpg
│ ├── ...
│
└── icono.ico

🧩 Créditos

Desarrollado por: [Tu nombre]

Lenguaje: Python

Librería principal: Pygame

❓ Preguntas o problemas

Si tienes alguna duda o encuentras un error, puedes contactarme o abrir un issue en el repositorio.
