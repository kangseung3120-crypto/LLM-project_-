import json
from datetime import datetime, timezone

from ollama import Client

MODEL = "qwen2.5:7b"

ARTICLE = """[[속보]퇴근길 주식거래 첫날인데…대형 증권사 잇단 전산장애]
한국거래소(KRX)가 애프터마켓을 처음 개장하는 14일 국내 대형 증권사에서 잇따라 전산장애가 발생했다. KRX와 대체거래소 넥스트레이드(NXT) 중 투자자에게 유리한 시장으로 주문을 보내는 최선주문집행(SOR) 시스템에서 문제가 발생하면서 일부 투자자들이 주문 체결 조회와 취소 등에 불편을 겪었다.

14일 금융투자업계에 따르면 이날 오전 미래에셋증권 홈트레이딩시스템(HTS)과 모바일트레이딩시스템(MTS)에서 프리마켓(오전 8시~8시50분) 매수·매도 주문의 체결 조회가 일부 지연됐다. 프리마켓 종료 이후 정규장 거래는 정상적으로 이뤄지고 있지만, SOR 시스템의 가동은 제한되고 있다.

미래에셋증권은 "SOR 시스템 점검으로 SOR 주문 시 정규장은 KRX, 애프터마켓은 NXT(오후 3시30분~4시) 또는 KRX(오후 4~8시)로 주문이 전송된다"고 안내했다.

삼성증권에서도 프리마켓 거래 과정에서 장애가 발생했다. 삼성증권은 "SOR 장애로 취소주문 처리가 정상적으로 되지 않아 KRX 시장으로 전환 처리했다"고 공지했다.

이번 전산 장애는 애프터마켓 개장에 따른 증권사들의 시스템 변경 과정에서 발생했다. 업계 관계자는 "애프터마켓 개설에 맞춰 증권사들이 SOR 시스템을 변경했고, 이를 처음 적용하는 과정에서 오류가 발생한 것으로 보인다"고 말했다. 이번 전산장애는 KRX 시스템과는 무관한 것으로 파악됐다.

이날부터 KRX는 기존 시간외 단일가 매매를 폐지하고 오후 4~8시 실시간 거래가 가능한 애프터마켓을 운영한다. NXT도 오후 8시까지 애프터마켓을 운영하고 있다."""

SYSTEM_PROMPT = (
    "당신은 뉴스 요약을 도와주는 어시스턴트입니다. "
    "사용자가 제공한 기사 원문만 근거로 핵심 내용을 간결하게 요약하세요. "
    "기사에 없는 내용은 절대 추측해서 만들어내지 마세요."
)


USER_PROMPT = "다음 기사를 요약해주세요.\n\n" + ARTICLE


client = Client(host="http://127.0.0.1:11434", timeout=180)
print("Ollama에 질문을 보냈습니다. 답변을 기다려 주세요.")

response = client.chat(
    model=MODEL,
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},  
        {"role": "user", "content": USER_PROMPT},       
    ],
    stream=False,
    options={"temperature": 0},  
)

answer = response.message.content
print("\n[Ollama 답변]")
print(answer)


record = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "model": MODEL,
    "article": ARTICLE,
    "answer": answer,
}

line = json.dumps(record, ensure_ascii=False)


f = open("results.jsonl", "a", encoding="utf-8")
f.write(line + "\n")
f.close()

print("\n[저장] results.jsonl 에 결과 1건 추가됨")