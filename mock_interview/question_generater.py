# from groq import Groq
# from config import GROQ_API_KEY


# client = Groq(api_key=GROQ_API_KEY)

# MODEL = "llama-3.1-8b-instant"


# def generate_questions(role, experience, jd):

#     prompt = f"""
# You are an expert interviewer.

# Generate interview questions for a {role} ({experience} level).

# Job Description:
# {jd}

# Rules:
# - Cover the complete job description
# - Include basic and JD-specific questions
# - Include skills, tools, technologies, and project questions
# - Start from beginner level and increase difficulty
# - No coding problems
# - Generate at least 15 questions

# Output format:
# 1. Question
# 2. Question
# 3. Question
# ...
# """

#     response = client.chat.completions.create(
#         model=MODEL,
#         messages=[
#             {
#                 "role": "user",
#                 "content": prompt
#             }
#         ],
#         temperature=0.5
#     )

#     return response.choices[0].message.content.strip()