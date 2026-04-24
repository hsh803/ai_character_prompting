import json
from datetime import datetime

# 1. Load a structured XML prompt
def load_system_prompt():
    with open("system_prompt.txt", "r", encoding="utf-8") as f:
        return f.read()

# 2. Mock Database Functions
def get_user_data(user_id):
    # In a real app, this would be a SQL or Vector DB call
    with open("user_database.json", "r", encoding="utf-8") as f:
        return json.load(f).get(user_id)

def save_user_data(user_id, updated_data):
    with open("user_database.json", "r", encoding="utf-8") as f:
        all_data = json.load(f)
    all_data[user_id] = updated_data
    with open("user_database.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

# 3. Simple Logic example for Memory Update
BEVERAGE_MENU = ["아메리카노", "에스프레소", "카페라떼", "바닐라라떼", "카푸치노"]
NEGATION_WORDS = ["싫어", "안 마셔", "못 마셔", "별로", "제외", "빼고"]

def update_memory(user_id, user_input, user_data):
    user_data['visit_count'] += 1
    user_data['mood_score'] += 0.1
    user_data['last_visit'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    # 1. Search for any item from BEVERAGE_MENU that exists in user_input
    found_beverages = [drink for drink in BEVERAGE_MENU if drink in user_input]

    if found_beverages:
        # 2. Decide like or dislike
        is_negative = any(neg in user_input for neg in NEGATION_WORDS)
        pref_type = "비선호" if is_negative else "선호"

        # 3. Gerenerate preference
        new_prefs = [f"{drink} {pref_type}" for drink in found_beverages]
        new_pref_str = ", ".join(new_prefs)

        # 4. Update preference list (Simplified logic)
        if user_data['user_preferences']:
            user_data['user_preferences'] += f", {new_pref_str}"
        else:
            user_data['user_preferences'] = new_pref_str

    # Save
    save_user_data(user_id, user_data)

# 4. Context Engineering Pipeline
def generate_junseo_response(user_id, user_input):
    # A. Fetch data from DB
    user_data = get_user_data(user_id)

    # B. Inject Variables into the prompt
    prompt = load_system_prompt()
    prompt = prompt.replace("{{level}}", str(user_data['level']))
    prompt = prompt.replace("{{mood_score}}", str(user_data['mood_score']))
    prompt = prompt.replace("{{visit_count}}", str(user_data['visit_count']))
    prompt = prompt.replace("{{last_visit}}", user_data['last_visit'])
    prompt = prompt.replace("{{user_tastes}}", user_data['user_preferences'])
    prompt = prompt.replace("{{context_summary}}", user_data['shared_context'])

    # print(prompt)

    # C. Call LLM API(Uncomment the code below once you have a real API Key)
    """
    response = client.chat.completions.create(
        model="chat_model_id",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7
    )
    ai_message = response.choices[0].message.content
    """

    # Toy example: response based on your Level 1
    ai_message = "(계산을 하며) 따뜻한 아메리카노 한 잔 준비해 드리겠습니다."

    # D. Memory Update Logic (The "Saving" part)
    update_memory(user_id, user_input, user_data)

    return ai_message

# --- RUN TOY EXAMPLE ---
if __name__ == "__main__":
    # Simulate Chat
    user_msg = "따뜻한 아메리카노 한 잔 주세요."
    print(f"\nUSER: {user_msg}")

    ai_reply = generate_junseo_response("user_1", user_msg)
    print(f"서준서: {ai_reply}")