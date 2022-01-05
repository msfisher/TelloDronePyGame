import sys
import time

from djitellopy import tello
import pygame

# initialize PyGame
pygame.init()

# create window for the drone camera images to be displayed in
screenWidth  = 600
screenHeight = 600
screenSize = (screenWidth, screenHeight)
droneWin = pygame.display.set_mode(screenSize)
pygame.display.set_caption("Tello Drone Remote Viewer")

# create drone object, connect to it, turn on streaming, hook a frame to the stream
# in the main loop call <objectname>>.frame to get the actual frame received
drone = tello.Tello()
drone.connect()
drone.streamon()
readFrame = drone.get_frame_read()

# Frames Per Second constant to control updates to window and what size
# to scale the image from the drone
FPS = 60
imageScale = (screenWidth, screenHeight)
lrVel  = 0      # Left and Right Velocity
fbVel  = 0      # Forward and Backward Velocity
udVel  = 0      # Up and Down Velocity
yawVel = 0      # Yaw Velocity
landing = True  # Drone on ground or in flight


# function to draw image from drone onto window.
# 1) Paint the screen black
# 2) create a surface using the image from the drone
# 3) scale and then rotate the image
# 4) BLIT the image on the screen
# 5) update the display
def updateWindow(droneImage):
    droneWin.fill((0,0,0))
    frame = pygame.surfarray.make_surface(droneImage)
    frame = pygame.transform.rotate(pygame.transform.scale(frame, imageScale), 270)
    droneWin.blit(frame,(0,0))
    pygame.display.update()


# function to move the drone based on user's key presses
def moveDrone(keysPressed):
    if (keysPressed[pygame.K_w]):
        udVel = 50                      # Move Up
    if (keysPressed[pygame.K_a]):
        yawVel = -50                    # Rotate counter clockwise
    if (keysPressed[pygame.K_d]):
        yawVel = 50                     # Rotate clockwise
    if (keysPressed[pygame.K_s]):
        udVel = -50                     # Move Down
    if(keysPressed[pygame.K_q]):
        landing = True                  # Land the Drone
    if (keysPressed[pygame.K_t]):
        if(landing):
            landing = False
            drone.takeoff()
            time.sleep(2)
    if (keysPressed[pygame.K_LEFT]):
        lrVel = -50                     # Move Left
    if (keysPressed[pygame.K_RIGHT]):
        lrVel = 50                      # Move Right
    if (keysPressed[pygame.K_UP]):
        fbVel = 50                      # Move Forward
    if (keysPressed[pygame.K_DOWN]):
        fbVel = -50                     # Move Backward

    # if the drone is not on the ground then send the command
    if(not landing):
        drone.send_rc_control(lrVel,fbVel,udVel,yawVel)
        time.sleep(2)

def main():
    keepGoing = True
    clock = pygame.time.Clock()     # create a timer to control FPS

    # main loop to get user's key presses and display video
    while(keepGoing):
        clock.tick(FPS)             # control speed by only running the loop as fast as FPS
        img = readFrame.frame       # get actual frame from the drone

        # check which events have occurred
        for event in pygame.event.get():
            if(event.type == pygame.QUIT):
                keepGoing = False   # quit the loop
        # end of for loop grabbing window events

        # process the key presses
        keysPressed = pygame.key.get_pressed()
        if(keepGoing):
            moveDrone(keysPressed)
            updateWindow(img)
    # end of while loop

    # Shutting down, so if flying then stop and land
    if(not landing):
        drone.send_rc_control(0,0,0,0)
        time.sleep(2)
        drone.land()
    drone.streamoff()
    pygame.display.quit()
    pygame.quit()

    print(f"Battery: {drone.get_battery()}")
# end of main function


# main entry into program
if __name__ == "__main__":
    main()