
class ConversationMemory: #class hold chat history
    def __init__(self, max_turns: int = 20):
        self.history: list[dict] = []
        self.max_turns = max_turns # number of pairs to keep

    def add_user(self, text: str): # when user sends msg 
        self.history.append({"role": "user", "content": text})
        self._trim() # keep only below the limit

    def add_assistant(self, text: str): #bot reply
        self.history.append({"role": "assistant", "content": text})

    def get_history(self) -> list[dict]: #list that gets sent to LLM
        """Returns the full message list to send to the API."""
        return self.history

    def clear(self): # to reset the list
        """Wipe history — useful when user starts a new session."""
        self.history = []

    def _trim(self):
        # only keep last max_turns * 2 messages (user + assistant)
        max_messages = self.max_turns * 2
        if len(self.history) > max_messages:
            self.history = self.history[-max_messages:]

    def summary(self) -> str:
        #just counts the number of messages in memory
        return f"{len(self.history)} messages in memory"