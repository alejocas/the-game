import pygame
import cv2
import numpy as np
import random

#This is a project for Digital Image Processing (DIP) course at the Universidad de Antioquia.

#--------------------------------------------------------------------------
#------- THE GAME ----------------------------------------------
#------- Conceptos básicos de PDI------------------------------------------
#------- Por: Alejandro Castaño Rojas  alejandro.castanor@udea.edu.co -----
#------- CC 1020484140  ---------------------------------------------------
#------- Por: Angélica Arroyave Mendoza angelica.arroyavem@udea.edu.co ----
#------- CC 1040756574  ---------------------------------------------------
#------- Curso Básico de Procesamiento de Digital de Imágenes -------------
#------- V0 Abril de 2010--------------------------------------------------
#--------------------------------------------------------------------------

# DESCRIPTION
# THE GAME! It is a construction simulator in which you must build a 7-story building !. 
# The challenge is to position the floors according to the floor that predicts it.
# You can position the floor using something blue in front of your camerera  
# and you can release the floor using something red in front of your camerera.

# TECHNOLOGIES
# Python 3
# OpenCV 3
# Pygames (python library)
# Numpy (python library)
# Random (python library)

#Game initialization
pygame.init()

#Window setup
game_height = 722
window_game = pygame.display.set_mode((630, game_height)) #Size
pygame.display.set_caption("The Game") #Título de la ventana de pygame

#Loading the assets for the game
background = pygame.image.load('./Assets/background.png')
floor = pygame.image.load('./Assets/floor.png')
first_floor = pygame.image.load('./Assets/first_floor.png')
exit_button = pygame.image.load('./Assets/exit_button.png')
try_again_button = pygame.image.load('./Assets/try_again_button.png')
win_button = pygame.image.load('./Assets/win_button.png')

#Adding the background image
window_game.blit(background, (0,0))
pygame.display.update() 

#Seting up the coordinates and constants
x = 0
y = 0
width = 60
height = 73
x_first_floor = random.randint(10, 600)
floor_stack = []
red_detected = False
step_size = 10  #Fall speed
run = True 
gamer_loses = False

#Setting the colors thresholds
lower_blue = np.array ([82,51, 51]) # Lower blue threshold
higher_blue = np.array([133, 255, 255]) # Higher blue threshold
lower_red = np.array ([0, 161, 0]) # Lower red threshold
higher_red = np.array([17,219, 255]) # Higher red threshold

# In this method we use the OpenCV library to catch the frame of the computer camera and 
# detect the objects with the specific color.
def color_capture(cap, higher_color, lower_color, x):
    ret, frame = cap.read() 
    if ret==True:
        # We use the the HSV (Hue, Saturation, Value) format because is used to separate image luminance 
        # from color information. This makes it easier when we are working on or need luminance of the image/frame.
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) #Converting from RGB to HSV
        mask = cv2.inRange(frame_hsv, lower_color, higher_color) #Creating the mask with the range of colors on the frame
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # Catching the red/blue contours 
        for c in contours: # Mapping all the found contours
            area = cv2.contourArea(c) #Catching the contour area
            if area > 3000:
                M = cv2.moments(c)
                if (M["m00"] == 0): M["m00"]=1
                x = int(M["m10"]/M["m00"]) #Getting the x coordinate
                y = 0 # Setting  the y coordinate to 0 because we don't want to move the floor vertically 
                cv2.circle(frame, (x,y), 7, (0,255,0), -1) 
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(frame, '{},{}'.format(x,y),(x+10,y), font, 0.75,(0,255,0),1,cv2.LINE_AA)
                nuevoContorno = cv2.convexHull(c)
                cv2.drawContours(frame, [nuevoContorno], 0, (255,0,0), 3) #Drawing the found contours
        cv2.imshow('frame',frame) # Displaying the frame with the contours and the coordinates
    return x

# This method draws the floor on the pygame window with determined coordinates.
def draw_floor(floor_image,x_pos, y_pos):
    window_game.blit(floor_image,(x_pos, y_pos))

# This method consults the floor_array (which contains the fallen floors) and draws them on the canvas.
def draw_still_floors(floor_array):
    for i in range(len(floor_array)):
        floor_image,x_pos,y_pos = floor_array[i]
        draw_floor(floor_image,x_pos, y_pos)

# This method is called for drawing the game buttons.
def draw_buttons(second_button_name):
    window_game.blit(exit_button,(100, 250))             
    window_game.blit(second_button_name,(300, 250))

# Camera initialization
cap = cv2.VideoCapture(0)
print(cap.get(3), cap.get(4))


#This while is our principal thread, is in charge of the game loop.
while run:
    
    pygame.time.delay(100)  # This will delay the game the given amount of milliseconds. In our casee 0.1 seconds will be the delay
    x = color_capture(cap, higher_blue, lower_blue, x)  # Catching the blue object coordinates
    red_validation = color_capture(cap, higher_red, lower_red, 0) # Detecting the red object

    # Floor movements
    if not(red_detected):  # Checks is user is not putting a red object
        if red_validation != 0:
            red_detected = True
    else:
        if x >= x_first_floor - 50 and x <= x_first_floor + 50: # Checking if the fallen floor is nearby the previous floor.
            if (y + height<= floor_stack[len(floor_stack) - 1][2]): #Check if the floor is already on the target spot.
                y += step_size
            else:  # This will execute if our floor finally get to the floor; the floor is added to the falled_floor stack and start with a new one.
                red_detected = False
                falled_floor = (floor,x, y)
                floor_stack.append(falled_floor)
                x, y = 0, 0
                # Resetting our Variables
        else: # If the fallen if far away from the previous one, then we let it fall until the floor touches the "y" limit.
            if (y + height*1.5 <= game_height):
                y += step_size
            else:    # When it touches the "y" limit, the player loses.       
                gamer_loses = True

    window_game.blit(background, (0,0))
    draw_floor(floor,x,y) #Drawing the main floor.
    draw_still_floors(floor_stack) # Checking if there is a floor in the fallen stack and drawing them.

    if len(floor_stack) == 0: # This if allows us to draw the first floor in the ground.
        first_floor_stack = (first_floor,x_first_floor,615)
        floor_stack.append(first_floor_stack)
    if gamer_loses or len(floor_stack) == 8: #When the player loses, we draw the buttons for "exit" or "start over". When the player wins, he/she wins :v
        image_condition = win_button if len(floor_stack) == 8 else try_again_button
        draw_buttons(image_condition) #We are calling the method who draws the buttons on the pygame window.
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
    if k == 27:  # Ends the Video Capturing and closes the game.
        break


pygame.quit()  # If we exit the loop this will execute and close our game.

cap.release()
cv2.destroyAllWindows()


