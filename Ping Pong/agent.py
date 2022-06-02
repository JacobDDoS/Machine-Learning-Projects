import torch
import random
import numpy as np 
from collections import deque
from model import Linear_QNet, QTrainer

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate (must be smaller than 1)
        self.memory = deque(maxlen=MAX_MEMORY) # will call popleft() if it takes up too much memory
        self.model = Linear_QNet(2, 32, 3)
        self.model.load_state_dict(torch.load('./model/model.pth'))
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
    
    def get_state(self, isHigher, isLower):
        state = [isHigher, isLower]
        return np.array(state, dtype=int) 

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # returns a list of tuples  
        else: 
            mini_sample = self.memory 

        states, actions, rewards, next_states, dones = zip(*mini_sample) 
        self.trainer.train_step(states, actions, rewards, next_states, dones) 

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done) 

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation 
        self.epsilon = 80 - self.n_games
        final_move = [0, 0, 0] 
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2) 
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item() 
            final_move[move] = 1

            # print("final_move:", final_move)

        return final_move   

# def train():
#     record = 0
#     agent = Agent()
#     while True:
#         # get old state 
#         state_old = agent.get_state(game)

#         # get move
#         final_move = agent.get_action(state_old) 

#         # perform move and get new state
#         reward, done, score = game.play_step(final_move)
#         state_new = agent.get_state(game) 

#         # train short memory 
#         agent.train_short_memory(state_old, final_move, reward, state_new, done) 

#         # remember
#         agent.remember(state_old, final_move, reward, state_new, done)

#         if done: 
#             # train long memory, plot result
#             game.reset() 
#             agent.n_games += 1
#             agent.train_long_memory() 

#             if score > record:
#                 record = score 
#                 agent.model.save() 
#                 print("Game", agent.n_games, 'Score', score, 'Record:', record) 


# if __name__ == "__main__":
#     train() 