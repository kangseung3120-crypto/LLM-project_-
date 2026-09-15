import json

# results.jsonl 한 줄씩 읽어서 리스트로 만들기
records = []
f = open("results.jsonl", encoding="utf-8")
for line in f:
    records.append(json.loads(line))
f.close()

models = []
for r in records:
    if r["model"] not in models:
        models.append(r["model"])


def average(values):
    """None을 제외하고 평균과 n(사용된 개수)을 함께 반환. 값이 하나도 없으면 (None, 0)."""
    valid = [v for v in values if v is not None]
    if len(valid) == 0:
        return None, 0
    return sum(valid) / len(valid), len(valid)


print("=" * 60)
print("1. 호출 성공률 (run_type = main 기준, 워밍업 제외)")
print("=" * 60)
for model in models:
    main_records = [r for r in records if r["model"] == model and r["run_type"] == "main"]
    total = len(main_records)
    success = len([r for r in main_records if r["status"] == "success"])
    print(f"{model}: {success} / {total} 성공")

print()
print("=" * 60)
print("2. 워밍업 vs 본실험 로딩 지연 비교 (첫 실행 지연 vs 로드된 상태 지연)")
print("=" * 60)
for model in models:
    warmup = [r for r in records if r["model"] == model and r["run_type"] == "warmup"]
    main = [r for r in records if r["model"] == model and r["run_type"] == "main"]

    warmup_load_values = [r["load_duration_seconds"] for r in warmup]
    main_load_values = [r["load_duration_seconds"] for r in main]

    warmup_avg, warmup_n = average(warmup_load_values)
    main_avg, main_n = average(main_load_values)

    print(f"{model}:")
    if warmup_avg is None:
        print("  워밍업(첫 실행) 로딩시간: 측정값 없음")
    else:
        print(f"  워밍업(첫 실행) 로딩시간: {round(warmup_avg, 3)}초 (n={warmup_n})")
    if main_avg is None:
        print("  본실험(로드된 상태) 로딩시간: 측정값 없음")
    else:
        print(f"  본실험(로드된 상태) 로딩시간: {round(main_avg, 3)}초 (n={main_n})")

print()
print("=" * 60)
print("3. 성능 지표 평균 (run_type = main, status = success 인 것만)")
print("=" * 60)
for model in models:
    main_success = [
        r for r in records
        if r["model"] == model and r["run_type"] == "main" and r["status"] == "success"
    ]

    wall_avg, wall_n = average([r["wall_clock_seconds"] for r in main_success])
    tok_avg, tok_n = average([r["tokens_per_second"] for r in main_success])
    vram_avg, vram_n = average([r["vram_used_mib"] for r in main_success])

    print(f"{model}:")
    print(f"  전체 응답 시간 평균: {round(wall_avg, 2) if wall_avg else '없음'}초 (n={wall_n})")
    print(f"  토큰 생성 속도 평균: {round(tok_avg, 1) if tok_avg else '없음'} tok/s (n={tok_n})")
    print(f"  VRAM 사용량 평균: {round(vram_avg, 1) if vram_avg else '없음'} MiB (n={vram_n})")
    print("  ※ 참고: tokens/s는 생성 속도 지표일 뿐, 품질이나 사용자 체감 속도를 나타내지 않음")
    print("  ※ 참고: 첫 토큰 지연(TTFT)은 별도 측정하지 않았으므로 위 응답 시간을 TTFT로 해석하지 말 것")

print()
print("=" * 60)
print("4. run_type별 건수 (워밍업 / 본실험 / 재시도 / 추가실험 분리 확인용)")
print("=" * 60)
run_types = []
for r in records:
    if r["run_type"] not in run_types:
        run_types.append(r["run_type"])

for model in models:
    print(f"{model}:")
    for rt in run_types:
        count = len([r for r in records if r["model"] == model and r["run_type"] == rt])
        print(f"  {rt}: {count}건")

print()
print("=" * 60)
print("5. 실행 조건 (모델별 대표값 1건 - main/success 중 첫 번째)")
print("=" * 60)
for model in models:
    main_success = [
        r for r in records
        if r["model"] == model and r["run_type"] == "main" and r["status"] == "success"
    ]
    if len(main_success) == 0:
        print(f"{model}: 성공한 본실험 기록 없음")
        continue
    sample = main_success[0]
    print(f"{model}:")
    print(f"  digest: {sample.get('model_digest')}")
    print(f"  quantization_level: {sample.get('quantization_level')}")
    print(f"  context_length: {sample.get('context_length')}")
    print(f"  generation_settings: {sample.get('settings')}")
    print(f"  cpu_gpu_load_status: {sample.get('cpu_gpu_load_status')}")