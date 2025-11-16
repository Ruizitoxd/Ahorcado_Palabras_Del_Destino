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

# Paleta para botones translúcidos (texto blanco)
BTN_BG_ALPHA = 160

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

# --- Clases ---
class Nube:
    def __init__(self, x, y, velocidad):
        self.x = x
        self.y = y
        self.velocidad = velocidad
        self.imagen = pygame.image.load("assets/nube.png")
        self.imagen = pygame.transform.scale(self.imagen, (int(ANCHO*0.15), int(ALTO*0.15)))

    def mover(self):
        self.x += self.velocidad
        if self.x > ANCHO:
            self.x = -self.imagen.get_width()
            self.y = random.randint(30, int(ALTO*0.3))

    def dibujar(self, ventana):
        ventana.blit(self.imagen, (self.x, self.y))

# Creación de las nubes
nubes = [
    Nube(100, 100, 0.3),
    Nube(400, 150, 0.2),
    Nube(700, 80, 0.4)
]

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

# ----- Botón translúcido y fiable -----
def dibujar_boton(texto, x, y, ancho, alto, color_bg, color_texto, hover_color=None):
    """
    Dibuja un botón translúcido con texto centrado.
    Devuelve True si fue clickeado (usa estado actual del mouse).
    """
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    dentro = x < mouse[0] < x + ancho and y < mouse[1] < y + alto

    # Crear superficie translúcida
    surf = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    # color_bg puede venir como tuple RGB o tuple RGBA
    bg = color_bg if len(color_bg) == 4 else (*color_bg, BTN_BG_ALPHA)
    hover_bg = hover_color if hover_color is not None else (bg[0], bg[1], bg[2])
    hover_bg = hover_bg if (len(hover_bg) == 4) else (*hover_bg, BTN_BG_ALPHA+40)

    if dentro:
        surf.fill(hover_bg)
    else:
        surf.fill(bg)

    # Borde suave
    radius = 10
    # Pegar surf en ventana con borde redondeado (pygame no trae fácil border_radius para surf con alpha)
    # Dibujamos rect en la ventana directamente con alpha mediante surf.convert_alpha()
    VENTANA.blit(surf, (x, y))

    # Texto centrado
    texto_render = FUENTE.render(texto, True, color_texto)
    VENTANA.blit(texto_render, (x + ancho/2 - texto_render.get_width()/2, y + alto/2 - texto_render.get_height()/2))

    # Detectar click (evitamos múltiples detecciones usando pequeño delay dentro del mismo frame)
    if dentro and click[0] == 1:
        # espera a release para evitar múltiples activaciones instantáneas
        # bloqueamos aquí brevemente (no demasiado): esto simplifica la interacción
        while pygame.mouse.get_pressed()[0]:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.time.delay(10)
        pygame.time.delay(80)
        return True
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

# --- FONDO ANIMADO (DESTELLOS) ---
def crear_particulas_destellos(n):
    particulas = []
    for _ in range(n):
        x = random.uniform(0, ANCHO)
        y = random.uniform(0, ALTO)
        vx = random.uniform(-0.15, 0.15)   # ligero movimiento horizontal
        vy = random.uniform(-0.25, -0.6)   # suben lentamente
        size = random.uniform(0.7, 3.2)
        brillo = random.uniform(100, 255)
        particulas.append([x, y, vx, vy, size, brillo])
    return particulas

