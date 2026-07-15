# from groq import Groq
# from config import GROQ_API_KEY


# client = Groq(api_key=GROQ_API_KEY)

# MODEL = "llama-3.1-8b-instant"


# def evaluate_answer(question, answer):

#     prompt = f"""
# You are an interviewer.

# Evaluate ONLY this candidate answer.

# Question:
# {question}

# Candidate Answer:
# {answer}

# Rules:
# - Do not create an answer
# - Do not assume anything
# - Judge only given response

# Output:
# Score: X/10
# Feedback: 1-2 lines
# """


#     response = client.chat.completions.create(
#         model=MODEL,
#         messages=[
#             {
#                 "role": "user",
#                 "content": prompt
#             }
#         ],
#         temperature=0
#     )


#     return response.choices[0].message.content.strip()