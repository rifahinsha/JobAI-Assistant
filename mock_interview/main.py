# from question_generator import generate_questions
# from evaluator import evaluate_answer
# from input_handler import get_jd, get_answer


# print("AI MOCK INTERVIEW\n")


# role = input("Enter Role: ")
# experience = input("Enter Experience Level: ")
# jd = get_jd()
# print("\n Generating questions...\n")


# questions_text = generate_questions(role,experience,jd)



# questions = []
# for line in questions_text.split("\n"):
#     line = line.strip()
#     if line.startswith(tuple(f"{i}." for i in range(1,20))):
#         questions.append( line.split(".",1)[1].strip())



# for i,q in enumerate(questions,1):

#     print("\n====================")
#     print(f"Question {i}:")
#     print(q)
#     print("====================")


#     answer = get_answer()


#     print("\nEvaluating...\n")


#     result = evaluate_answer(q,answer)


#     print("Result:")
#     print(result)


#     input("\nPress ENTER for next question...")



# print("\nInterview Completed!")
