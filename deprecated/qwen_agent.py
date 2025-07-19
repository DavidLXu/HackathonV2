import dashscope

# Set your DashScope API Key here
dashscope.api_key = 'sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

def ask_qwen(prompt, history=[]):
    response = dashscope.Generation.call(
        model='qwen-plus',  # or qwen-turbo / qwen-max
        messages=[
            {"role": "system", "content": "You are a helpful chatbot."}
        ] + history + [{"role": "user", "content": prompt}],
        result_format='message'
    )
    if response.status_code == 200:
        reply = response.output.choices[0].message['content']
        return reply
    else:
        return f"[Error {response.status_code}]: {response.message}"

# Example usage:
history = []
while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    history.append({"role": "user", "content": user_input})
    reply = ask_qwen(user_input, history)
    history.append({"role": "assistant", "content": reply})
    print("Bot:", reply)