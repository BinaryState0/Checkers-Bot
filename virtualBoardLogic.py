#from mlf_api import RobotClient
import time
import cv2
import argparse
import transformations as tf  
import numpy as np
from checkers import *


def show(frame):
    cv2.imshow("XD", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def show_bounding_boxes(frame, contours):
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    show(frame)


def transform(cx, cy):
    # Transformar las coordenadas de la imagen a coordenadas del robot
    # obsoleto?
    xaxis, yaxis, zaxis = [1, 0, 0], [0, 1, 0], [0, 0, 1]

    T1 = tf.translation_matrix([320, 480, 0])
    R1 = tf.rotation_matrix(180 , xaxis)
    R2 = tf.rotation_matrix(90 , zaxis)

    trans = tf.concatenate_matrices(R2, R1, T1)
    matriz = tf.concatenate_matrices(trans, [cx, cy, 0, 1])
    # debug
    # print(matriz)

    mm_per_pixel = 0.81967
    x = int(matriz[0] * mm_per_pixel)
    y = int(matriz[1] * mm_per_pixel)

    return x, y


def transforma(cx, cy):
    # Lo mismo que transform() pero ahora mas compacto
    # (480, 320) son las coordenadas de la base del robot en la imagen, 0.82 es la medida de un pixel en mm
    return 0.82*(480-cy), 0.82*(320-cx)


def extract_centroid(contours):
    # Utiliza el area para computar el centro de masa
    contour = max(contours, key=cv2.contourArea)

    M = cv2.moments(contour)

    if M["m00"] != 0:
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
    else:
        
        cx, cy = 0, 0

    return cx, cy

def order_points(puntos):
    """
    Ordena 4 puntos en el orden:
    top-left, top-right, bottom-right, bottom-left.
    Acepta cualquier formato anidado de cv2.approxPolyDP.
    """
    pts = np.array(puntos, dtype="float32")

    # Si viene con forma (4, 1, 2), la convertimos a (4, 2)
    if pts.ndim == 3:
        pts = pts.reshape(-1, 2)

    if len(pts) != 4:
        raise ValueError(f"Se esperaban 4 puntos, pero se recibieron {len(pts)}")

    # Ordenar según suma y diferencia
    s = pts.sum(axis=1)
    tl = pts[np.argmin(s)]
    br = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    tr = pts[np.argmin(diff)]
    bl = pts[np.argmax(diff)]

    return np.array([tl, tr, br, bl], dtype="float32")

#Transformación al sistema de referencias alineado a los ejes de vuelta al convencional

def warp_to_original(point, M_inv):
    x, y = point
    vec = np.array([x, y, 1], dtype=float)
    x_o, y_o, w = M_inv.dot(vec)
    return (int(round(x_o / w)), int(round(y_o / w)))

def cell_index(punto, width, height, n=6):
    px, py = punto
    xs = np.linspace(0, width, n + 1)
    ys = np.linspace(0, height, n + 1)

    i = np.searchsorted(xs, px) - 1
    j = np.searchsorted(ys, py) - 1

    if 0 <= i < n and 0 <= j < n:
        return i, j
    else:
        return None

def locate_centroid(contours, dibujar=False, imagen=None):
    centroides = []
    img_result = imagen.copy() if dibujar and imagen is not None else None

    for cnt in contours:
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            centroides.append((cx, cy))
            if dibujar and img_result is not None:
                cv2.circle(img_result, (cx, cy), 5, (0, 0, 255), -1)

    return (centroides, img_result) if dibujar else (centroides, None)

def lay_board(current_board, centroids, player):
    working_board = current_board
    value = 0
    if player == 1:
        value = 1
    if player == 2:
        value = -1
    for cnt in centroids:
        print(cnt)
        x, y = cell_index(cnt, 600, 600)
        print(x, y)
        working_board.board[y][x] = value
    return working_board

# Capture es una función que como su nombre índica, captura con la cámara del robot el tablero y lo traslada a un array compatible con checkers.py 

def capture(board):
    #robot = RobotClient("10.200.145.103")

    #frame = robot.capture()
    frame = cv2.imread('boardperspective.png')
    
    show(frame)

    # Guardar imagen para encontrar buen umbral hsv
    # Vean: utils/getHsv.py
    # cv2.imwrite("frame.jpg", frame)

    # Seleccionar los umbrales (tablero)
    board_colorsMin = [137, 54, 0]
    board_colorsMax = [151, 255, 255]
    board_lower = np.array([board_colorsMin])
    board_upper = np.array([board_colorsMax])

    # Siguiendo el orden dado por playCheckers, Player 1 (ø) es IA [Orientación Norte], Player 2 (o) [Sur] es el jugador humano que da la primera jugada.
    Player1_colorsMin = [72, 80, 0]
    Player1_colorsMax = [125, 255, 255]
    Player1_lower = np.array([Player1_colorsMin])
    Player1_upper = np.array([Player1_colorsMax])

    Player2_colorsMin = [0, 0, 0]
    Player2_colorsMax = [3, 255, 255]
    Player2_lower = np.array([Player2_colorsMin])
    Player2_upper = np.array([Player2_colorsMax])

    # Crear la imagen HSV y aplicar el umbral
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, board_lower, board_upper)
    #kernel = np.ones((5,5), np.uint8) # matriz de 1s de 5x5
    #mask2 = cv2.erode(mask, kernel)
    show(mask)

    # Encontrar los contornos
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
    # Aproximar contornos a un polígono
        epsilon = 0.02 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

    # Vemos si es un rectangulo
    if len(approx) == 4:
        print("Found board with following corners:")
        for point in approx:
            x, y = point[0]  
            print(x, y)
        print(approx)

    ordered = order_points(approx)

    # Definir las coordenadas de destino (cuadrado “ideal”)
    width, height = 600, 600  # puedes ajustar este tamaño
    dst_pts = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]
    ], dtype="float32")

    # Calcular la transformación de perspectiva
    M = cv2.getPerspectiveTransform(ordered, dst_pts)

    # Aplicar la transformación a la imagen
    warped = cv2.warpPerspective(frame, M, (width, height))

    cv2.imshow("Alineado", warped)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Setearemos el tablero. Dado que esta función debe de tener como salida un tablero para cada jugada.

    # Ahora veremos los jugadores.

    hsv = cv2.cvtColor(warped, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, Player1_lower, Player1_upper)

    # Suavizado. Player 1

    kernel = np.ones((5,5), np.uint8) # matriz de 1s de 5x5
    mask2 = cv2.erode(mask, kernel)
    show(mask2)

    contours, _ = cv2.findContours(mask2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    print(f"N° de Contornos (Jugador 1): {len(contours)}")

    show_bounding_boxes(warped.copy(), contours)

    centroids, image_centroids = locate_centroid(contours, dibujar=True, imagen=mask2)

    print(centroids)
    show(image_centroids)

    #Ahora veremos donde deben de estar los centroides. Tercera variable define si es jugador 1 o 2
    board = lay_board(board, centroids, 1)
    print(board)

    #Repetimos con Jugador 2 -----------------------------------------------------------------------------

    mask = cv2.inRange(hsv, Player2_lower, Player2_upper)
    show(mask)

    # Suavizado. Player 2

    kernel = np.ones((5,5), np.uint8) # matriz de 1s de 5x5
    mask2 = cv2.erode(mask, kernel)
    show(mask2)

    contours, _ = cv2.findContours(mask2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    print(f"N° de Contornos (Jugador 2): {len(contours)}")

    show_bounding_boxes(warped.copy(), contours)

    centroids, image_centroids = locate_centroid(contours, dibujar=True, imagen=mask2)

    print(centroids)
    show(image_centroids)

    #Ahora veremos donde deben de estar los centroides. Tercera variable define si es jugador 1 o 2
    board = lay_board(board, centroids, 2)
    print(board)

    #cx, cy = extract_centroid(contours)

    # Dibujar el centroide
    #cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
    #show(frame)

    # Transformar de coordenadas de la imagen a coordenadas del robot
    #x, y = transforma(cx, cy)

    # Mover el robot con cinemática inversa
    #robot.move_xyz(x, y, z=0.0)

gameBoard = Board(0)
gameBoard.SetBoard
capture(gameBoard)
