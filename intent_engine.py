def generate_action_plan(intent, user_text):
    """
    Converts detected intent into a simple, clear action plan.
    """

    if intent == "Learning":
        return """
📘 ACTION PLAN:
1. Pick ONE topic you want to learn today.
2. Spend 30 minutes understanding basics.
3. Write 3 questions you still don’t understand.
4. Revise tomorrow.
"""

    elif intent == "Career":
        return """
💼 ACTION PLAN:
1. Identify one role you want.
2. List required skills.
3. Start learning ONE skill today.
4. Apply to 2 jobs this week.
"""

    elif intent == "Stress":
        return """
🧘 ACTION PLAN:
1. Pause and take 5 deep breaths.
2. Write down what’s stressing you.
3. Do ONE small task only.
4. Rest guilt-free.
"""

    elif intent == "SelfImprovement":
        return """
🚀 ACTION PLAN:
1. Pick one habit to improve.
2. Start very small.
3. Track daily progress.
4. Reflect weekly.
"""

    elif intent == "Loneliness":
        return """
💬 ACTION PLAN:
1. Message one trusted person.
2. Spend time doing something you enjoy.
3. Avoid self-blame.
4. Reach out again tomorrow.
"""

    else:
        return "⚠️ No action plan available."