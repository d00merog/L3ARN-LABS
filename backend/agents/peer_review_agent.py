from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Annotated
import operator

class PeerReviewState(TypedDict):
    submission: str
    reviewers: List[str]
    feedback: List[str]
    status: str

def submit_work(state):
    return {**state, "status": "submitted"}

def assign_reviewers(state):
    # In a real application, this would involve a more complex assignment logic.
    reviewers = ["user_a", "user_b"]
    return {**state, "reviewers": reviewers, "status": "review_assigned"}

def get_feedback(state):
    # This would involve notifying reviewers and collecting their feedback.
    feedback = ["This is a great start!", "Consider adding more examples."]
    return {**state, "feedback": feedback, "status": "feedback_received"}

def revise_work(state):
    # This would involve the original author revising their work based on the feedback.
    return {**state, "status": "revised"}

def final_approval(state):
    return {**state, "status": "approved"}

workflow = StateGraph(PeerReviewState)

workflow.add_node("submit_work", submit_work)
workflow.add_node("assign_reviewers", assign_reviewers)
workflow.add_node("get_feedback", get_feedback)
workflow.add_node("revise_work", revise_work)
workflow.add_node("final_approval", final_approval)

workflow.set_entry_point("submit_work")
workflow.add_edge("submit_work", "assign_reviewers")
workflow.add_edge("assign_reviewers", "get_feedback")
workflow.add_edge("get_feedback", "revise_work")
workflow.add_edge("revise_work", "final_approval")
workflow.add_edge("final_approval", END)

app = workflow.compile()
