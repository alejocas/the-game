import pygame
import cv2
import numpy as np


pygame.init()

#Tamaño de la ventana del juego que abre pygame
win = pygame.display.set_mode((640, 480))
#Título de la ventana de pygame
pygame.display.set_caption("The Game")

#Coordenadas iniciales de la figura
x = 0
y = 0
#Tamaño de la figura
width = 60
height = 80

red_detected = False
step_size = 10
#Velicidad a la que se mueve la figura, la velocidad es la cantidad de pixeles que se mueve
vel = 5

run = True

#Selección del umbral del color azul
l_h = 82
l_s = 51
l_v = 51
u_h = 133
u_s = 255
u_v = 255
lower_blue = np.array ([l_h, l_s, l_v]) #Umbral del azul bajo
higher_blue = np.array([u_h, u_s, u_v]) #Umbral del azul alto :3
# azulBajo = np.array([100,100,20],np.uint8)
# azulAlto = np.array([125,255,255],np.uint8)
def color_capture(cap, higher_color, lower_color, x, y):
    #Capturar la imagen
    ret, frame = cap.read()
    if ret==True:
        frame_hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV) # define range of blue color in HSV
        mask = cv2.inRange(frame_hsv, lower_color, higher_color)
        contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
        #cv2.drawContours(frame, contornos, -1, (255,0,0), 3)
        for c in contornos:
          area = cv2.contourArea(c)
          if area > 3000:
            M = cv2.moments(c)
            if (M["m00"]==0): M["m00"]=1
            x = int(M["m10"]/M["m00"])
            # y = int(M['m01']/M['m00'])
            y = 0
            cv2.circle(frame, (x,y), 7, (0,255,0), -1)
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, '{},{}'.format(x,y),(x+10,y), font, 0.75,(0,255,0),1,cv2.LINE_AA)
            nuevoContorno = cv2.convexHull(c)
            cv2.drawContours(frame, [nuevoContorno], 0, (255,0,0), 3)

        # cv2.imshow('maskAzul',mask)
        cv2.imshow('frame',frame)
    return x
#Inicialización de la cámara
cap = cv2.VideoCapture(0)
print(cap.get(3), cap.get(4))
rect_stack = []
while run:
    pygame.time.delay(100) # This will delay the game the given amount of milliseconds. In our casee 0.1 seconds will be the delay
    x = color_capture(cap, higher_blue, lower_blue, x, 0) #Obtenemos las coordenadas del objeto azul
    #Movimientos de la figura
    keys = pygame.key.get_pressed()  # This will give us a dictonary where each key has a value of 1 or 0. Where 1 is pressed and 0 is not pressed.
    if not(red_detected): # Checks is user is not putting a red object
        if keys[pygame.K_SPACE]:
            red_detected = True
    else:
        if y <= 430 - height:
            y += step_size
        else: # This will execute if our jump is finished
            red_detected = False
            falled_rect = (x, y, width, height)
            rect_stack.append(falled_rect)
            x, y = 0, 0
            # Resetting our Variables
    win.fill((0,0,0))  # Fills the screen with black
    actual_rect = (x, y, width, height)
    actual_rect = pygame.draw.rect(win, (255,0,0), actual_rect)  #This takes: window/surface, color, rect
    rect_stack = rect_stack[:]
    print("Rect stack")
    print(rect_stack)
    #pygame.display.update(rect_stack) # This updates the screen so we can see our rectangle
    for i in range(len(rect_stack)):
        pygame.draw.rect(win, (0,255,0), rect_stack[i])
        pygame.display.update(rect_stack[i])
    pygame.display.update()
 
    #For closing the windows
    for event in pygame.event.get():  # This will loop through a list of any keyboard or mouse events.
      if event.type == pygame.QUIT: # Checks if the red button in the corner of the window is clicked
        run = False  # Ends the game loop
    k = cv2.waitKey(1) 
    if k == 27: #Salir del programa con ESC
        break
    
  

pygame.quit()  # If we exit the loop this will execute and close our game

cap.release()
cv2.destroyAllWindows()

 