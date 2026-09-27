class llmclient:
    def __init__(self,model:str):
        self.model = self.model

    def describe(self):
        return f"your model is:{self.model}"
check = llmclient("test")
print(check.describe())