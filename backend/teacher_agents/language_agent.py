from backend.ai_models.model_selector import ModelSelector
from ..utils.brave_search import search_missing_info
from ..utils.text_to_speech import generate_audio
from ..utils.speech_recognition import transcribe_audio

class LanguageTeacher:
    def __init__(self, model_name: str):
        self.model = ModelSelector.get_model(model_name)

    async def generate_lesson(self, topic: str, difficulty: str) -> str:
        prompt = f"Generate a {difficulty} language lesson about {topic}."
        response = await self.model.generate_response(prompt)
        return response

    async def evaluate_response(self, student_response: str, expected_response: str, language: str):
        prompt = f"""Evaluate this student response in {language}: '{student_response}' against the expected response: '{expected_response}'. In your evaluation:
        1. Assess grammatical accuracy, including verb conjugations, tenses, and sentence structure
        2. Evaluate vocabulary usage, including appropriateness and variety
        3. Check for proper use of idiomatic expressions or colloquialisms, if applicable
        4. Analyze pronunciation and intonation (if this is a spoken response)
        5. Assess overall fluency and coherence of the response
        6. Identify any language interference from the student's native language
        7. Provide detailed feedback on strengths and areas for improvement
        8. Suggest specific exercises or resources to address weak areas
        9. Offer alternative phrases or structures to enhance the response
        10. If applicable, comment on the cultural appropriateness of the response
        11. Provide a corrected version of the response
        12. Assign a proficiency level based on common language frameworks (e.g., CEFR)
        Ensure your feedback is constructive, encouraging, and tailored to the student's language learning journey."""
        return await self.model.generate_response(prompt)

    async def generate_translation_exercise(self, text: str, from_lang: str, to_lang: str):
        prompt = f"""Generate a comprehensive translation exercise. Translate the following text from {from_lang} to {to_lang}: '{text}'. Include:
        1. The original text in {from_lang}
        2. A word-for-word literal translation
        3. A polished, natural-sounding translation in {to_lang}
        4. Explanations for key phrases or idioms that don't have direct translations
        5. Notes on any cultural references or context that might affect the translation
        6. Alternative translations for ambiguous words or phrases
        7. Grammatical notes comparing structures in {from_lang} and {to_lang}
        8. Common pitfalls or mistakes to avoid when translating between these languages
        9. A brief discussion on the challenges of this particular translation
        10. Suggestions for further practice or study based on the translation challenges
        Ensure the exercise is informative, highlighting the nuances of both languages and promoting a deeper understanding of translation techniques."""
        return await self.model.generate_response(prompt)

    async def create_interactive_dialogue(self, scenario: str, language: str, difficulty: str):
        prompt = f"""Create an interactive dialogue for a {difficulty} level {language} lesson based on the scenario: '{scenario}'. Include:
        1. A brief introduction setting the scene
        2. A branching dialogue with multiple conversation paths
        3. Key vocabulary and phrases highlighted with translations and usage notes
        4. Grammar points relevant to the dialogue, with explanations
        5. Cultural notes related to the scenario
        6. Pronunciation guides for challenging words or phrases
        7. Suggestions for role-playing the dialogue in an online setting
        8. Ideas for extending the dialogue or creating variations
        9. Comprehension questions to check understanding
        10. Audio recordings of the dialogue (indicate where these should be placed)
        11. Interactive elements like clickable words for definitions or audio playback
        Ensure the dialogue is engaging, realistic, and suitable for web-based language learning platforms."""
        return await self.model.generate_response(prompt)

    async def generate_audio_lesson(self, text: str, language: str):
        audio_file = await generate_audio(text, language)
        return audio_file

    async def transcribe_student_response(self, audio_file: str, language: str):
        transcription = await transcribe_audio(audio_file, language)
        return transcription

    async def create_language_game(self, game_type: str, language: str, difficulty: str):
        prompt = f"""Design a web-based language learning game of type '{game_type}' for {language} at a {difficulty} level. Include:
        1. A clear description of the game mechanics
        2. Learning objectives and target language skills
        3. A list of required vocabulary and grammar points
        4. Suggestions for graphics, animations, and sound effects
        5. Ideas for scoring and progress tracking
        6. Levels or stages of increasing difficulty
        7. Multiplayer or collaborative elements (if applicable)
        8. How to integrate the game with other language learning activities
        9. Adaptations for different devices (desktop, mobile, tablet)
        10. Ideas for expanding or customizing the game
        Ensure the game is engaging, educational, and optimized for online play."""
        return await self.model.generate_response(prompt)
