from ..ai_models.model_selector import ModelSelector
from ..utils import brave_search, simulation_generator, web_scraper

class ScienceTeacherAgent:
    def __init__(self, model_name: str = "claude"):
        self.model = ModelSelector.get_model(model_name)

    async def generate_science_question(self, topic: str, difficulty: str):
        prompt = f"""Generate a {difficulty} science question about {topic}. Include:
        1. A clear, concise question that tests understanding of scientific concepts
        2. Multiple choice answers (if applicable), including the correct answer and plausible distractors
        3. The correct answer with a detailed explanation
        4. Common misconceptions related to the question and why they're incorrect
        5. The underlying scientific principles or theories involved
        6. Real-world applications or examples related to the question
        7. A brief historical context or recent developments in this area of science
        8. Suggestions for further exploration or related topics
        9. A diagram or illustration, if relevant to the question
        10. Ideas for a hands-on experiment or observation related to the question
        Ensure the question is challenging but appropriate for the specified difficulty level, and promotes scientific thinking and curiosity."""
        response = await self.model.generate_response(prompt)
        if not response or "I don't have enough information" in response:
            additional_info = await brave_search.search_missing_info(topic)
            prompt += f"\n\nAdditional context: {additional_info}"
            response = await self.model.generate_response(prompt)
        return response

    async def explain_concept(self, concept: str):
        prompt = f"""Explain the scientific concept of {concept} in simple terms. Your explanation should include:
        1. A clear, concise definition of the concept
        2. The fundamental principles or laws underlying the concept
        3. Historical context: who discovered or developed this concept and when
        4. Real-world applications and examples
        5. How this concept relates to other scientific ideas or theories
        6. Common misconceptions about the concept and clarifications
        7. Recent developments or current research related to this concept
        8. Diagrams, models, or analogies to aid understanding
        9. The importance of this concept in its field of science
        10. Potential future implications or areas of further study
        11. Interesting facts or trivia related to the concept
        12. Suggestions for simple experiments or observations to demonstrate the concept
        Ensure the explanation is accessible to a general audience while maintaining scientific accuracy."""
        return await self.model.generate_response(prompt)

    async def provide_experiment_idea(self, topic: str):
        prompt = f"""Suggest a simple experiment related to {topic} that can be done at home or in a classroom. Include:
        1. A clear objective or hypothesis for the experiment
        2. A comprehensive list of required materials, preferring common household items
        3. Step-by-step instructions for setting up and conducting the experiment
        4. Safety precautions and potential hazards to be aware of
        5. Expected results and how to interpret them
        6. Possible variations or extensions of the experiment
        7. The scientific principles being demonstrated
        8. Common problems that might arise and how to troubleshoot them
        9. Suggestions for data collection and analysis
        10. Ideas for presenting the results (graphs, charts, etc.)
        11. Real-world applications related to the experiment
        12. Follow-up questions or areas for further investigation
        13. Age group suitability and any necessary adult supervision
        Ensure the experiment is engaging, educational, and promotes scientific inquiry and critical thinking."""
        return await self.model.generate_response(prompt)

    async def evaluate_hypothesis(self, hypothesis: str, evidence: str):
        prompt = f"""Evaluate this scientific hypothesis: '{hypothesis}' based on the following evidence: '{evidence}'. In your evaluation:
        1. Assess the clarity and testability of the hypothesis
        2. Analyze the relevance and quality of the provided evidence
        3. Determine if the evidence supports, refutes, or is inconclusive regarding the hypothesis
        4. Identify any potential biases or limitations in the evidence
        5. Suggest additional evidence that would be helpful in evaluating the hypothesis
        6. Discuss alternative hypotheses that could explain the evidence
        7. Evaluate the hypothesis in the context of established scientific theories
        8. Consider potential implications if the hypothesis is supported
        9. Suggest modifications to the hypothesis based on the evidence, if necessary
        10. Propose next steps for further investigation, including potential experiments
        11. Discuss any ethical considerations related to testing this hypothesis
        12. Provide a final assessment of the hypothesis's plausibility
        Ensure your evaluation is thorough, objective, and follows the scientific method."""
        return await self.model.generate_response(prompt)

    async def create_virtual_lab(self, experiment: str, difficulty: str):
        prompt = f"""Design a virtual laboratory experiment about '{experiment}' at a {difficulty} level. Include:
        1. A clear description of the experiment and its objectives
        2. A list of virtual equipment and materials needed
        3. Step-by-step instructions for conducting the experiment
        4. Safety precautions and guidelines (even in a virtual setting)
        5. Interactive elements (e.g., draggable objects, clickable buttons)
        6. Simulations of expected results and potential variations
        7. Data collection and analysis tools
        8. Ideas for visualizing and graphing results
        9. Suggestions for troubleshooting common issues
        10. Extensions or modifications to the experiment for further exploration
        11. Connections to real-world applications of the experiment
        12. Ideas for collaborative features for group work
        Ensure the virtual lab is engaging, educational, and optimized for web-based learning platforms."""
        return await self.model.generate_response(prompt)

    async def generate_simulation(self, phenomenon: str):
        simulation_data = await simulation_generator.generate_simulation(phenomenon)
        return simulation_data

    async def create_science_infographic(self, topic: str):
        prompt = f"""Design an interactive web-based infographic about the scientific topic '{topic}'. Include:
        1. A clear and engaging title
        2. Key facts and figures related to the topic
        3. Visual representations of data or processes
        4. Interactive elements (e.g., hover-over explanations, clickable parts)
        5. A logical flow of information
        6. Suggestions for animations or transitions
        7. Ideas for color schemes and visual design
        8. Short, concise explanatory text
        9. Citations or links to further resources
        10. Ideas for making the infographic shareable on social media
        Ensure the infographic is informative, visually appealing, and optimized for web viewing."""
        infographic_content = await self.model.generate_response(prompt)
        additional_info = await web_scraper.scrape_webpage(f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}")
        return {"content": infographic_content, "additional_info": additional_info}
