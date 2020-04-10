import pygame
import cv2
import numpy as np
import random


pygame.init()

#Tamaño de la ventana del juego que abre pygame
game_height = 722
win = pygame.display.set_mode((640, game_height))
#Título de la ventana de pygame
pygame.display.set_caption("The Game")
bg = pygame.image.load('./Assets/background.png')
floor = pygame.image.load('./Assets/floor.png')
first_floor = pygame.image.load('./Assets/first_floor.png')
exit_button = pygame.image.load('./Assets/exit_button.png')
try_again_button = pygame.image.load('./Assets/try_again_button.png')
win.blit(bg, (0,0))
pygame.display.update() 
#Coordenadas iniciales de la figura
x = 0
y = 0
#Tamaño de la figura
width = 60
height = 73
x_first_floor = random.randint(10, 600)
red_detected = False
step_size = 10
#Velicidad a la que se mueve la figura, la velocidad es la cantidad de pixeles que se mueve
vel = 5

run = True
gamer_loses = False
#Selección del umbral del color azul
l_h = 82
l_s = 51
l_v = 51
u_h = 133
u_s = 255
u_v = 255
lower_blue = np.array ([l_h, l_s, l_v]) #Umbral del azul bajo
higher_blue = np.array([u_h, u_s, u_v]) #Umbral del azul alto :3
lower_red = np.array ([0, 161, 0]) #Umbral del rojo bajo
higher_red = np.array([17,219, 255]) #Umbral del rojo alto :3


def color_capture(cap, higher_color, lower_color, x):
    #Capturar la imagen
    ret, frame = cap.read()
    if ret==True:
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) # define range of blue color in HSV
        mask = cv2.inRange(frame_hsv, lower_color, higher_color)
        contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
        for c in contornos:
          area = cv2.contourArea(c)
          if area > 3000:
            M = cv2.moments(c)
            if (M["m00"] == 0): M["m00"]=1
            x = int(M["m10"]/M["m00"])
            y = 0
            cv2.circle(frame, (x,y), 7, (0,255,0), -1)
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, '{},{}'.format(x,y),(x+10,y), font, 0.75,(0,255,0),1,cv2.LINE_AA)
            nuevoContorno = cv2.convexHull(c)
            cv2.drawContours(frame, [nuevoContorno], 0, (255,0,0), 3)
        cv2.imshow('frame',frame)
    return x

def draw_still_rectangles(rect_array):
    for i in range(len(rect_array)):
        floor_image,x_pos,y_pos = rect_array[i]
        draw_floor(floor_image,x_pos, y_pos)

def draw_floor(floor_image,x_pos, y_pos):
    win.blit(floor_image,(x_pos, y_pos))

def draw_buttons(second_button_name):
    win.blit(exit_button,(100, 250))             
    win.blit(second_button_name,(300, 250))

# Inicialización de la cámara
cap = cv2.VideoCapture(0)
print(cap.get(3), cap.get(4))
floor_stack = []

while run:
    
    pygame.time.delay(100)  # This will delay the game the given amount of milliseconds. In our casee 0.1 seconds will be the delay
    x = color_capture(cap, higher_blue, lower_blue, x)  # Obtenemos las coordenadas del objeto azul
    red_validation = color_capture(cap, higher_red, lower_red, 0)
    # Movimientos de la figura
    if not(red_detected):  # Checks is user is not putting a red object
        if red_validation != 0:
            red_detected = True
    else:
        if x >= x_first_floor - 50 and x <= x_first_floor + 50: 
            if (y + height<= floor_stack[len(floor_stack) - 1][2]):
                y += step_size
            else:  # This will execute if our jump is finished
                red_detected = False
                falled_floor = (floor,x, y)
                floor_stack.append(falled_floor)
                x, y = 0, 0
                # Resetting our Variables
        else:
            if (y + height<= game_height):
                y += step_size
            else:                
                gamer_loses = True

    win.blit(bg, (0,0))
    draw_floor(floor,x,y)
    draw_still_rectangles(floor_stack)
    if len(floor_stack) == 0:
        first_floor_stack = (first_floor,x_first_floor,615)
        floor_stack.append(first_floor_stack)
    if gamer_loses:
        draw_buttons(try_again_button) #We are calling the method who draws the buttons on the pygame window.
        pygame.display.update()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: #If the user presses the "a" key on the keyboard, the game will start over.
            red_detected = False
            x, y = 0, 0
            gamer_loses = False
            floor_stack = []
            x_first_floor = random.randint(10, 600)
        if keys[pygame.K_b]: #If the user presses the "b" key on the keyboard, the game will be closed.
            run = False
    pygame.display.update()

    # For closing the windows in general.
    for event in pygame.event.get():  # This will loop through a list of any keyboard or mouse events.
      if event.type == pygame.QUIT:  # Checks if the red button in the corner of the window is clicked
        run = False  # Ends the game loop and closes the video capturing.
    k = cv2.waitKey(1) 
    if k == 27:  # Ends the Video Capturing and closes the game
        break


pygame.quit()  # If we exit the loop this will execute and close our game

cap.release()
cv2.destroyAllWindows()


