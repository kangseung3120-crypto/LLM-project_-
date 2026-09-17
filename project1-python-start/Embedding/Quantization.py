from ollama import Client
import time


client = Client(host="http://localhost:11434")


models = [
    "hf.co/Qwen/Qwen3-8B-GGUF:Q4_K_M",
    "hf.co/Qwen/Qwen3-8B-GGUF:Q6_K",
]


questions = [
    "인공지능과 머신러닝의 차이를 초보자도 이해하기 쉽게 설명해줘.",
    
    "과적합(overfitting)이 무엇인지 설명하고, 과적합을 줄이는 방법 3가지를 알려줘.",
    
    "Transformer에서 Self-Attention이 어떤 역할을 하는지 초보자도 이해하기 쉽게 설명해줘.",
    
    "RAG가 무엇인지 설명하고, 일반적인 LLM의 답변과 비교했을 때 어떤 장점이 있는지 설명해줘.",
    
    "양자화(Quantization)가 LLM의 메모리 사용량과 모델 성능에 어떤 영향을 줄 수 있는지 설명해줘.",
]


for model in models:

    print("=" * 80)
    print(f"모델: {model}")

    for i, question in enumerate(questions, start=1):

        print("-" * 80)
        print(f"Q{i}. {question}")

        start = time.perf_counter()

        response = client.generate(
            model=model,
            prompt=question,
            options={
                "temperature": 0,
            },
        )

        elapsed = time.perf_counter() - start

        print(f"응답 시간: {elapsed:.2f}초")
        print()
        print(response.response)
        print()