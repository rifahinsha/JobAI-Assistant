from .config import is_job_related, is_small_talk, OFF_TOPIC_REPLY
from .memory import ConversationMemory
from .llm_api import call_llm


class JobChatbot:
    def __init__(self):
        self.memory = ConversationMemory(max_turns=20)

    def chat(self, user_message: str) -> str:

        #user_message
            #[keyword filter] --> off-topic --> return redirect message

        #on-topic

        #[add to memory] 
             
        #[call Claude API with full history + system prompt]
        
        #[save reply to memory]
              
        #return reply

        user_message = user_message.strip()

        if not user_message:
            return "Please type a question about your job search!"
        
        # Key Filter
        if not is_job_related(user_message) and not is_small_talk(user_message):
            return OFF_TOPIC_REPLY

        self.memory.add_user(user_message)

        try: #exception to catches error
            reply = call_llm(self.memory.get_history())
        except Exception as e:
            self.memory.history.pop()
            return f"Sorry, something went wrong: {str(e)}"

        self.memory.add_assistant(reply)
        return reply

    def reset(self):
        self.memory.clear()

    def history_summary(self) -> str:
        return self.memory.summary()