# class llmclient:
#     def __init__(self,model:str):
#         self.model = self.model

#     def describe(self):
#         return f"your model is:{self.model}"
# check = llmclient("test")
# print(check.describe())

class LLMClient:
    def __init__(self, model: str):
        self.model = model

    # 1. INSTANCE METHOD
    # Needs data from a specific object
    def describe(self) -> str:
        return f"Using model: {self.model}"

    # 2. STATIC METHOD
    # Does not need self or cls
    @staticmethod
    def is_valid_prompt(prompt: str) -> bool:
        return len(prompt.strip()) > 0

    # 3. CLASS METHOD
    # Uses the class to create a new object
    @classmethod
    # def from_default(cls):
    #     return cls("gemini this is static data")

    def get_model_name(cls,model:str):
        return cls(f"your model name is: {model}")


# # -------------------------
# # NORMAL OBJECT CREATION
# # -------------------------

# client1 = LLMClient("claude")

# print(client1.describe())


# # -------------------------
# # STATIC METHOD
# # -------------------------

# result = LLMClient.is_valid_prompt("Hello")

# print(result)


# -------------------------
# CLASS METHOD
# -------------------------

client2 = LLMClient.get_model_name("test")

# print(client2.describe())

print(client2.describe())