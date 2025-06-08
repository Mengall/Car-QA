from langchain.llms.base import LLM
from typing import Optional, List, Mapping, Any

from langchain_core.callbacks import CallbackManagerForLLMRun


class MyLLm(LLM):
    def __init__(self, model, tokenizer):
        super().__init__()
        self.model = model
        self.tokenizer = tokenizer

    @property
    def _llm_type(self) -> str:
        return "Qwen-llm1.5-1.8B"

    def _call(
        self,
        prompt: str,
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs)
        text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return text

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model": "my-simple-llm"}


model = r"D:\PythonWeb\Car_QuestionSystem\models\Qwen-llm1.5-1.8B"
tokenizer = r"D:\PythonWeb\Car_QuestionSystem\models\Qwen-llm1.5-1.8B"
llm = MyLLm(model, tokenizer)
response = llm.invoke("你好，介绍一下北京。")
print(response)
