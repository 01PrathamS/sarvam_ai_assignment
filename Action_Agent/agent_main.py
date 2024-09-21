from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random

app = FastAPI()

# Game state to store the number to be guessed
game_state = {
    "active": False,
    "number_to_guess": None
}

# Function to start a new number guessing game
def start_number_guessing_game():
    game_state["active"] = True
    game_state["number_to_guess"] = random.randint(1, 100)
    return "Game started! Guess a number between 1 and 100."

# Function to handle guesses
def check_guess(user_guess: int):
    if not game_state["active"]:
        return "No active game. Please start a new game."

    number_to_guess = game_state["number_to_guess"]
    
    if user_guess < number_to_guess:
        return "Guess higher!"
    elif user_guess > number_to_guess:
        return "Guess lower!"
    else:
        game_state["active"] = False
        return "You guessed it right! Game over."

# Agent class with multiple action support
class Agent:
    def __init__(self):
        pass

    def perform_action(self, user_query: str, guess: int = None):
        if "start game" in user_query.lower():
            return start_number_guessing_game()
        elif "guess" in user_query.lower() and guess is not None:
            return check_guess(guess)
        else:
            return "Sorry, I don't understand this query. Try 'start game' or 'guess'."

# Request schema
class QueryRequest(BaseModel):
    query: str
    guess: int = None  # Optional guess for number guessing game

agent = Agent()

@app.post("/agent")
async def handle_agent(request: QueryRequest):
    query = request.query
    guess = request.guess

    response = agent.perform_action(query, guess)

    if not response:
        raise HTTPException(status_code=400, detail="Invalid query")
    
    return {"response": response}
