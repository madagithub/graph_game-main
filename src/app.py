import numpy as np
import pygame
import car_plot_constants as constants
from sensor import Sensor
from serial import SerialException

import time

x = []
y = []
mean_y = 100.0
number_of_points = constants.NUM_OF_PLOT_POINTS

sin_y = []
sin_x = []


Full_Screen_W = 0
Full_Screen_H = 0

present = 100

def fill_linear_data(slop):
    global y
    global number_of_points
    del y[:]
    for i in range(0, number_of_points):
        y.append(i*slop)

# create the array that holds the y values of the sine function. 
def create_sin():
    global sin_y
    points = np.arange(0,number_of_points  , 0.2) # calculate an array of x valuse based on the number of point with an step of 0.2.
    offset = 1.5 # offset from the top of the screen. 
    
    for x in points:
        sin_y.append((np.sin(x) + offset ) * 200) # calculate the y values. 
    

# function to update the y values of the sensor data with the new data from the sensor.  
def update_plot_data(new_data):
    global Full_Screen_W
    global Full_Screen_H
    global y

    y.append(new_data) # append the new data from the sensor to the end of the array. 
    y.pop(0) # remove the data at the start of thee array. 


# function to draw the graph of the sensor data on the screen. 
def update_plot():
    global Full_Screen_W
    global Full_Screen_H
    global x
    global y
    global sin_y
    global number_of_points
    thick = constants.LINE_WIDTH
    color = constants.LINE_COLOR
    bg_color = (255,255,255)
    offset = 250 # offset from the right of the screen in px.
    x_left = 0# x left
    x1 = x_left
    y1 =y[0]
    dx = (Full_Screen_W-x_left)/(number_of_points-1)
    main_screen.fill(bg_color)
    for i in range(1, number_of_points):
        x2 = x_left + i*dx - offset
        y2 = y[i]
        pygame.draw.line(main_screen, color,(x1, y1), (x2 ,y2), thick)
        x1 = x2
        y1 = y2
    #pygame.display.flip()

# function to update the data of the sine array. 
def update_plot_data_sin():
    global Full_Screen_W
    global Full_Screen_H
    global sin_y
    new_data = sin_y.pop(0) # pop the data at the start of the array. 
    sin_y.append(new_data) # append the data to the end of the array to create a continuos sine function. 

# function to draw the sine graph on screen. 
def update_sin():
    global Full_Screen_W
    global Full_Screen_H
    global x
    global sin_y
    global number_of_points
    thick = constants.LINE_WIDTH 
    color = constants.SIN_LINE_COLOR
    x_left = 0 # x left
    x1 = x_left
    y1 =sin_y[0]
    dx = (Full_Screen_W-x_left)/(number_of_points-1)
    for i in range(number_of_points  * 4): # the number of points in the sine array is 4 times larger than the number_of_points. 
        x2 = x_left + i*dx
        y2 = sin_y[i]
        pygame.draw.line(main_screen, color,(x1, y1), (x2,y2), thick)
        x1 = x2
        y1 = y2 

    #pygame.display.flip()

# TODO fix the calc function. 
def calc_score():
    global sin_y
    global y 
    diff = 0
    global present
    
    for i in range(0 , 1000 , 5):
        d =  int(abs(y[int(i / 5)] -  sin_y[i]))
        
        if d <= 40:
            diff = 1

        elif d > 40 and d <= 100:
            diff = 2

        elif d > 100 and d <= 180:
            diff = 3

        elif d > 180 and d <= 300:
            diff = 4    

        else:
            diff = 5
    
        
        if diff == 1 and present < 100:
            present = present + 15

        elif diff == 2 and present < 100:
            present = present + 10
        
        elif diff == 3 and present < 100:
            present = present + 5

        elif diff == 4 and present > 5:
            present = present - 5

        elif diff == 5 and present > 5:
            present = present - 10


# establish the connection with the sensor. if it fails it will try to reconnect. 
try:        
    ser = Sensor()
except SerialException:
    ser.reconnect(Sensor())

# create the sine array, and fill the sensor array with dummy data that will be overwritten later. 
create_sin()
fill_linear_data(5)

# initialize pygame 
pygame.init()
clock = pygame.time.Clock
infoObject = pygame.display.Info() #get information about dispaly 
Full_Screen_W = infoObject.current_w # used later for full screen update 
Full_Screen_H = infoObject.current_h
main_screen = pygame.display.set_mode((Full_Screen_W, Full_Screen_H))

bg_color = (255, 255, 255) 
main_screen.fill(bg_color)

font = pygame.font.SysFont('Arial', 25)


# main runtime loop. 
running =  True

while (1):
    if running:
        try:
            # draw the graphs on screen. 
            distance =  (ser.get_data() / 2)
            update_plot_data(distance)                
            update_plot()
            update_plot_data_sin()
            update_sin()
            calc_score()
            
            textsurface = font.render(f"{present}%", False, (0, 0, 0))
            main_screen.blit(textsurface,( int(Full_Screen_W/2) , 20))
            
            pygame.display.update()
            
        except SerialException:
            ser.reconnect(Sensor())
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print('done')
                running = False
                pygame.quit()
                ser.ser.close()
                break
    else:
        break