def actualizar_y_dibujar_particulas(particulas):
    for p in particulas:
        p[0] += p[2]
        p[1] += p[3]
        p[5] += random.uniform(-1.0, 1.0)  # fluctuación brillo
        p[5] = max(80, min(255, p[5]))
        # reaparecer abajo si se van arriba
        if p[1] < -10 or p[0] < -20 or p[0] > ANCHO + 20:
            p[0] = random.uniform(0, ANCHO)
            p[1] = ALTO + random.uniform(5, 60)
            p[2] = random.uniform(-0.15, 0.15)
            p[3] = random.uniform(-0.25, -0.6)
            p[4] = random.uniform(0.7, 3.2)
            p[5] = random.uniform(120, 255)
        # dibujar círculo con alpha según brillo
        alpha = int(p[5])
        surf = pygame.Surface((int(p[4]*3)+2, int(p[4]*3)+2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 255, 255, alpha), (surf.get_width()//2, surf.get_height()//2), max(1, int(p[4])))
        VENTANA.blit(surf, (int(p[0]-surf.get_width()//2), int(p[1]-surf.get_height()//2)))

# --- MENÚ PRINCIPAL (ESTILO HOLLOW) ---
def menu_principal():
    # Fondo base
    ruta_fondo = os.path.join(ruta_assets, "fondo_hollow.png")
    fondo = None
    if os.path.exists(ruta_fondo):
        fondo = pygame.image.load(ruta_fondo).convert()

    # Intento de fuente temática (si tienes assets/fonts/TrajanPro-Regular.ttf lo usará)
    try:
        fuente_titulo = pygame.font.Font(os.path.join(ruta_assets, "fonts", "TrajanPro-Regular.ttf"), int(ALTO * 0.12))
    except:
        fuente_titulo = pygame.font.SysFont("georgia", int(ALTO * 0.12))

    # partículas (destellos)
    particulas = crear_particulas_destellos(48)

    fade_alpha = 0
    fade_in = True

    while True:
        # DIBUJO FONDO
        if fondo:
            fondo_escalado = pygame.transform.smoothscale(fondo, (ANCHO, ALTO))
            VENTANA.blit(fondo_escalado, (0, 0))
            # aplicar un leve oscurecimiento para que texto resalte
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            overlay.fill((10, 12, 20, 120))
            VENTANA.blit(overlay, (0,0))
        else:
            VENTANA.fill((12, 14, 18))

        # partículas destellos
        actualizar_y_dibujar_particulas(particulas)

        # TÍTULO grande
        titulo = fuente_titulo.render("HOLLOW HANGMAN", True, (245, 245, 250))
        # fade-in
        if fade_in:
            fade_alpha += 4
            if fade_alpha >= 255:
                fade_alpha = 255
                fade_in = False
        titulo.set_alpha(fade_alpha)
        VENTANA.blit(titulo, (ANCHO/2 - titulo.get_width()/2, ALTO * 0.14))

        # Botones centrados
        btn_w = int(ANCHO * 0.33)
        btn_h = int(ALTO * 0.085)
        x_center = int(ANCHO/2 - btn_w/2)
        y_start = int(ALTO * 0.45)
        hover = (220, 220, 255)

        # START -> abrir selector de dificultad
        if dibujar_boton("START GAME", x_center, y_start, btn_w, btn_h, (30,30,40), (255,255,255), hover):
            dificultad = seleccionar_dificultad()
            if dificultad:
                modo_desafio(dificultad)
            # al volver, continuar mostrando el menu

        # OPTIONS
        if dibujar_boton("OPTIONS", x_center, y_start + btn_h + 18, btn_w, btn_h, (30,30,40), (255,255,255), hover):
            configuracion()

        # QUIT
        if dibujar_boton("QUIT GAME", x_center, y_start + 2*(btn_h + 18), btn_w, btn_h, (30,30,40), (255,255,255), hover):
            pygame.quit()
            sys.exit()

        # eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                redimensionar(event.w, event.h)

        pygame.display.update()
        clock.tick(FPS)

# --- CONFIGURACIÓN (aplica mismo estilo) ---
def configuracion():
    global modo_pantalla_completa, VENTANA, ANCHO, ALTO
    ruta_fondo = os.path.join(ruta_assets, "fondo_hollow.png")
    fondo = None
    if os.path.exists(ruta_fondo):
        fondo = pygame.image.load(ruta_fondo).convert()

    try:
        fuente_titulo = pygame.font.Font(os.path.join(ruta_assets, "fonts", "TrajanPro-Regular.ttf"), int(ALTO * 0.09))
    except:
        fuente_titulo = pygame.font.SysFont("georgia", int(ALTO * 0.09))

    particulas = crear_particulas_destellos(36)

    while True:
        if fondo:
            VENTANA.blit(pygame.transform.smoothscale(fondo, (ANCHO, ALTO)), (0,0))
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            overlay.fill((6, 6, 8, 140))
            VENTANA.blit(overlay, (0,0))
        else:
            VENTANA.fill((12, 14, 18))

        actualizar_y_dibujar_particulas(particulas)

        titulo = fuente_titulo.render("CONFIGURACIÓN", True, (245,245,250))
        VENTANA.blit(titulo, (ANCHO/2 - titulo.get_width()/2, ALTO * 0.12))

        btn_w = int(ANCHO * 0.44)
        btn_h = int(ALTO * 0.10)
        x_center = ANCHO/2 - btn_w/2
        y = int(ALTO*0.4)
        hover = (220,220,255)

        if dibujar_boton("Pantalla completa" if not modo_pantalla_completa else "Modo ventana", int(x_center), y, btn_w, btn_h, (30,30,40), (255,255,255), hover):
            modo_pantalla_completa = not modo_pantalla_completa
            try:
                if modo_pantalla_completa:
                    VENTANA = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    ANCHO, ALTO = VENTANA.get_size()
                    redimensionar(ANCHO, ALTO, recrear_ventana=False)
                else:
                    VENTANA = pygame.display.set_mode((1024, 640), pygame.RESIZABLE)
                    ANCHO, ALTO = VENTANA.get_size()
                    redimensionar(ANCHO, ALTO, recrear_ventana=False)
            except Exception as e:
                print("[configuracion] error al cambiar modo:", e)

        if dibujar_boton("← VOLVER",  int(ANCHO*0.03), ALTO - int(ALTO*0.12), int(ANCHO*0.18), int(ALTO*0.08), (30,30,40), (255,255,255), hover):
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                redimensionar(event.w, event.h, recrear_ventana=True)

        pygame.display.update()
        clock.tick(FPS)

# Seleccionar dificultad (tema hollow)
def seleccionar_dificultad():
    ruta_fondo = os.path.join(ruta_assets, "fondo_hollow.png")
    fondo = None
    if os.path.exists(ruta_fondo):
        fondo = pygame.image.load(ruta_fondo).convert()

    try:
        fuente_titulo = pygame.font.Font(os.path.join(ruta_assets, "fonts", "TrajanPro-Regular.ttf"), int(ALTO * 0.085))
    except:
        fuente_titulo = pygame.font.SysFont("georgia", int(ALTO * 0.085))

    particulas = crear_particulas_destellos(36)

    while True:
        if fondo:
            VENTANA.blit(pygame.transform.smoothscale(fondo, (ANCHO, ALTO)), (0,0))
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            overlay.fill((8, 8, 12, 140))
            VENTANA.blit(overlay, (0,0))
        else:
            VENTANA.fill((12, 14, 18))

        actualizar_y_dibujar_particulas(particulas)

        titulo = fuente_titulo.render("Selecciona la Dificultad", True, (245,245,250))
        VENTANA.blit(titulo, (ANCHO / 2 - titulo.get_width() / 2, ALTO * 0.12))

        # Botones centrados horizontalmente
        btn_w = int(ANCHO * 0.28)
        btn_h = int(ALTO * 0.11)
        espacio = int(ANCHO * 0.05)
        total_ancho = btn_w * 2 + espacio
        x_inicial = (ANCHO - total_ancho) // 2
        y_centro = (ALTO - btn_h) // 2 + int(ALTO * 0.08)

        # FACIL y DIFICIL
        if dibujar_boton("FÁCIL", x_inicial, y_centro, btn_w, btn_h, (40,60,40), (255,255,255), (0,150,0)):
            return "facil"
        if dibujar_boton("DIFÍCIL", x_inicial + btn_w + espacio, y_centro, btn_w, btn_h, (60,30,30), (255,255,255), (180,0,0)):
            return "dificil"

        # Volver
        if dibujar_boton("← VOLVER", int(ANCHO * 0.03), ALTO - int(ALTO * 0.12), int(ANCHO * 0.18), int(ALTO * 0.08), (30,30,40), (255,255,255), (220,220,255)):
            return None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                redimensionar(event.w, event.h)

        pygame.display.update()
        clock.tick(FPS)

# --- CARGAR FONDOS DE DIFICULTAD ---
fondo_facil_path = os.path.join(ruta_assets, "fondo_facil.jpg")
fondo_dificil_path = os.path.join(ruta_assets, "fondo_dificil.jpg")

try:
    fondo_facil = pygame.image.load(fondo_facil_path).convert()
    print(f"[OK] Fondo fácil cargado desde {fondo_facil_path}")
except Exception as e:
    print(f"[ERROR] No se pudo cargar fondo_facil.png: {e}")
    fondo_facil = pygame.Surface((ANCHO, ALTO))
    fondo_facil.fill((120, 200, 255))  # color azul claro de respaldo
    print("[INFO] Usando color de respaldo para fondo fácil.")

try:
    if fondo_dificil_path.lower().endswith(".avif"):
        # pygame no soporta .avif, intentamos una versión .png alternativa
        alt_path = fondo_dificil_path.replace(".avif", ".png")
        if os.path.exists(alt_path):
            fondo_dificil = pygame.image.load(alt_path).convert()
            print(f"[OK] Fondo difícil cargado desde {alt_path}")
        else:
            raise Exception("Formato .avif no soportado, y no existe versión .png")
    else:
        fondo_dificil = pygame.image.load(fondo_dificil_path).convert()
        print(f"[OK] Fondo difícil cargado desde {fondo_dificil_path}")
except Exception as e:
    print(f"[ADVERTENCIA] No se pudo cargar fondo_dificil: {e}")
    fondo_dificil = pygame.Surface((ANCHO, ALTO))
    fondo_dificil.fill((30, 30, 60))  # color oscuro de respaldo
    print("[INFO] Usando color de respaldo para fondo difícil.")

    # --- SISTEMA DE PARTÍCULAS (CENIZA) ---
# --- SISTEMA DE PARTÍCULAS (CENIZA) ---
import random

class ParticulaCeniza:
    def __init__(self):
        self.x = random.randint(0, ANCHO)
        self.y = random.randint(-ALTO, 0)
        self.vel_y = random.uniform(0.3, 1.0)
        self.tamano = random.randint(2, 4)
        self.alpha = random.randint(100, 180)

    def actualizar(self):
        self.y += self.vel_y
        if self.y > ALTO:
            self.y = random.randint(-50, 0)
            self.x = random.randint(0, ANCHO)
        # movimiento sutil lateral
        self.x += random.uniform(-0.3, 0.3)

    def dibujar(self, pantalla):
        color = (180, 180, 180, self.alpha)
        superficie = pygame.Surface((self.tamano, self.tamano), pygame.SRCALPHA)
        pygame.draw.circle(superficie, color, (self.tamano//2, self.tamano//2), self.tamano//2)
        pantalla.blit(superficie, (self.x, self.y))

# Crear partículas de ceniza (se usan solo en modo difícil)
particulas_ceniza = [ParticulaCeniza() for _ in range(70)]

# --- SISTEMA DE ERUPCIONES VOLCÁNICAS ---
class Erupcion:
    def __init__(self):
        self.reiniciar()

    def reiniciar(self):
        self.x = random.randint(0, ANCHO)
        self.y = ALTO/2 + random.randint(100, 300)   # Nacen más abajo del suelo
        self.radio = random.randint(8, 14)        # Tamaño del fuego
        self.vel_y = random.uniform(1.5, 2.5)     # Subida moderada
        self.color = random.choice([
            (255, 80, 0, 220),   # naranja fuerte
            (255, 30, 0, 200),   # rojo intenso
            (255, 180, 50, 200)  # amarillo-lava
        ])
        self.alpha = 255
        self.tiempo_vida = random.randint(130, 200)

    def actualizar(self):
        self.y -= self.vel_y
        self.vel_y *= 0.98  # desacelera suavemente
        self.tiempo_vida -= 1

        # 🔥 si llega a la mitad de la pantalla, reinicia
        if self.y <= ALTO / 10:
            self.reiniciar()

        # o si se acaba su tiempo de vida
        elif self.tiempo_vida <= 0:
            self.reiniciar()

        # desvanecimiento suave al final
        if self.tiempo_vida < 50:
            self.alpha = max(0, int(self.alpha * 0.9))

    def dibujar(self, pantalla):
        superficie = pygame.Surface((self.radio * 2, self.radio * 2), pygame.SRCALPHA)
        color = (*self.color[:3], self.alpha)
        pygame.draw.circle(superficie, color, (self.radio, self.radio), self.radio)
        pantalla.blit(superficie, (self.x, self.y))

# Crear lista de erupciones (más cantidad = más movimiento)
erupciones = [Erupcion() for _ in range(25)]

# --- DIBUJAR JUEGO (mejorado responsive) ---
def dibujar(palabra, letras_adivinadas, letras, intentos, letras_falladas, tiempo_restante, palabra_actual, total_palabras, puntuacion, dificultad):
    # --- Fondo según dificultad ---
    if dificultad == "facil":
        # Escalar fondo fácil a tamaño de ventana
        fondo_escalado = pygame.transform.smoothscale(fondo_facil, (ANCHO, ALTO))
        VENTANA.blit(fondo_escalado, (0, 0))
        # Dibujar nubes animadas sobre el fondo
        for nube in nubes:
            nube.mover()
            nube.dibujar(VENTANA)
    else:
        fondo_escalado = pygame.transform.smoothscale(fondo_dificil, (ANCHO, ALTO))
        VENTANA.blit(fondo_escalado, (0, 0))
            # --- Erupciones de lava (solo modo difícil) ---
        for e in erupciones:
            e.actualizar()
            e.dibujar(VENTANA)

        # --- Ceniza flotante encima ---
        for p in particulas_ceniza:
            p.actualizar()
            p.dibujar(VENTANA)

    # --- Imagen del ahorcado ---
    imagen = IMAGENES[intentos]
    margen_x = int(ANCHO * 0.06)
    margen_y = int(ALTO * 0.06)
    imagen_x = margen_x
    imagen_y = margen_y
    VENTANA.blit(imagen, (imagen_x, imagen_y))

    # --- Palabra ---
    imagen_bottom = imagen_y + imagen.get_height()
    palabra_y = imagen_bottom + int(ALTO * 0.03)
    mostrar_palabra = ""
    for letra in palabra:
        mostrar_palabra += letra + " " if letra in letras_adivinadas else "_ "
    color_palabra = BLANCO if dificultad == "dificil" else NEGRO
    texto_palabra = FUENTE_PALABRA.render(mostrar_palabra, True, color_palabra)
    if texto_palabra.get_width() > ANCHO * 0.9:
        font_temp = pygame.font.SysFont("comicsans", max(12, int(FUENTE_PALABRA.get_height() * 0.7)))
        texto_palabra = font_temp.render(mostrar_palabra, True, NEGRO)
    min_palabra_y = imagen_y + imagen.get_height() + 10
    final_palabra_y = max(palabra_y, min_palabra_y)
    VENTANA.blit(texto_palabra, (ANCHO/2 - texto_palabra.get_width()/2, final_palabra_y))

    # --- Letras ---
    for btn in letras:
        x, y, letra, estado, radius = btn
        texto = FUENTE.render(letra, True, BLANCO)

        if dificultad == "facil":
            # --- MODO FÁCIL: Botones suaves y redondos ---
            if estado == "activo":
                pygame.draw.circle(VENTANA, (150, 180, 255), (x, y), radius)
                pygame.draw.circle(VENTANA, (80, 110, 255), (x, y), radius, 3)
            elif estado == "usada":
                pygame.draw.circle(VENTANA, (200, 200, 200), (x, y), radius)
            elif estado == "fallo":
                pygame.draw.circle(VENTANA, (255, 150, 150), (x, y), radius)
            VENTANA.blit(texto, (x - texto.get_width()/2, y - texto.get_height()/2))

        else:
            # --- MODO DIFÍCIL: Botones agresivos, rectos ---
            rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
            if estado == "activo":
                pygame.draw.rect(VENTANA, (80, 80, 80), rect, border_radius=2)
                pygame.draw.rect(VENTANA, (255, 60, 60), rect, 2, border_radius=2)
            elif estado == "usada":
                pygame.draw.rect(VENTANA, (60, 60, 60), rect, border_radius=2)
            elif estado == "fallo":
                pygame.draw.rect(VENTANA, (120, 20, 20), rect, border_radius=2)
            VENTANA.blit(texto, (x - texto.get_width()/2, y - texto.get_height()/2))


    # --- HUD (progreso, tiempo, puntuación) ---
    progreso = FUENTE.render(f"Palabra {palabra_actual}/{total_palabras}", True, BLANCO)
    VENTANA.blit(progreso, (int(ANCHO*0.02), int(ALTO*0.02)))

    minutos = int(tiempo_restante // 60)
    segundos = int(tiempo_restante % 60)
    color_tiempo = ROJO if tiempo_restante < 30 else BLANCO
    cronometro = FUENTE.render(f"Tiempo: {minutos:02}:{segundos:02}", True, color_tiempo)
    VENTANA.blit(cronometro, (ANCHO - cronometro.get_width() - int(ANCHO*0.02), int(ALTO*0.02)))

    puntos_txt = FUENTE.render(f"Puntos: {puntuacion}", True, BLANCO)
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
                    tiempo_restante, palabra_actual, total_palabras, puntuacion, dificultad)

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
if __name__ == "__main__":
    menu_principal()
    pygame.quit()
