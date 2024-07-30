from flask import Flask, render_template, request, jsonify
import re
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

# In-memory storage for chat data
chats = {}

def parse_chat(file_content):
    messages = []
    participants = set()
    message_pattern = re.compile(r'(\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}\s?[ap]m) - (.*?): (.*)', re.IGNORECASE)
    system_message_pattern = re.compile(r'(\d{2}/\d{2}/\d{4}, \d{1,2}\s?[ap]m) - (.*)')
    for line in file_content.split('\n'):
        match = message_pattern.match(line)
        if match:
            timestamp, sender, message = match.groups()
            participants.add(sender)
            messages.append({'timestamp': timestamp, 'sender': sender, 'message': message})
        else:
            match = system_message_pattern.match(line)
            if match:
                timestamp, message = match.groups()
                messages.append({'timestamp': timestamp, 'sender': 'System', 'message': message})
    return messages, sorted(participants)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            content = file.read().decode('utf-8')
            messages, participants = parse_chat(content)
            chat_id = str(uuid.uuid4())
            chats[chat_id] = {
                'messages': messages,
                'participants': participants,
                'primary_person': None,
                'search_query': ''
            }
            return render_template('index.html', chat_id=chat_id, messages=messages, participants=participants)
    return render_template('index.html')

@app.route('/update', methods=['POST'])
def update():
    chat_id = request.form.get('chat_id')
    primary_person = request.form.get('primary_person')
    search_query = request.form.get('search_query', '').strip()

    chat_data = chats.get(chat_id)
    if not chat_data:
        return jsonify(messages=[], primary_person=primary_person)

    chat_data['primary_person'] = primary_person
    chat_data['search_query'] = search_query

    messages = chat_data['messages']
    if search_query:
        messages = [msg for msg in messages if search_query.lower() in msg['message'].lower()]

    return jsonify(messages=messages, primary_person=primary_person)

if __name__ == '__main__':
    app.run(debug=True)
