import pygame
import random
import sys
import time

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
    return pygame.font.SysFont("comicsans", max(14, int(tamaño * (ANCHO / ANCHO_BASE))))

FUENTE = fuente_responsive(40)
FUENTE_PALABRA = fuente_responsive(70)

# --- PALABRAS ---
PALABRAS = ["PYTHON", "JUEGO", "PROGRAMAR", "AHORCADO", "TECLADO",
            "PANTALLA", "RATON", "CODIGO", "VARIABLE", "ALGORITMO",
            "CLASE", "FUNCION", "CICLO", "OBJETO", "COMPILAR"]

# --- CARGAR IMÁGENES ---
IMAGENES = []
for i in range(7):
    imagen = pygame.image.load(f"assets/hangman{i}.png").convert_alpha()
    IMAGENES.append(imagen)

# --- VARIABLES GLOBALES ---
modo_pantalla_completa = False
clock = pygame.time.Clock()
FPS = 60

# --- FUNCIONES AUXILIARES ---
def escalar_imagen(imagen, escala):
    ancho = max(1, int(imagen.get_width() * escala))
    alto = max(1, int(imagen.get_height() * escala))
    return pygame.transform.smoothscale(imagen, (ancho, alto))

def dibujar_boton(texto, x, y, ancho, alto, color, color_texto, hover_color=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    dentro = x < mouse[0] < x + ancho and y < mouse[1] < y + alto

    if dentro:
        pygame.draw.rect(VENTANA, hover_color or color, (x, y, ancho, alto))
        if click[0] == 1:
            pygame.time.delay(150)
            return True
    else:
        pygame.draw.rect(VENTANA, color, (x, y, ancho, alto))

    texto_render = FUENTE.render(texto, True, color_texto)
    VENTANA.blit(texto_render, (x + ancho/2 - texto_render.get_width()/2, y + alto/2 - texto_render.get_height()/2))
    return False

def redimensionar(nuevo_ancho, nuevo_alto):
    global ANCHO, ALTO, FUENTE, FUENTE_PALABRA
    ANCHO, ALTO = nuevo_ancho, nuevo_alto
    FUENTE = fuente_responsive(40)
    FUENTE_PALABRA = fuente_responsive( max(28, 70 * (ANCHO/ANCHO_BASE)) )

# crea las posiciones de las letras de forma responsive (2 filas de 13)
def crear_botones_letras():
    # radius y gap dependen del ancho
    radius = int(max(18, min(32, ANCHO / 45)))  # entre 18 y 32 px aprox
    gap = int(radius * 0.6)
    total_width = (2 * radius) * 13 + gap * 12
    inicioX = max(20, round((ANCHO - total_width) / 2))
    inicioY = ALTO - (radius * 4) - 20
    botones = []
    for i in range(26):
        x = inicioX + ((i % 13) * (2 * radius + gap)) + radius
        y = inicioY + ((i // 13) * (2 * radius + gap))
        botones.append([x, y, chr(65 + i), "activo", radius])
    return botones

# versión robusta de verificar_letra que acepta set o list
def verificar_letra(letra, palabra, letras_adivinadas, letras_falladas, boton):
    if letra in palabra:
        if isinstance(letras_adivinadas, set):
            letras_adivinadas.add(letra)
        else:
            if letra not in letras_adivinadas:
                letras_adivinadas.append(letra)
        boton[3] = "usada"
    else:
        if isinstance(letras_falladas, set):
            letras_falladas.add(letra)
        else:
            if letra not in letras_falladas:
                letras_falladas.append(letra)
        boton[3] = "fallo"

def mostrar_mensaje(texto, color, delay_ms=1500):
    pygame.time.delay(300)
    VENTANA.fill(BLANCO)
    mensaje = FUENTE_PALABRA.render(texto, True, color)
    VENTANA.blit(mensaje, (ANCHO/2 - mensaje.get_width()/2, ALTO/2 - mensaje.get_height()/2))
    pygame.display.update()
    pygame.time.delay(delay_ms)

# --- MENÚ PRINCIPAL ---
def menu_principal():
    corriendo = True
    while corriendo:
        VENTANA.fill(BLANCO)
        titulo_fuente = fuente_responsive(100)
        titulo = titulo_fuente.render("JUEGO DEL AHORCADO", True, NEGRO)
        VENTANA.blit(titulo, (ANCHO/2 - titulo.get_width()/2, ALTO/4))

        if dibujar_boton("JUGAR", ANCHO/2 - 200, ALTO/2 - 100, 400, 80, GRIS, NEGRO, (180,180,180)):
            modo_desafio()

        if dibujar_boton("CONFIGURACIÓN", ANCHO/2 - 200, ALTO/2 + 20, 400, 80, GRIS, NEGRO, (180,180,180)):
            configuracion()

        if dibujar_boton("SALIR", ANCHO/2 - 200, ALTO/2 + 140, 400, 80, GRIS, NEGRO, (180,180,180)):
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
    global modo_pantalla_completa, VENTANA
    corriendo = True
    while corriendo:
        VENTANA.fill(BLANCO)
        titulo_fuente = fuente_responsive(80)
        titulo = titulo_fuente.render("CONFIGURACIÓN", True, NEGRO)
        VENTANA.blit(titulo, (ANCHO/2 - titulo.get_width()/2, ALTO/4))

        if dibujar_boton("Pantalla completa" if not modo_pantalla_completa else "Modo ventana",
                         ANCHO/2 - 250, ALTO/2 - 50, 500, 80, GRIS, NEGRO, (180,180,180)):
            modo_pantalla_completa = not modo_pantalla_completa
            if modo_pantalla_completa:
                VENTANA = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            else:
                VENTANA = pygame.display.set_mode((1024, 640), pygame.RESIZABLE)
            redimensionar(VENTANA.get_width(), VENTANA.get_height())

        if dibujar_boton("← VOLVER", 50, ALTO - 100, 250, 70, GRIS, NEGRO, (180,180,180)):
            corriendo = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                redimensionar(event.w, event.h)

        pygame.display.update()
        clock.tick(FPS)

# --- DIBUJAR JUEGO (mejorado responsive) ---
def dibujar(palabra, letras_adivinadas, letras, intentos, letras_falladas, tiempo_restante, palabra_actual, total_palabras):
    VENTANA.fill(BLANCO)

    # escala apropiada para la imagen (dependiendo de ancho y alto)
    escala = min(ANCHO / 1920, ALTO / 1080) * 1.0
    imagen = escalar_imagen(IMAGENES[intentos], escala)

    # posición de la imagen: arriba-izquierda con margen
    margen_x = int(ANCHO * 0.08)
    margen_y = int(ALTO * 0.08)
    imagen_x = margen_x
    imagen_y = margen_y
    VENTANA.blit(imagen, (imagen_x, imagen_y))

    # calcular donde colocar la palabra: debajo de la imagen (si cabe), si no, un poco más abajo
    imagen_bottom = imagen_y + imagen.get_height()
    palabra_y = imagen_bottom + int(ALTO * 0.03)  # separación entre imagen y palabra
    # dibujar la palabra centrada horizontalmente, pero asegurando que esté por debajo de la imagen
    mostrar_palabra = ""
    for letra in palabra:
        mostrar_palabra += letra + " " if letra in letras_adivinadas else "_ "
    texto_palabra = FUENTE_PALABRA.render(mostrar_palabra, True, NEGRO)

    # si la palabra se superpone verticalmente con la imagen (caso de imagen muy alta), empujarla abajo
    min_palabra_y = imagen_y + imagen.get_height() + 10
    final_palabra_y = max(palabra_y, min_palabra_y)
    # si aún ahora la palabra queda demasiado abajo (por muy poca altura), reducir fuente (opcional)
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
    VENTANA.blit(progreso, (20, 20))
    minutos = int(tiempo_restante // 60)
    segundos = int(tiempo_restante % 60)
    color_tiempo = ROJO if tiempo_restante < 30 else NEGRO
    cronometro = FUENTE.render(f"Tiempo: {minutos:02}:{segundos:02}", True, color_tiempo)
    VENTANA.blit(cronometro, (ANCHO - cronometro.get_width() - 30, 20))

    pygame.display.update()

# --- MODO DESAFÍO (10 palabras, 3 minutos total) ---
def modo_desafio():
    palabras_juego = random.sample(PALABRAS, min(10, len(PALABRAS)))
    letras_adivinadas_global = set()
    tiempo_total = 300  # 🕐 5 minutos base
    inicio_tiempo_total = time.time()
    palabra_actual = 1
    total_palabras = len(palabras_juego)

    # ⚡ Sistema de rachas y puntuación
    racha_rapida = 0
    tiempo_inicio_palabra = 0
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

        # Además, mantener la letra encadenada de palabras anteriores
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
                                # puntuación por letra
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
                    tiempo_restante, palabra_actual, total_palabras)

            # Mostrar puntuación en pantalla
            puntos_txt = FUENTE.render(f"Puntos: {puntuacion}", True, NEGRO)
            VENTANA.blit(puntos_txt, (ANCHO//2 - puntos_txt.get_width()//2, 20))
            pygame.display.update()

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

    mostrar_mensaje(f"🏆 ¡Completaste las 10 palabras!\nPuntuación final: {puntuacion}", VERDE)
    return



# --- INICIO ---
menu_principal()
pygame.quit()
