import unicodedata
import pygame
import random
import json
import time
import sys
import os

pygame.init()

# --- CONFIGURACIÓN BASE ---
ANCHO_BASE, ALTO_BASE = 1920, 1080
ANCHO, ALTO = 1280, 720
VENTANA = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
pygame.display.set_caption("Juego del Ahorcado")

# --- COLORES ---
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)
GRIS = (200, 200, 200)
GRIS_OSCURO = (150, 150, 150)
VERDE = (0, 200, 0)

# --- FUENTES ---
def fuente_responsive(tamaño):
    # Tamaño base escalado por ANCHO respecto a ANCHO_BASE, con mínimo 14
    size = max(14, int(tamaño * (ANCHO / ANCHO_BASE)))
    return pygame.font.SysFont("comicsans", size)

FUENTE = fuente_responsive(40)
FUENTE_PALABRA = fuente_responsive(70)

# --- CARGAR PALABRAS DESDE JSON ---
with open("palabras.json", "r", encoding="utf-8") as archivo:
    DATA_PALABRAS = json.load(archivo)
# Normalizar a mayúsculas para evitar discrepancias
for k in list(DATA_PALABRAS.keys()):
    DATA_PALABRAS[k] = [p.upper() for p in DATA_PALABRAS[k]]

# --- CARGAR IMÁGENES (originales) ---
IMAGENES_ORIG = []
ruta_assets = os.path.join(os.path.dirname(__file__), "assets")
for i in range(7):
    path_img = os.path.join(ruta_assets, f"hangman{i}.png")
    imagen = pygame.image.load(path_img).convert_alpha()
    IMAGENES_ORIG.append(imagen)

# IMAGENES que se usan en cada frame (escaladas)
IMAGENES = []

# --- VARIABLES GLOBALES ---
modo_pantalla_completa = False
clock = pygame.time.Clock()
FPS = 60

# --- FUNCIONES AUXILIARES ---
def escalar_imagen_desde_original(idx, escala):
    """Escala la imagen original en IMAGENES_ORIG[idx] con factor escala (float)."""
    orig = IMAGENES_ORIG[idx]
    ancho = max(1, int(orig.get_width() * escala))
    alto = max(1, int(orig.get_height() * escala))
    return pygame.transform.smoothscale(orig, (ancho, alto))

def actualizar_imagenes_por_tamano():
    """Recalcula IMAGENES escaladas según ANCHO/ALTO actuales."""
    global IMAGENES
    factor = min(ANCHO / ANCHO_BASE, ALTO / ALTO_BASE)
    # multiplica por un factor adicional para que la imagen no ocupe toda la pantalla
    escala_visual = max(0.15, factor * 0.6)
    IMAGENES = [escalar_imagen_desde_original(i, escala_visual) for i in range(len(IMAGENES_ORIG))]

# inicializar IMAGENES escaladas
actualizar_imagenes_por_tamano()

def dibujar_boton(texto, x, y, ancho, alto, color, color_texto, hover_color=None):
    """
    Dibuja un botón en coordenadas absolutas (enteros) y devuelve True si fue clickeado.
    x,y,ancho,alto deben estar en pixeles. Para hacerlo responsive, calcula estos con proporciones fuera.
    """
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    dentro = x < mouse[0] < x + ancho and y < mouse[1] < y + alto

    if dentro:
        pygame.draw.rect(VENTANA, hover_color or color, (x, y, ancho, alto), border_radius=8)
        if click[0] == 1:
            pygame.time.delay(120)
            return True
    else:
        pygame.draw.rect(VENTANA, color, (x, y, ancho, alto), border_radius=8)

    texto_render = FUENTE.render(texto, True, color_texto)
    VENTANA.blit(texto_render, (x + ancho/2 - texto_render.get_width()/2, y + alto/2 - texto_render.get_height()/2))
    return False

