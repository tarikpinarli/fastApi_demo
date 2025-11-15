from datetime import datetime, timezone

def generate_recommendation(user_id: str, steps: int, heart_rate: float) -> dict:
    # 👉 This is just a MOCK – your colleague will replace the inside later

    # Simple scoring logic
    score = steps / 1000
    if heart_rate < 60:
        score += 2
    elif heart_rate < 80:
        score += 1

    if score > 8:
        recommendation = "Great recovery day. 2 x 15 min sauna at 80°C."
        intensity = "moderate"
        suggested_duration = 15
        temperature = 80
    else:
        recommendation = "Keep it light. 1 x 10 min sauna at 70°C."
        intensity = "light"
        suggested_duration = 10
        temperature = 70

    return {
        "user_id": user_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "temperature": temperature,
        "suggested_duration": suggested_duration,
        "intensity": intensity,
        "notes": "Mock recommendation – replace with real model later.",
        "raw_health_data": {
            "steps": steps,
            "heart_rate": heart_rate,
        },
        "heart_rate": heart_rate,
        "recommendation": recommendation,
        "score": score,
        "steps": steps,
    }
