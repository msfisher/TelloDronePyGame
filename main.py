import time
from djitellopy import tello
import pygame

# initialize PyGame
pygame.init()

# create window for the drone camera images to be displayed in
screenWidth  = 300
screenHeight = 300
screenSize = (screenWidth, screenHeight)
droneWin = pygame.display.set_mode(screenSize)
pygame.display.set_caption("Tello Drone Remote Viewer")

drone = tello.Tello()                       # Create drone object
drone.connect()                             # connect to the drone
drone.streamon()                            # turn on video stream
readFrame = drone.get_frame_read()          # hook frame to the stream
imageScale = (screenWidth, screenHeight)    # amount to scale image from drone
SPEED = 50                                  # velocity of drone
SLEEP_TIME = 1                              # how long to sleep between commands


# function to draw image from drone onto window.
# 1) Paint the screen black
# 2) create a surface using the image from the drone
# 3) scale and then rotate the image
# 4) BLIT the image on the screen
# 5) update the display
def updateWindow(droneImage):
    droneWin.fill((0, 0, 0))
    frame = pygame.surfarray.make_surface(droneImage)
    frame = pygame.transform.rotate(pygame.transform.scale(frame, imageScale), 270)
    droneWin.blit(frame,(0,0))
    pygame.display.update()


# function to command the drone based on arguments passed
# lr = left or right velocity
# fb = forward or backward velocity
# ud = upward or downward velocity
# yaw = rotational velocity
def moveDrone(lr, fb, ud, yaw):
    drone.send_rc_control(lr, fb, ud, yaw)
    time.sleep(SLEEP_TIME)
    drone.send_rc_control(0, 0, 0, 0)

def main():
    keepGoing   = True  # flag to control main loop
    landed      = True  # flag to determine if flying or not

    # main loop to get user's key presses and display video
    while(keepGoing):
        img = readFrame.frame                       # get actual frame from the drone
        lrVel, fbVel, udVel, yawVel = 0, 0, 0, 0    # variables to control drone velocity

        # check which events have occurred
        for event in pygame.event.get():
            if(event.type == pygame.QUIT):
                keepGoing = False   # quit the loop
            if(event.type == pygame.KEYUP):
                if(not landed):                    # not on the ground
                    if(event.key == pygame.K_UP):
                        fbVel = SPEED              # translate forward
                    if (event.key == pygame.K_DOWN):
                        fbVel = -SPEED             # translate backward
                    if (event.key == pygame.K_LEFT):
                        lrVel = -SPEED             # translate left
                    if (event.key == pygame.K_RIGHT):
                        lrVel = SPEED              # translate right
                    if (event.key == pygame.K_w):
                        udVel = SPEED              # translate up
                    if (event.key == pygame.K_s):
                        udVel = -SPEED             # translate down
                    if (event.key == pygame.K_a):
                        yawVel = -SPEED            # rotate counter clockwise
                    if (event.key == pygame.K_d):
                        yawVel = SPEED             # rotate clockwise
                    if (event.key == pygame.K_q):
                        landed = True              # land
                        drone.send_rc_control(0, 0, 0, 0)
                        time.sleep(SLEEP_TIME)
                        drone.land()
                # while on ground only command that works is taking off
                else:
                    if (event.key == pygame.K_t):
                        landed = False
                        drone.takeoff()
                        time.sleep(SLEEP_TIME)

                # translate the drone based on velocities set in variables
                # only move the drone if user has pressed a key
                moveDrone(lrVel, fbVel, udVel, yawVel)
        # end of for loop grabbing window events

        updateWindow(img)
    # end of while loop

    # Shutting down, so if flying then stop flying and land
    if(not landed):
        drone.send_rc_control(0,0,0,0)
        time.sleep(SLEEP_TIME)
        drone.land()
    drone.streamoff()       # turn off stream
    pygame.display.quit()   # kill the display
    pygame.quit()           # shutdown pygame

    # display the battery charge when closing down
    print(f"Battery: {drone.get_battery()}")
# end of main function


# main entry into program
if __name__ == "__main__":
    main()