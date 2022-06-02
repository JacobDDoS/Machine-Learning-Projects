import random
import torch
import pygame
from enum import Enum
import os 
import math
from agent import Agent

pygame.font.init()



class Direction(Enum):
    RIGHT = 1
    LEFT = -1

WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT)) 

WHITE = 255, 255, 255
BLACK = 0, 0, 0

FPS = 200
PADDLE_SPEED = 7

BALL_X_SPEED = 12
BALL_Y_SPEED = 0

PADDLE_WIDTH, PADDLE_HEIGHT = 15, 80
BALL_WIDTH, BALL_HEIGHT = 15, 15

BALL_DIRECTION = Direction.LEFT

SCORE_FONT = pygame.font.SysFont('comicsans', 40)
TITLE_FONT = pygame.font.SysFont('comicsans', 50) 

leftScore, rightScore = 0, 0

rightHits = 0

rightRecord = 0
reward = 0
done = False

class PingPongGame():
    def reset(self, leftPaddle, rightPaddle, ball, done=True):
        global leftScore, rightScore
        self.resetBall(ball)
        if done:
            leftScore, rightScore = 0, 0
        # leftPaddle.y = HEIGHT//2 - PADDLE_HEIGHT//2
        rightPaddle.y = HEIGHT//2 - PADDLE_HEIGHT//2

    def drawWindow(self, leftPaddle, rightPaddle, ball):
        #Background
        WIN.fill(WHITE)

        #Score
        leftScoreText = SCORE_FONT.render(str(leftScore), 1, BLACK) 
        rightScoreText = SCORE_FONT.render(str(rightScore), 1, BLACK)
        WIN.blit(leftScoreText, (40, 10)) 
        WIN.blit(rightScoreText, (WIDTH-rightScoreText.get_width()-40, 10))

        #Paddles
        pygame.draw.rect(WIN, BLACK, leftPaddle) 
        pygame.draw.rect(WIN, BLACK, rightPaddle) 

        #Ball
        pygame.draw.rect(WIN, BLACK, ball)

        #Update Screen 
        pygame.display.update() 

    def AIMove(self, action, paddle):
        if action[0]:
            paddle.y -= PADDLE_SPEED
            paddle.y = max(0, paddle.y) 
        elif action[1]:
            paddle.y += PADDLE_SPEED
            paddle.y = min(HEIGHT-PADDLE_HEIGHT, paddle.y) 

    def handlePaddleMovement(self, keysPressed, leftPaddle=None, rightPaddle=None):
        #left paddle
        if leftPaddle != None:
            if keysPressed[pygame.K_w] and leftPaddle.y >= 0:
                leftPaddle.y -= PADDLE_SPEED
                leftPaddle.y = max(0, leftPaddle.y)
            if keysPressed[pygame.K_s] and leftPaddle.y <= HEIGHT - PADDLE_HEIGHT:
                leftPaddle.y += PADDLE_SPEED
                leftPaddle = min(HEIGHT-PADDLE_HEIGHT, leftPaddle.y)

        #right paddle
        if rightPaddle != None:
            if keysPressed[pygame.K_UP] and rightPaddle.y >= 0:
                rightPaddle.y -= PADDLE_SPEED
                rightPaddle.y = max(0, rightPaddle.y)
            if keysPressed[pygame.K_DOWN] and rightPaddle.y <= HEIGHT - PADDLE_HEIGHT:
                rightPaddle.y += PADDLE_SPEED
                rightPaddle.y = min(HEIGHT, rightPaddle.y) 

    def resetBall(self, ball):
        global BALL_DIRECTION, BALL_X_SPEED, BALL_Y_SPEED
        ball.x = WIDTH//2
        ball.y = HEIGHT//2
        BALL_DIRECTION = Direction.LEFT
        BALL_X_SPEED = 12
        BALL_Y_SPEED = 0

    def handleBall(self, ball, leftPaddle, rightPaddle):
        global BALL_DIRECTION, BALL_Y_SPEED, BALL_X_SPEED, leftScore, rightScore, done, reward, rightHits

        BALL_X_SPEED = min(15, BALL_X_SPEED)

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
            if rightScore >= 5:
                done = True 
            self.reset(leftPaddle, rightPaddle, ball, done=False)
        if ball.x+BALL_WIDTH >= WIDTH and (ball.y+BALL_HEIGHT > rightPaddle.y or ball.y < rightPaddle.y + PADDLE_HEIGHT):
            leftScore += 1
            if leftScore >= 5:
                done = True 
            reward = -10
            self.reset(leftPaddle, rightPaddle, ball, done=False) 
        
        
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
            #update reward
            reward = 10
            rightHits += 1

            #if top part of paddle, decrease ball.y, else increase ball.y
            if ball.y+BALL_HEIGHT//2 > rightPaddle.y+PADDLE_HEIGHT//2:
                BALL_Y_SPEED += 1
            else:
                BALL_Y_SPEED -= 1

    def playerVersusPlayer(self):
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
            self.handlePaddleMovement(keysPressed, leftPaddle, rightPaddle)
            self.handleBall(ball, leftPaddle, rightPaddle)
            self.drawWindow(leftPaddle, rightPaddle, ball)
        
        self.main()

    def playerVersusBot(self):
        global reward, done, rightScore, rightRecord, rightRecord, rightHits
        # leftPaddle = pygame.Rect(5, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
        leftPaddle = pygame.Rect(5,0, PADDLE_WIDTH, HEIGHT)
        rightPaddle = pygame.Rect(WIDTH-5-PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
        ball = pygame.Rect(WIDTH//2, HEIGHT//2, BALL_WIDTH, BALL_HEIGHT)
        clock = pygame.time.Clock()
        isGameRunning = True 

        agent = Agent()
        

        while isGameRunning:
            #Retrive the current state
            isHigher = ball.y+BALL_HEIGHT < rightPaddle.y + 20
            isLower = ball.y+20 > rightPaddle.y + PADDLE_HEIGHT
            distance = rightPaddle.x - ball.x + BALL_WIDTH
            state_old = agent.get_state(isHigher, isLower)

            # print("Higher:", isHigher, "Lower:", isLower, "distance:",distance)

            #Get a move based on the current state
            final_move = agent.get_action(state_old) 

            #Perform move and get new state
            self.AIMove(final_move, rightPaddle)

            #get the new state
            isHigher = ball.y+BALL_HEIGHT > rightPaddle.y 
            isLower = ball.y < rightPaddle.y + PADDLE_HEIGHT
            distance = rightPaddle.x - ball.x + BALL_WIDTH
            state_new = agent.get_state(isHigher, isLower)

            #Train short-term memory
            agent.train_short_memory(state_old, final_move, reward, state_new, done) 

            #Remember
            agent.remember(state_old, final_move, reward, state_new, done)

            reward = 0

            if done:
                #Train long term memory
                self.reset(leftPaddle, rightPaddle, ball)
                agent.n_games += 1
                agent.train_long_memory() 

                if rightHits > rightRecord:
                    rightRecord = rightHits 
                    print("NEW RECORD:", rightRecord)
                    agent.model.save()

                print("Game:", agent.n_games, "Score:", rightHits)
                rightHits = 0
                done = False 

            clock.tick(FPS) 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    isGameRunning = False
                    pygame.quit()

            keysPressed = pygame.key.get_pressed()
            self.handlePaddleMovement(keysPressed, leftPaddle)
            self.handleBall(ball, leftPaddle, rightPaddle)
            self.drawWindow(leftPaddle, rightPaddle, ball)
        
        self.main()

    def main(self):
        titleText1 = TITLE_FONT.render("Press 1 for Player versus Player", 1, WHITE)
        titleText2 = TITLE_FONT.render("Press 2 for Player versus Bot", 1, WHITE)
        titleText3 = TITLE_FONT.render("Press 3 for Bot versus Bot", 1, WHITE)
        titleText = [titleText1, titleText2, titleText3]
        for idx in range(len(titleText)):
            WIN.blit(titleText[idx], (10, idx*70))
        pygame.display.update()

        isTitleRunning = True
        clock = pygame.time.Clock()
        while isTitleRunning:
            clock.tick(FPS) 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    isTitleRunning = False 
                    pygame.quit() 
            
            keysPressed = pygame.key.get_pressed() 
            if keysPressed[pygame.K_1]:
                self.playerVersusPlayer()
            elif keysPressed[pygame.K_2]:
                self.playerVersusBot()
        
        self.main() 

game = PingPongGame()
game.main()