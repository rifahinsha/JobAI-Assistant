# def get_jd():

#     print("\nPaste Job Description")
#     print("Type END on a new line when finished:\n")


#     jd_lines = []


#     while True:

#         line = input()

#         if line.strip() == "END":
#             break

#         jd_lines.append(line)


#     return "\n".join(jd_lines)



# def get_answer():

#     while True:

#         answer = input(
#             "\nYour Answer (type exit to stop): "
#         ).strip()


#         if answer.lower() == "exit":
#             print("Interview stopped")
#             exit()


#         if answer:
#             return answer


#         print("Please enter an answer")