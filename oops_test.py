
from typing import Protocol,ClassVar
from dataclasses import dataclass

@dataclass
class LLMResponse:
    text: str
    input_tokens: int
    output_tokens: int
    model: str

    PRICE_TABLE: ClassVar[dict[str, float]] = {
        "gemini-2.5-flash": 0.00025,
        "gpt-3.5-turbo": 0.00050,
    }

    @property
    def cost(self) -> float:
        price = self.PRICE_TABLE[self.model]

        return price * (
            self.input_tokens + self.output_tokens
        )

class LLMClient(Protocol):
    def generate(self, prompt: str) -> LLMResponse:
        pass

class Gemini:
    def __init__(self, api_key, model, input_tokens, output_tokens):
        self.model = model
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens

    def __repr__(self) -> str:
        return f"Gemini(model={self.model!r})"

    @classmethod
    def from_env(cls):
        api_key="abc"
        model="gemini-2.5-flash"
        input_tokens=1000
        output_tokens=100
        return cls(api_key, model, input_tokens, output_tokens)

    def generate(self, prompt)-> LLMResponse:
        return LLMResponse(text=f"this is gemini output {prompt}", input_tokens=self.input_tokens, output_tokens=self.output_tokens, model=self.model)

def use_llm(llm: LLMClient, prompt: str)-> LLMResponse:
    return llm.generate(prompt)

# print(use_llm(Gemini(api_key="abc", model="gemini-2.5-flash", input_tokens=1000, output_tokens=100), "Hello, how are you"))
# print(use_llm(Gemini.from_env(), "Hello, how are you"))
test = Gemini(api_key="abc", model="gemini-2.5-flash", input_tokens=1000, output_tokens=100)
print(test)    