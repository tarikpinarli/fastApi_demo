# logic.py
def generate_recommendation(user_id: str, steps: int, heart_rate: float) -> dict:
    # your existing logic here
    score = steps / 1000
    if heart_rate < 60:
        score += 2
    elif heart_rate < 80:
        score += 1

    recommendation = (
        "You are doing great, keep your routine."
        if score > 8
        else "Try adding a 20-minute walk and earlier bedtime."
    )

    return {"score": score, "recommendation": recommendation}
