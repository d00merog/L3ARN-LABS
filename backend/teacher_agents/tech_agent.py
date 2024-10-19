from ..ai_models.model_selector import ModelSelector
from ..utils.brave_search import search_missing_info
from ..utils.code_executor import execute_code

class TechTeacherAgent:
    def __init__(self, model_name: str = "claude"):
        self.model = ModelSelector.get_model(model_name)

    async def explain_tech_concept(self, concept: str):
        prompt = f"""Explain the technology concept of {concept} in simple terms. Your explanation should include:
        1. A clear, concise definition of the concept
        2. The fundamental principles or technologies underlying the concept
        3. Historical context: how and when this technology developed
        4. Current real-world applications and examples
        5. How this concept relates to other technologies or IT concepts
        6. Common misconceptions about the concept and clarifications
        7. Recent developments or innovations in this area
        8. Diagrams, flowcharts, or analogies to aid understanding
        9. The importance of this concept in the field of technology
        10. Potential future implications or areas of further development
        11. Any relevant programming languages, frameworks, or tools associated with the concept
        12. Ethical considerations or societal impacts of the technology
        13. Resources for further learning (books, courses, websites)
        Ensure the explanation is accessible to a general audience while maintaining technical accuracy."""
        response = await self.model.generate_response(prompt)
        if not response or "I don't have enough information" in response:
            additional_info = await search_missing_info(concept)
            prompt += f"\n\nAdditional context: {additional_info}"
            response = await self.model.generate_response(prompt)
        return response

    async def generate_coding_challenge(self, language: str, difficulty: str):
        prompt = f"""Generate a {difficulty} coding challenge in {language}. Include:
        1. A clear problem statement with specific requirements
        2. Input/output examples to illustrate expected behavior
        3. Any constraints or edge cases to consider
        4. A comprehensive solution with explanations for each step
        5. Alternative solutions or approaches, if applicable
        6. Time and space complexity analysis of the solution(s)
        7. Common pitfalls or mistakes to avoid
        8. Best practices or coding standards relevant to the challenge
        9. Suggestions for optimizing the code
        10. Ideas for extending or modifying the challenge for additional practice
        11. Relevant built-in functions or libraries that could be useful
        12. Unit tests to verify the solution
        13. Real-world applications or scenarios where this problem might be encountered
        Ensure the challenge is appropriate for the specified difficulty level and promotes good coding practices and problem-solving skills."""
        return await self.model.generate_response(prompt)

    async def provide_tech_trend_insight(self, trend: str):
        prompt = f"""Provide comprehensive insights on the current technology trend: {trend}. Include:
        1. A clear definition and explanation of the trend
        2. Historical context: how this trend emerged and evolved
        3. Current state of the technology and its adoption rate
        4. Key players or companies driving this trend
        5. Real-world applications and use cases
        6. Potential impact on various industries and sectors
        7. Challenges and limitations associated with the trend
        8. Future projections and potential developments
        9. How it relates to or influences other technology trends
        10. Ethical considerations or societal impacts
        11. Skills or knowledge required to work with this technology
        12. Investment and market opportunities related to the trend
        13. Relevant standards, regulations, or policies
        14. Comparisons with similar or competing technologies
        15. Resources for further learning or staying updated on the trend
        Ensure the insights are well-researched, balanced, and provide a comprehensive overview of the trend's significance in the tech landscape."""
        return await self.model.generate_response(prompt)

    async def review_code(self, code: str, language: str):
        prompt = f"""Review the following {language} code:

        {code}

        Provide a comprehensive code review, including:
        1. Overall code structure and organization
        2. Adherence to {language} best practices and coding standards
        3. Proper use of language-specific features and idioms
        4. Naming conventions for variables, functions, and classes
        5. Code readability and maintainability
        6. Potential bugs or edge cases
        7. Error handling and input validation
        8. Performance considerations and optimization opportunities
        9. Security vulnerabilities or risks
        10. Proper use of comments and documentation
        11. Suggestions for improving code modularity and reusability
        12. Identification of any redundant or unnecessary code
        13. Proper use of version control (if applicable)
        14. Compliance with relevant coding style guides
        15. Suggestions for unit tests or test cases
        16. Scalability considerations
        Provide specific examples and explanations for each point of feedback, and suggest improvements where applicable. Ensure the review is constructive and aims to improve the overall quality of the code."""
        return await self.model.generate_response(prompt)

    async def create_interactive_tutorial(self, topic: str, language: str):
        prompt = f"""Design an interactive web-based coding tutorial about '{topic}' in {language}. Include:
        1. A clear introduction to the topic and learning objectives
        2. Step-by-step instructions with code snippets
        3. Interactive code editor for users to practice
        4. Live output display for code execution
        5. Explanations of key concepts and best practices
        6. Common pitfalls and how to avoid them
        7. Suggestions for error handling and debugging tips
        8. Progressive challenges to reinforce learning
        9. Ideas for projects or extensions to apply the learned concepts
        10. Links to additional resources or documentation
        11. A system for saving and sharing user progress
        12. Adaptations for different skill levels (beginner, intermediate, advanced)
        Ensure the tutorial is engaging, hands-on, and optimized for web-based learning platforms."""
        return await self.model.generate_response(prompt)

    async def execute_user_code(self, code: str, language: str):
        result = await execute_code(code, language)
        return result

    async def generate_tech_roadmap(self, technology: str, timeframe: str):
        prompt = f"""Create a technology roadmap for '{technology}' over the next {timeframe}. Include:
        1. Current state of the technology
        2. Predicted major milestones and breakthroughs
        3. Potential challenges and obstacles
        4. Key players and companies driving innovation
        5. Emerging trends and their potential impact
        6. Suggestions for visual representation (timeline, flowchart, etc.)
        7. Ideas for interactive elements (e.g., clickable nodes for more info)
        8. Relevant skills and knowledge areas for professionals
        9. Potential societal and ethical implications
        10. Links to relevant research papers or industry reports
        Ensure the roadmap is informative, visually appealing, and suitable for web presentation."""
        return await self.model.generate_response(prompt)
