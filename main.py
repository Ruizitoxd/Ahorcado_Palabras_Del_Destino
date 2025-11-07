import pygame
import random

# Inicializar pygame
pygame.init()

# Configuración de la pantalla
ANCHO, ALTO = 1920, 1080
VENTANA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Juego del Ahorcado")

# TE AMO MACIASSS (Borré estoxd no sé porque el git no me dejaba subir todo el archivo sin algún cambio raroxdd)

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)

# Fuente
FUENTE = pygame.font.SysFont("comicsans", 40)
FUENTE_PALABRA = pygame.font.SysFont("comicsans", 60)

# Palabras posibles
PALABRAS = ["PYTHON", "JUEGO", "PROGRAMAR", "AHORCADO", "PANTALLA", "TECLADO", "RATON", "CODIGO"]

# Cargar imágenes del ahorcado
IMAGENES = []
for i in range(7):
    imagen = pygame.image.load(f"assets/hangman{i}.png")  # Debes tener imágenes hangman0.png ... hangman6.
    ancho, alto = imagen.get_size()
    imagen = pygame.transform.scale(imagen, (ancho // 3, alto // 3))
    IMAGENES.append(imagen)

# Variables del juego
palabra = random.choice(PALABRAS)
letras_adivinadas = []
intentos = 0
FPS = 60
clock = pygame.time.Clock()

# Posiciones de botones (A-Z)
RADIO = 20
GAP = 15
letras = []
inicioX = round((ANCHO - (RADIO * 2 + GAP) * 13) / 2)
inicioY = 400
for i in range(26):
    x = inicioX + GAP * 2 + ((RADIO * 2 + GAP) * (i % 13))
    y = inicioY + ((i // 13) * (GAP + RADIO * 2))
    letras.append([x, y, chr(65 + i), True])  # [x, y, letra, visible]

# Función para dibujar en pantalla
def dibujar():
    VENTANA.fill(BLANCO)
    
    # Mostrar título
    texto = FUENTE.render("ADIVINA LA PALABRA:", True, NEGRO)
    VENTANA.blit(texto, (ANCHO / 2 - texto.get_width() / 2, 20))
    
    # Mostrar palabra con guiones
    mostrar_palabra = ""
    for letra in palabra:
        if letra in letras_adivinadas:
            mostrar_palabra += letra + " "
        else:
            mostrar_palabra += "_ "
    texto_palabra = FUENTE_PALABRA.render(mostrar_palabra, True, NEGRO)
    VENTANA.blit(texto_palabra, (400 - texto_palabra.get_width() / 2, 200))
    
    # Dibujar letras
    for x, y, letra, visible in letras:
        if visible:
            pygame.draw.circle(VENTANA, NEGRO, (x, y), RADIO, 3)
            texto = FUENTE.render(letra, True, NEGRO)
            VENTANA.blit(texto, (x - texto.get_width()/2, y - texto.get_height()/2))
    
    # Dibujar imagen del ahorcado
    VENTANA.blit(IMAGENES[intentos], (x - IMAGENES[intentos].get_width()/2, 100))
    
    pygame.display.update()

# Función principal del juego
def main():
    global intentos
    correr = True
    ganar = False

    while correr:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                correr = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                m_x, m_y = pygame.mouse.get_pos()
                for letra in letras:
                    x, y, ltr, visible = letra
                    if visible:
                        distancia = ((x - m_x)**2 + (y - m_y)**2) ** 0.5
                        if distancia < RADIO:
                            letra[3] = False
                            letras_adivinadas.append(ltr)
                            if ltr not in palabra:
                                intentos += 1

        dibujar()

        # Verificar victoria
        ganar = True
        for letra in palabra:
            if letra not in letras_adivinadas:
                ganar = False
                break

        if ganar:
            mostrar_mensaje("¡GANASTE!")
            break

        if intentos == 6:
            mostrar_mensaje(f"PERDISTE. La palabra era: {palabra}")
            break

def mostrar_mensaje(texto):
    pygame.time.delay(1000)
    VENTANA.fill(BLANCO)
    mensaje = FUENTE_PALABRA.render(texto, True, ROJO)
    VENTANA.blit(mensaje, (ANCHO/2 - mensaje.get_width()/2, ALTO/2 - mensaje.get_height()/2))
    pygame.display.update()
    pygame.time.delay(3000)

main()
pygame.quit()
