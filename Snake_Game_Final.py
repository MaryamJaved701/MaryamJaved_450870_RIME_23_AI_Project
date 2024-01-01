import tkinter as tk
import os
import random
import time
import math

class SnakeGame:
    def __init__(self, master):
        self.master = master    # Allows access the main window
        self.master.title("Snake Game")
        self.master.geometry("600x600") 
        self.master.resizable(False, False)

        self.canvas = tk.Canvas(self.master, bg="#3658a8", width=600, height=600)
        self.canvas.pack()

        self.scoreboard = 0  # User's score
        self.ai_scoreboard = 0  # AI's score
        
        # User Snake
        self.snake = [(100, 100), (90, 100)]    # Initial snake consists of two blocks
        self.direction = "Right"                # Initial direction of the snake
        self.snake_size = 20

        # Add an AI snake
        self.ai_snake = [(200, 200), (190, 200)]
        self.ai_direction = "Right"
        self.ai_snake_size = 20

        self.obstacles = self.create_obstacles() # Call function to create obstacles
        self.food = self.create_food()           # call function to create food

        self.master.bind("<KeyPress>", self.change_direction)   # Allows the user to control snake using keyboard keys

        self.previous_ai_snake_head = None

        self.snake_moving = True
        self.start_time = time.time()
        self.game_duration = 60  # Set the game duration in seconds
        self.update()

    def set_title(self):
        self.master.title(f"Snake Game - User Score: {self.scoreboard} | AI Score: {self.ai_scoreboard}")

    '''
    Take a random integer from 0 to 20 and multiply it with the snake size to convert it to pixels.
    Using this define the coordinates for the food on the canvas)
    '''
    
    def create_food(self):
        while True:
            x = random.randint(0, 20) * self.snake_size
            y = random.randint(0, 20) * self.snake_size
            food_coords = (x, y, x + self.snake_size, y + self.snake_size)
            if (
                food_coords not in self.obstacles
                and food_coords not in self.snake
                and food_coords not in self.ai_snake
            ):
                break           # Breaks out of the loop if the above conditions are met
        food = self.canvas.create_oval(food_coords, fill="#e64d0b", tags="food")
        return food

    def create_obstacles(self):
        obstacles = []
        for _ in range(8):
            while True:
                x = random.randint(0, 29) * self.snake_size
                y = random.randint(0, 29) * self.snake_size
    
                obstacle_coords = (x, y, x + self.snake_size, y + self.snake_size)
    
                # Check if the obstacle overlaps with the user snake or AI snake
                if (
                    obstacle_coords not in obstacles
                    and obstacle_coords not in self.snake
                    and obstacle_coords not in self.ai_snake
                ):
                    obstacles.append(obstacle_coords)
                    self.canvas.create_rectangle(obstacle_coords, fill="purple", outline="black", tags="obstacle")
                    break
    
        return obstacles

    def move_snake(self, snake, direction):
        head = snake[0]
        new_head = None

        if direction == "Right":
            new_head = (head[0] + self.snake_size, head[1])
        elif direction == "Left":
            new_head = (head[0] - self.snake_size, head[1])
        elif direction == "Up":
            new_head = (head[0], head[1] - self.snake_size)
        elif direction == "Down":
            new_head = (head[0], head[1] + self.snake_size)

        if (new_head is not None and
            (new_head[0] < 0
            or new_head[0] >= 600
            or new_head[1] < 0
            or new_head[1] >= 600
            or new_head in snake[1:]
        )):
            return False

        snake.insert(0, new_head)
        snake.pop()

        return True
    
    def move_ai_snake(self, ai_snake):
        head = self.ai_snake[0]
        new_head = None

        # Move toward the food
        food_coords = self.canvas.coords(self.food)
        if head[0] < food_coords[0]:
            new_head = (head[0] + self.snake_size, head[1])
        elif head[0] > food_coords[0]:
            new_head = (head[0] - self.snake_size, head[1])
        elif head[1] < food_coords[1]:
            new_head = (head[0], head[1] + self.snake_size)
        elif head[1] > food_coords[1]:
            new_head = (head[0], head[1] - self.snake_size)
            
        '''
        The above block ensures that if new_head is not set (meaning the AI snake is already aligned
        with the food), it calculates the new head position based on the difference between the current
        head position and the previous head position.
        '''
        if new_head:
            self.previous_ai_snake_head = head
        else:
            delta_head_0 = head[0] - self.previous_ai_snake_head[0]
            delta_head_1 = head[1] - self.previous_ai_snake_head[1]
            new_head = (head[0] + delta_head_0, head[1] + delta_head_1)
        
        # Check for Boundaries and Self Collisions
        if new_head is not None and (
            new_head[0] < 0
            or new_head[0] >= 600
            or new_head[1] < 0
            or new_head[1] >= 600
            or new_head in self.ai_snake[1:]
        ):
            return False

        self.ai_snake.insert(0, new_head)

        # Check collision with food
        food_coords = self.canvas.coords(self.food)
        if int(head[0]) == food_coords[0] and int(head[1]) == food_coords[1]:
            self.canvas.delete("food")
            self.food = self.create_food()
            self.ai_scoreboard += 1 # Update the score
            self.set_title()  # Update title with the new AI score
        else:
            # Remove the tail to maintain length
            tail = self.ai_snake.pop()
            self.canvas.delete(tail)

        return True

    def end_game(self):
        self.snake_moving = False   # To stop the snake from moving further
        winner = None

        if self.scoreboard > self.ai_scoreboard:
            winner = "User"
        elif self.scoreboard < self.ai_scoreboard:
            winner = "AI"
        elif self.scoreboard == self.ai_scoreboard:
            # Check if any snake collided with boundaries
            head_user = self.snake[0]
            head_ai = self.ai_snake[0]

            if (
                head_user[0] < 0
                or head_user[0] >= 600
                or head_user[1] < 0
                or head_user[1] >= 600
            ):
                winner = "AI"
            elif (
                head_ai[0] < 0
                or head_ai[0] >= 600
                or head_ai[1] < 0
                or head_ai[1] >= 600
            ):
                winner = "User"
            
            # Check collision with obstacles
            for obstacle_coords in self.obstacles:
                if (
                    head_user[0] == obstacle_coords[0]
                    or head_user[1] == obstacle_coords[1]
                ):
                    winner = "AI"
                    break
                elif (
                    head_ai[0] == obstacle_coords[0]
                    or head_ai[1] == obstacle_coords[1]
                ):
                    winner = "User"
                    break
            
        # Declare the winner on the canvas
        if winner:
            self.canvas.create_text(300, 300, text=f"Game Over!!! {winner} Wins!", 
                                    fill="#3d0217", font=("Calibri", 28))
        else:
            self.canvas.create_text(300, 300, text="Game Over!!! It's a Draw!",
                                    fill="#3d0217", font=("Calibri", 28))

    def update(self):
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        if self.snake_moving and elapsed_time < self.game_duration:
            # Move the user snake
            if not self.move_snake(self.snake, self.direction): # If it hits a boundary or obstacle, end the game
                self.end_game()
                return

            # Move the AI snake
            if not self.move_ai_snake(self.ai_snake):
                self.end_game()
                return

            head = self.snake[0]
            self.canvas.delete("snake") #deletes the previous snake
            for segment in self.snake:
                if segment is not None:
                    self.canvas.create_rectangle(segment[0],segment[1],segment[0] + self.snake_size,segment[1] + self.snake_size,
                        fill="green", tags="snake")

            head_ai = self.ai_snake[0]
            self.canvas.delete("ai_snake")
            for segment in self.ai_snake:
                if segment is not None:
                    self.canvas.create_rectangle(segment[0],segment[1],segment[0] + self.ai_snake_size,segment[1] + self.ai_snake_size,
                        fill="yellow",tags="ai_snake")

            # Check collision with food
            food_coords = self.canvas.coords(self.food)
            if int(head[0]) == food_coords[0] and int(head[1]) == food_coords[1]:
                self.snake.append(self.snake[-1])
                self.canvas.delete("food")
                self.food = self.create_food()
                self.scoreboard += 1
                self.set_title()  # Update title with the new score

            # Check collision with obstacles
            for obstacle_coords in self.obstacles:
                if head[0] == obstacle_coords[0] and head[1] == obstacle_coords[1]:
                    self.end_game()
                    return

            self.master.after(200, self.update)
        else:
            self.end_game()


    def change_direction(self, event):
        if event.keysym == "Right" and not self.direction == "Left":
            self.direction = "Right"
        elif event.keysym == "Left" and not self.direction == "Right":
            self.direction = "Left"
        elif event.keysym == "Up" and not self.direction == "Down":
            self.direction = "Up"
        elif event.keysym == "Down" and not self.direction == "Up":
            self.direction = "Down"

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
