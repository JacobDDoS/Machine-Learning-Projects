import random
import pygame
from enum import Enum
import os 
import math

class Direction(Enum):
    RIGHT = 1
    LEFT = -1

WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT)) 

WHITE = 255, 255, 255
BLACK = 0, 0, 0

FPS = 60
PADDLE_SPEED = 7

BALL_X_SPEED = 3
BALL_Y_SPEED = 0

PADDLE_WIDTH, PADDLE_HEIGHT = 15, 80
BALL_WIDTH, BALL_HEIGHT = 15, 15

BALL_DIRECTION = Direction.RIGHT

leftScore, rightScore = 0, 0

def drawWindow(leftPaddle, rightPaddle, ball):
    #Background
    WIN.fill(WHITE)

    #Paddles
    pygame.draw.rect(WIN, BLACK, leftPaddle) 
    pygame.draw.rect(WIN, BLACK, rightPaddle) 

    #Ball
    pygame.draw.rect(WIN, BLACK, ball)

    #Update Screen 
    pygame.display.update() 

def handlePaddleMovement(keysPressed, leftPaddle, rightPaddle):
    #left paddle
    if keysPressed[pygame.K_w] and leftPaddle.y >= 0:
        leftPaddle.y -= PADDLE_SPEED
        leftPaddle.y = max(0, leftPaddle.y)
    if keysPressed[pygame.K_s] and leftPaddle.y <= HEIGHT - PADDLE_HEIGHT:
        leftPaddle.y += PADDLE_SPEED
        leftPaddle = min(HEIGHT, leftPaddle.y)

    #right paddle
    if keysPressed[pygame.K_UP] and rightPaddle.y >= 0:
        rightPaddle.y -= PADDLE_SPEED
        rightPaddle.y = max(0, rightPaddle.y)
    if keysPressed[pygame.K_DOWN] and rightPaddle.y <= HEIGHT - PADDLE_HEIGHT:
        rightPaddle.y += PADDLE_SPEED
        rightPaddle.y = min(HEIGHT, rightPaddle.y) 

def resetBall(ball):
    global BALL_DIRECTION, BALL_X_SPEED, BALL_Y_SPEED
    ball.x = WIDTH//2
    ball.y = HEIGHT//2
    BALL_DIRECTION = Direction.RIGHT
    BALL_X_SPEED = 3
    BALL_Y_SPEED = 0

def handleBall(ball, leftPaddle, rightPaddle):
    global BALL_DIRECTION, BALL_Y_SPEED, BALL_X_SPEED, leftScore, rightScore

    BALL_X_SPEED = min(20, BALL_X_SPEED)

    #Update x value of ball
    if BALL_DIRECTION == Direction.RIGHT:
        ball.x += BALL_X_SPEED
    elif BALL_DIRECTION == Direction.LEFT:
        ball.x -= BALL_X_SPEED

    #Update y value of ball
    ball.y += math.ceil(BALL_Y_SPEED)

    #Check if ball has hit top or bottom wall
    if ball.y <= 0:
        BALL_Y_SPEED *= -1
        ball.y = 1
    
    if ball.y+BALL_HEIGHT >= HEIGHT:
        BALL_Y_SPEED *= -1
        ball.y = HEIGHT-1-BALL_HEIGHT

    #Check if ball has hit left or right wall and that it didn't go through a paddle
    if ball.x <= 0 and (ball.y+BALL_HEIGHT > leftPaddle.y or ball.y < leftPaddle.y + PADDLE_HEIGHT):
        rightScore += 1
        resetBall(ball)
    if ball.x+BALL_WIDTH >= WIDTH and (ball.y+BALL_HEIGHT > rightPaddle.y or ball.y < rightPaddle.y + PADDLE_HEIGHT):
        leftScore += 1
        resetBall(ball) 
    
    
    if leftPaddle.colliderect(ball) or (ball.y+BALL_HEIGHT <= leftPaddle.y and ball.y >= leftPaddle.y+PADDLE_HEIGHT and ball.x <= 5+PADDLE_WIDTH):
        BALL_DIRECTION = Direction.RIGHT
        ball.x = max(5+PADDLE_WIDTH, ball.x) 
        BALL_X_SPEED += 1
        #if top part of paddle, decrease ball.y, else increase ball.y
        if ball.y+BALL_HEIGHT//2 > leftPaddle.y+PADDLE_HEIGHT//2:
            BALL_Y_SPEED += 1
        else:
            BALL_Y_SPEED -= 1
    
    if rightPaddle.colliderect(ball) or (ball.y+BALL_HEIGHT <= rightPaddle.y and ball.y >= rightPaddle.y+PADDLE_HEIGHT and ball.x >= WIDTH-5-PADDLE_WIDTH):
        BALL_DIRECTION = Direction.LEFT
        ball.x = min(WIDTH-5-PADDLE_WIDTH, ball.x)
        BALL_X_SPEED += 1
        #if top part of paddle, decrease ball.y, else increase ball.y
        if ball.y+BALL_HEIGHT//2 > rightPaddle.y+PADDLE_HEIGHT//2:
            BALL_Y_SPEED += 1
        else:
            BALL_Y_SPEED -= 1

def main():
    leftPaddle = pygame.Rect(5, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    rightPaddle = pygame.Rect(WIDTH-5-PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(WIDTH//2, HEIGHT//2, BALL_WIDTH, BALL_HEIGHT)
    clock = pygame.time.Clock()
    isGameRunning = True 
    while isGameRunning:
        clock.tick(FPS) 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isGameRunning = False
                pygame.quit()

        keysPressed = pygame.key.get_pressed()
        handlePaddleMovement(keysPressed, leftPaddle, rightPaddle)
        handleBall(ball, leftPaddle, rightPaddle)
        drawWindow(leftPaddle, rightPaddle, ball)
    
    main()

if __name__ == '__main__':
    main()