def redimensionar(nuevo_ancho, nuevo_alto, recrear_ventana=True):
    """
    Actualiza ANCHO/ALTO, ventana, fuentes e imágenes escaladas.
    Si recrear_ventana==False, NO llama a pygame.display.set_mode() (útil cuando ya cambiamos la ventana).
    """
    global ANCHO, ALTO, FUENTE, FUENTE_PALABRA, VENTANA
    try:
        ANCHO, ALTO = max(300, int(nuevo_ancho)), max(200, int(nuevo_alto))  # límites mínimos
        if recrear_ventana:
            # recrea la ventana sólo si es necesario
            VENTANA = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
        # actualizar fuentes y recursos dependientes del tamaño
        FUENTE = fuente_responsive(40)
        FUENTE_PALABRA = fuente_responsive(max(28, 70 * (ANCHO / ANCHO_BASE)))
        actualizar_imagenes_por_tamano()
        print(f"[redimensionar] ANCHO={ANCHO} ALTO={ALTO} recrear_ventana={recrear_ventana}")
    except Exception as e:
        print("[redimensionar] error:", e)

# crea las posiciones de las letras de forma responsive (2 filas de 13)
def crear_botones_letras():
    # radius y gap dependen del ancho
    radius = int(max(14, min(48, ANCHO / 45)))  # adaptativo
    gap = int(radius * 0.5)
    total_width = (2 * radius) * 13 + gap * 12
    inicioX = max(20, round((ANCHO - total_width) / 2))
    inicioY = ALTO - (radius * 4) - int(ALTO * 0.02)
    botones = []
    for i in range(26):
        x = inicioX + ((i % 13) * (2 * radius + gap)) + radius
        y = inicioY + ((i // 13) * (2 * radius + gap))
        botones.append([x, y, chr(65 + i), "activo", radius])
    return botones

# versión robusta de verificar_letra que acepta set o list
def verificar_letra(letra, palabra, letras_adivinadas, letras_falladas, boton):
    # Comparar letras ignorando tildes y mayúsculas/minúsculas
    letra_normalizada = quitar_tildes(letra.lower())
    palabra_normalizada = quitar_tildes(palabra.lower())

    if letra_normalizada in palabra_normalizada:
        # Agregar todas las letras de la palabra original que coinciden con la letra (sin tildes)
        for original in palabra:
            if quitar_tildes(original.lower()) == letra_normalizada:
                if isinstance(letras_adivinadas, set):
                    letras_adivinadas.add(original)
                else:
                    if original not in letras_adivinadas:
                        letras_adivinadas.append(original)
        boton[3] = "usada"
    else:
        if isinstance(letras_falladas, set):
            letras_falladas.add(letra)
        else:
            if letra not in letras_falladas:
                letras_falladas.append(letra)
        boton[3] = "fallo"

def mostrar_mensaje(texto, color, delay_ms=1500):
    pygame.time.delay(200)
    VENTANA.fill(BLANCO)
    # soporte para saltos de línea
    lineas = str(texto).split("\n")
    altura_total = sum(FUENTE_PALABRA.size(linea)[1] for linea in lineas) + (len(lineas)-1)*10
    y_inicio = ALTO/2 - altura_total/2
    for linea in lineas:
        mensaje = FUENTE_PALABRA.render(linea, True, color)
        VENTANA.blit(mensaje, (ANCHO/2 - mensaje.get_width()/2, y_inicio))
        y_inicio += mensaje.get_height() + 10
    pygame.display.update()
    pygame.time.delay(delay_ms)

def quitar_tildes(texto):
    """Elimina tildes y signos diacríticos del texto."""
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

# --- MENÚ PRINCIPAL ---
def menu_principal():
    corriendo = True
    while corriendo:
        VENTANA.fill(BLANCO)
        titulo_fuente = pygame.font.SysFont("comicsans", max(24, int(ANCHO * 0.06)))
        titulo = titulo_fuente.render("JUEGO DEL AHORCADO", True, NEGRO)
        VENTANA.blit(titulo, (ANCHO/2 - titulo.get_width()/2, ALTO*0.12))

        # calcular botones con proporciones
        btn_w = int(ANCHO * 0.32)
        btn_h = int(ALTO * 0.10)
        x_center = ANCHO/2 - btn_w/2
        y_jugar = int(ALTO * 0.42)

        if dibujar_boton("JUGAR", int(x_center), y_jugar, btn_w, btn_h, GRIS, NEGRO, (180,180,180)):
            dificultad = seleccionar_dificultad()
            if dificultad is not None:
                modo_desafio(dificultad)

        if dibujar_boton("CONFIGURACIÓN", int(x_center), y_jugar + btn_h + int(ALTO*0.03), btn_w, btn_h, GRIS, NEGRO, (180,180,180)):
            configuracion()

        if dibujar_boton("SALIR", int(x_center), y_jugar + 2*(btn_h + int(ALTO*0.03)), btn_w, btn_h, GRIS, NEGRO, (180,180,180)):
            pygame.quit()
            sys.exit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                redimensionar(event.w, event.h)

        pygame.display.update()
        clock.tick(FPS)

# --- CONFIGURACIÓN ---
def configuracion():
    """
    Menú de configuración. Al cambiar el modo de pantalla se llama a set_mode() una vez
    y luego a redimensionar(..., recrear_ventana=False) para recalcular fuentes e imágenes.
    """
    global modo_pantalla_completa, VENTANA, ANCHO, ALTO
    corriendo = True
    while corriendo:
        VENTANA.fill(BLANCO)
        titulo_fuente = fuente_responsive(60)
        titulo = titulo_fuente.render("CONFIGURACIÓN", True, NEGRO)
        VENTANA.blit(titulo, (ANCHO/2 - titulo.get_width()/2, ALTO*0.12))

        btn_w = int(ANCHO * 0.44)
        btn_h = int(ALTO * 0.10)
        x_center = ANCHO/2 - btn_w/2
        y = int(ALTO*0.4)

        if dibujar_boton("Pantalla completa" if not modo_pantalla_completa else "Modo ventana", int(x_center), y, btn_w, btn_h, GRIS, NEGRO, (180,180,180)):
            # toggle del modo completo
            modo_pantalla_completa = not modo_pantalla_completa
            try:
                if modo_pantalla_completa:
                    # Activar fullscreen — llamar a set_mode UNA vez
                    VENTANA = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    ANCHO, ALTO = VENTANA.get_size()
                    # No recreamos la ventana dentro de redimensionar, ya la cambiamos arriba
                    redimensionar(ANCHO, ALTO, recrear_ventana=False)
                    print("[configuracion] ahora FULLSCREEN:", ANCHO, ALTO)
                else:
                    # Volver a ventana redimensionable con tamaño por defecto
                    VENTANA = pygame.display.set_mode((1024, 640), pygame.RESIZABLE)
                    ANCHO, ALTO = VENTANA.get_size()
                    redimensionar(ANCHO, ALTO, recrear_ventana=False)
                    print("[configuracion] ahora VENTANA:", ANCHO, ALTO)
            except Exception as e:
                print("[configuracion] error al cambiar modo:", e)

        if dibujar_boton("← VOLVER",  int(ANCHO*0.03), ALTO - int(ALTO*0.12), int(ANCHO*0.18), int(ALTO*0.08), GRIS, NEGRO, (180,180,180)):
            corriendo = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                # Cuando el usuario redimensiona manualmente la ventana, redimensionar recrea la ventana.
                redimensionar(event.w, event.h, recrear_ventana=True)

        pygame.display.update()
        clock.tick(FPS)

# Seleccionar dificultad del juego (responsive)
def seleccionar_dificultad():
    corriendo = True
    dificultad = None
    while corriendo:
        VENTANA.fill(BLANCO)
        titulo_fuente = fuente_responsive(56)
        titulo = titulo_fuente.render("Selecciona la Dificultad", True, NEGRO)
        VENTANA.blit(titulo, (ANCHO / 2 - titulo.get_width() / 2, ALTO * 0.12))

        # --- Botones de dificultad centrados horizontal y verticalmente ---
        btn_w = int(ANCHO * 0.28)
        btn_h = int(ALTO * 0.11)
        espacio = int(ANCHO * 0.05)  # separación horizontal entre botones

        total_ancho = btn_w * 2 + espacio
        x_inicial = (ANCHO - total_ancho) // 2  # margen izquierdo del primer botón
        y_centro = (ALTO - btn_h) // 2 + int(ALTO * 0.08)  # ligeramente más abajo del centro

        # Coordenadas de los botones
        x_facil = x_inicial
        x_dificil = x_inicial + btn_w + espacio

        # --- Dibujo de los botones ---
        if dibujar_boton("FÁCIL", x_facil, y_centro, btn_w, btn_h, VERDE, BLANCO, (0, 150, 0)):
            dificultad = "facil"
            corriendo = False

        if dibujar_boton("DIFÍCIL", x_dificil, y_centro, btn_w, btn_h, ROJO, BLANCO, (180, 0, 0)):
            dificultad = "dificil"
            corriendo = False

        # --- Botón VOLVER (abajo a la izquierda) ---
        if dibujar_boton("← VOLVER", int(ANCHO * 0.03), ALTO - int(ALTO * 0.12), int(ANCHO * 0.18), int(ALTO * 0.08), GRIS, NEGRO, (180, 180, 180)):
            return None  # volver al menú principal

        # --- Eventos ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                redimensionar(event.w, event.h)

        pygame.display.update()
        clock.tick(FPS)

    return dificultad


# --- DIBUJAR JUEGO (mejorado responsive) ---
def dibujar(palabra, letras_adivinadas, letras, intentos, letras_falladas, tiempo_restante, palabra_actual, total_palabras, puntuacion):
    VENTANA.fill(BLANCO)

    # escala y obtener imagen
    imagen = IMAGENES[intentos]

    # posición de la imagen: arriba-izquierda con margen proporcional
    margen_x = int(ANCHO * 0.06)
    margen_y = int(ALTO * 0.06)
    imagen_x = margen_x
    imagen_y = margen_y
    VENTANA.blit(imagen, (imagen_x, imagen_y))

    # calcular donde colocar la palabra: debajo de la imagen
    imagen_bottom = imagen_y + imagen.get_height()
    palabra_y = imagen_bottom + int(ALTO * 0.03)
    mostrar_palabra = ""
    for letra in palabra:
        mostrar_palabra += letra + " " if letra in letras_adivinadas else "_ "
    # si la palabra es muy larga, reducir la fuente temporalmente
    texto_palabra = FUENTE_PALABRA.render(mostrar_palabra, True, NEGRO)
    if texto_palabra.get_width() > ANCHO * 0.9:
        # escala de fuente manual: usar FUENTE más pequeña
        font_temp = pygame.font.SysFont("comicsans", max(12, int(FUENTE_PALABRA.get_height() * 0.7)))
        texto_palabra = font_temp.render(mostrar_palabra, True, NEGRO)

    min_palabra_y = imagen_y + imagen.get_height() + 10
    final_palabra_y = max(palabra_y, min_palabra_y)
    VENTANA.blit(texto_palabra, (ANCHO/2 - texto_palabra.get_width()/2, final_palabra_y))

    # Dibujar letras (botones)
    for btn in letras:
        x, y, letra, estado, radius = btn
        if estado == "activo":
            pygame.draw.circle(VENTANA, NEGRO, (x, y), radius, 3)
            texto = FUENTE.render(letra, True, NEGRO)
        elif estado == "usada":
            pygame.draw.circle(VENTANA, GRIS_OSCURO, (x, y), radius)
            texto = FUENTE.render(letra, True, BLANCO)
        elif estado == "fallo":
            pygame.draw.circle(VENTANA, ROJO, (x, y), radius)
            texto = FUENTE.render(letra, True, BLANCO)
        VENTANA.blit(texto, (x - texto.get_width()/2, y - texto.get_height()/2))

    # Contador de palabras y tiempo (arriba)
    progreso = FUENTE.render(f"Palabra {palabra_actual}/{total_palabras}", True, NEGRO)
    VENTANA.blit(progreso, (int(ANCHO*0.02), int(ALTO*0.02)))

    minutos = int(tiempo_restante // 60)
    segundos = int(tiempo_restante % 60)
    color_tiempo = ROJO if tiempo_restante < 30 else NEGRO
    cronometro = FUENTE.render(f"Tiempo: {minutos:02}:{segundos:02}", True, color_tiempo)
    VENTANA.blit(cronometro, (ANCHO - cronometro.get_width() - int(ANCHO*0.02), int(ALTO*0.02)))

    # Mostrar puntuación en pantalla
    puntos_txt = FUENTE.render(f"Puntos: {puntuacion}", True, NEGRO)
    VENTANA.blit(puntos_txt, (ANCHO//2 - puntos_txt.get_width()//2, int(ALTO*0.02)))

    pygame.display.update()

# --- MODO DESAFÍO (10 palabras) ---
def modo_desafio(dificultad):
    palabras_origen = DATA_PALABRAS[dificultad]
    palabras_juego = random.sample(palabras_origen, min(10, len(palabras_origen)))
    letras_adivinadas_global = set()
    # tiempo base distinto por dificultad (ejemplo)
    tiempo_total = 360 if dificultad == "facil" else 240
    inicio_tiempo_total = time.time()
    palabra_actual = 1
    total_palabras = len(palabras_juego)

    # ⚡ Sistema de rachas y puntuación
    racha_rapida = 0
    puntuacion = 0

    for palabra in palabras_juego:
        letras_adivinadas = set()
        letras_falladas = []
        intentos = 0
        tiempo_inicio_palabra = time.time()

        # --- Recompensas según racha ---
        letras_extra = 0
        if racha_rapida >= 3:
            letras_extra = 3
        elif racha_rapida == 2:
            letras_extra = 2
        elif racha_rapida == 1:
            letras_extra = 1

        # Revelar letras gratis (por racha)
        posibles_letras = list(set(palabra))
        random.shuffle(posibles_letras)
        for i in range(min(letras_extra, len(posibles_letras))):
            letras_adivinadas.add(posibles_letras[i])

        # mantener la letra encadenada de palabras anteriores
        if letras_adivinadas_global:
            comunes = [c for c in letras_adivinadas_global if c in palabra]
            if comunes:
                letras_adivinadas.add(random.choice(comunes))

        letras = crear_botones_letras()
        jugando = True

        while jugando:
            tiempo_restante = tiempo_total - (time.time() - inicio_tiempo_total)
            if tiempo_restante <= 0:
                mostrar_mensaje(f"⏰ ¡Tiempo agotado!\nPuntuación final: {puntuacion}", ROJO)
                return

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.VIDEORESIZE:
                    redimensionar(event.w, event.h)
                    nuevo = crear_botones_letras()
                    estado_por_letra = {b[2]: b[3] for b in letras}
                    for b in nuevo:
                        if estado_por_letra.get(b[2]) is not None:
                            b[3] = estado_por_letra[b[2]]
                    letras = nuevo

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return menu_principal()
                    if event.unicode.isalpha():
                        letra = event.unicode.upper()
                        for boton in letras:
                            if boton[2] == letra and boton[3] == "activo":
                                verificar_letra(letra, palabra, letras_adivinadas, letras_falladas, boton)
                                if letra in palabra:
                                    puntuacion += 10
                                else:
                                    puntuacion -= 5

                if event.type == pygame.MOUSEBUTTONDOWN:
                    m_x, m_y = pygame.mouse.get_pos()
                    for boton in letras:
                        x, y, ltr, estado, radius = boton
                        if estado == "activo":
                            distancia = ((x - m_x)**2 + (y - m_y)**2)**0.5
                            if distancia < radius:
                                verificar_letra(ltr, palabra, letras_adivinadas, letras_falladas, boton)
                                if ltr in palabra:
                                    puntuacion += 10
                                else:
                                    puntuacion -= 5

            intentos = len(letras_falladas)
            dibujar(palabra, letras_adivinadas, letras, intentos, letras_falladas,
                    tiempo_restante, palabra_actual, total_palabras, puntuacion)

            # --- Comprobaciones ---
            if all(l in letras_adivinadas for l in palabra):
                tiempo_tardado = time.time() - tiempo_inicio_palabra
                letras_adivinadas_global |= letras_adivinadas
                puntuacion += 50  # palabra completada
                mostrar_mensaje("✅ ¡Correcto!", VERDE, delay_ms=700)

                # Racha y tiempo extra
                if tiempo_tardado <= 20:  # ⏱️ si fue rápido (<20s)
                    racha_rapida += 1
                    tiempo_total += 5  # bonus por racha
                else:
                    racha_rapida = 0

                tiempo_total += 10  # +10s por palabra completada
                palabra_actual += 1
                jugando = False

            if intentos >= 6:
                mostrar_mensaje(f"❌ Fallaste: {palabra}", ROJO, delay_ms=900)
                racha_rapida = 0
                puntuacion -= 10
                return

            clock.tick(FPS)

    # Bonus por tiempo restante
    tiempo_final = tiempo_total - (time.time() - inicio_tiempo_total)
    if tiempo_final > 0:
        puntuacion += int(tiempo_final)

    mostrar_mensaje(f"🏆 ¡Completaste las {total_palabras} palabras!\nPuntuación final: {puntuacion}", VERDE)
    return

# --- INICIO ---
menu_principal()
pygame.quit()
