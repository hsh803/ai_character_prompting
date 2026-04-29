import json
from datetime import datetime
import os
from google import genai

# 0. Gemini ai setup
client = genai.Client(api_key="YOUR_GEMINI_API_KEY")
model ='gemini-1.5-flash'

# 1. Load a structured XML prompt
def load_system_prompt():
    with open("system_prompt.txt", "r", encoding="utf-8") as f:
        return f.read()

# 2. Database Functions (Mock DB using JSON)
def get_user_data(user_id):
    # We call json file as toy example
    with open("user_database.json", "r", encoding="utf-8") as f:
        return json.load(f).get(user_id)

def save_user_data(user_id, updated_data):
    with open("user_database.json", "r", encoding="utf-8") as f:
        all_data = json.load(f)
    all_data[user_id] = updated_data
    with open("user_database.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

# 3. Summarizer LLM Logic (Conceptual Theory)
# Implementation of Asynchronous Processing for long-term memory
def summarize_interaction(user_input, ai_message, old_context):
    """
    Conceptual hook for updating shared_context.
    In production, this runs as a background task using Gemini's summarization capability.
    """
    summary_prompt = f"""
    아래 대화에서 캐릭터 '서준서'와 사용자의 관계 발전에 중요한 정보만 한 문장으로 요약해줘.
    기존 맥락: {old_context}
    최신 대화: 사용자 - {user_input} / 서준서 - {ai_message}
    """

    try:
        # Actual API Call Example:
        # response = model.generate_content(summary_prompt)
        # return f"{old_context} | {response.text.strip()}"

        # Toy Example
        return f"{old_context} | 사용자가 스콘을 주문."
    except Exception:
        return old_context

# 4. Memory Update
BEVERAGE_MENU = ["아메리카노", "에스프레소", "카페라떼", "바닐라라떼", "카푸치노"]
NEGATION_WORDS = ["싫어", "안 마셔", "못 마셔", "별로", "제외", "빼고"]

def update_memory(user_id, user_input, ai_message, user_data):
    # Update Metadata
    user_data['visit_count'] += 1
    user_data['mood_score'] += 0.5
    user_data['last_visit'] = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Update Shared Context
    user_data['shared_context'] = summarize_interaction(
        user_input, ai_message, user_data['shared_context'])

    # Information Extraction: Update user preferences
    found_beverages = [drink for drink in BEVERAGE_MENU if drink in user_input]

    if found_beverages:
        # Decide like or dislike
        is_negative = any(neg in user_input for neg in NEGATION_WORDS)
        pref_type = "비선호" if is_negative else "선호"

        # Gerenerate preference
        new_prefs = [f"{drink} {pref_type}" for drink in found_beverages]
        new_pref_str = ", ".join(new_prefs)

        # Update preference list (Simplified logic)
        if user_data['user_preferences']:
            user_data['user_preferences'] += f", {new_pref_str}"
        else:
            user_data['user_preferences'] = new_pref_str

    # Save
    save_user_data(user_id, user_data)

# 4. Context Engineering Pipeline
def generate_junseo_response(user_id, user_input):
    # Fetch data from DB
    user_data = get_user_data(user_id)

    # Inject Variables into the prompt
    prompt = load_system_prompt()
    prompt = prompt.replace("{{level}}", str(user_data['level']))
    prompt = prompt.replace("{{mood_score}}", str(user_data['mood_score']))
    prompt = prompt.replace("{{visit_count}}", str(user_data['visit_count']))
    prompt = prompt.replace("{{last_visit}}", user_data['last_visit'])
    prompt = prompt.replace("{{user_tastes}}", user_data['user_preferences'])
    prompt = prompt.replace("{{context_summary}}", user_data['shared_context'])

    # print(prompt)

    # Gemini API Call (Uncomment to use)
    """
    response = client.models.generate_content(
      model=model,
      contents=f"System: {prompt}\nUser: {user_input}")
    ai_message = response.text
    """

    # Toy example: response based on your Level 1
    ai_message = "(계산을 하며) 따뜻한 아메리카노랑 스콘 준비해 드리겠습니다."

    # Finalize Update
    update_memory(user_id, user_input, ai_message, user_data)

    return ai_message

# --- RUN TOY EXAMPLE ---
if __name__ == "__main__":
    # Simulate Chat
    user_msg = "따뜻한 아메리카노 한 잔이랑 스콘 하나 주세요."
    print(f"\nUSER: {user_msg}")

    ai_reply = generate_junseo_response("user_1", user_msg)
    print(f"서준서: {ai_reply}")
