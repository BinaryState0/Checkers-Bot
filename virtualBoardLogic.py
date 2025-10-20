#from mlf_api import RobotClient
import time
import cv2
import argparse
import transformations as tf  
import numpy as np


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

def create_virtual_board(width, height, n=6):
    """
    Divide el cuadrado en n×n celdas.
    Retorna una lista de celdas, cada una con ((x0, y0), (x1, y1)).
    """
    dx = width / n
    dy = height / n
    # Líneas divisorias (7 si n=6)
    xs = [i * dx for i in range(n + 1)]
    ys = [j * dy for j in range(n + 1)]
    # Celdas entre líneas
    celdas = []
    for i in range(n):
        for j in range(n):
            x0, y0 = xs[i], ys[j]
            x1, y1 = xs[i + 1], ys[j + 1]
            celdas.append(((x0, y0), (x1, y1)))
    return celdas, xs, ys

def cell_index(punto, xs, ys):
    x, y = punto
    i = np.searchsorted(xs, x) - 1
    j = np.searchsorted(ys, y) - 1
    if 0 <= i < len(xs) - 1 and 0 <= j < len(ys) - 1:
        return i, j

def main():
    #robot = RobotClient("10.200.145.103")

    #frame = robot.capture()
    frame = cv2.imread('boardexample.png')
    
    show(frame)

    # Guardar imagen para encontrar buen umbral hsv
    # Vean: utils/getHsv.py
    # cv2.imwrite("frame.jpg", frame)

    # Seleccionar los umbrales
    board_colorsMin = [122, 54, 0]
    board_colorsMax = [179, 255, 255]
    lower = np.array([board_colorsMin])
    upper = np.array([board_colorsMax])

    # Crear la imagen HSV y aplicar el umbral
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    show(mask)
    print(mask.shape)
    #kernel = np.ones((5,5), np.uint8) # matriz de 1s de 5x5
    #mask2 = cv2.erode(mask, kernel)
    #show(mask2)

    # Encontrar los contornos
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    print(f"N° de Contornos: {len(contours)}")

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

    # 2️Definir las coordenadas de destino (cuadrado “ideal”)
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

    width, height = 600, 600
    celdas, xs, ys = create_virtual_board(width, height)

    # punto del objeto (por ejemplo, centro de contorno) [Este objeto está en el nuevo sistema de referencia]
    # se hará luego el barrido que detecte cada ficha en este nuevo sistema, obteniendo direcciones que serán transformadas de vuelta al sistema original para el movimiento de la maquina
    p_objeto = (600, 600)
    img_vis = warped.copy()
    i, j = cell_index(p_objeto, xs, ys)
    print(f"El objeto está en la celda ({i}, {j})")
    # Dibujar cuadrícula
    for i in range(1, 6):
        for x in xs:
            cv2.line(img_vis, (int(x), 0), (int(x), height), (100, 100, 100), 1)
        for y in ys:
            cv2.line(img_vis, (0, int(y)), (width, int(y)), (100, 100, 100), 1)

    # Marcar el punto del objeto
    cv2.circle(img_vis, (int(p_objeto[0]), int(p_objeto[1])), 5, (0, 0, 255), -1)

    cv2.imshow("Cuadricula 6x6", img_vis)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Extraemos el centroide
    cx, cy = extract_centroid(contours)

    # Dibujar el centroide
    #cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
    #show(frame)

    # Transformar de coordenadas de la imagen a coordenadas del robot
    x, y = transforma(cx, cy)

    # Mover el robot con cinemática inversa
    #robot.move_xyz(x, y, z=0.0)


if __name__ == "__main__":
    main()
