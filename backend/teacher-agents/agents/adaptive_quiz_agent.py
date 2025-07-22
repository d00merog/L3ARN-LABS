from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator

class AgentState(TypedDict):
    question: str
    answer: str
    history: List[str]
    feedback: str
    difficulty: str

def start_quiz(state):
    return {"question": "What is the capital of France?", "difficulty": "easy"}

def present_question(state):
    # Log question for debugging purposes
    return state

def get_answer(state):
    answer = input("Your answer: ")
    return {**state, "answer": answer}

def evaluate_answer(state):
    if state['answer'].lower() == "paris":
        feedback = "Correct!"
        difficulty = "medium"
    else:
        feedback = "Incorrect. The correct answer is Paris."
        difficulty = "easy"
    return {**state, "feedback": feedback, "difficulty": difficulty}

def adapt_difficulty(state):
    # In a real application, this would involve more complex logic
    # to select the next question based on the user's performance.
    if state['difficulty'] == "medium":
        next_question = "What is 2 + 2?"
    else:
        next_question = "What is 1 + 1?"
    return {**state, "question": next_question}

workflow = StateGraph(AgentState)

workflow.add_node("start", start_quiz)
workflow.add_node("present_question", present_question)
workflow.add_node("get_answer", get_answer)
workflow.add_node("evaluate_answer", evaluate_answer)
workflow.add_node("adapt_difficulty", adapt_difficulty)

workflow.set_entry_point("start")
workflow.add_edge("start", "present_question")
workflow.add_edge("present_question", "get_answer")
workflow.add_edge("get_answer", "evaluate_answer")
workflow.add_edge("evaluate_answer", "adapt_difficulty")
workflow.add_edge("adapt_difficulty", "present_question")

app = workflow.compile()
