#! /usr/bin/env python3
from flask import Flask, request, jsonify
from collections import defaultdict
from flask_socketio import SocketIO, join_room, leave_room, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")


meetings = defaultdict(lambda: {
    "currentQuestionIndex": -1,
    "showResults": False,
    "showScores": False,
    "startTimeUTC": 0,
    "users": {},
    "answers": defaultdict(int),  # number of answers for each answer
})

questions = [
    {
        "question": "What is the probability of getting heads in a coin toss?",
        "answers": [
            "1/2",
            "1/4",
            "1",
            "50",
        ],
        "correctAnswerIndex": 0,
    },
    {
        "question": "What is the probability of rolling a number greater than 2 in a die roll?",
        "answers": [
            "1/2",
            "1/3",
            "2/3",
            "1/4"
        ],
        "correctAnswerIndex": 2,
    },
]

#
# Websocket routes
#
@socketio.on('answer')
def handle_answer(data):
    answer = data['answer']
    userEmail = data['userEmail']
    meetingID = data['meetingID']
    meeting = meetings[meetingID]

    print(f'received answer {answer} from user {userEmail}')
    # can't answer twice
    if meeting['users'][userEmail]['answer'] == -1:
        meeting['answers'][answer] += 1
        meeting['users'][userEmail]['answer'] = answer

        # If the answer was correct, then increment the user's score
        if answer == questions[meeting['currentQuestionIndex']]['correctAnswerIndex']:
            meeting['users'][userEmail]['score'] += 1

        # If all users have answered, then end then show results!
        showResults = True
        for user in meeting['users'].values():
            answer = user['answer']
            if answer == -1:
                showResults = False
        meeting['showResults'] = showResults

        emit('meeting_update', meeting, broadcast=True)


@socketio.on('start_question')
def handle_start_question(data):
    """
    Should only be called by the host
    """
    userEmail = data['userEmail']
    meetingID = data['meetingID']
    currentQuestionIndex = data['currentQuestionIndex']
    startTimeUTC = data['startTimeUTC']

    print(f'start question with index {currentQuestionIndex + 1} by user {userEmail}')
    if meetings[meetingID]['users'][userEmail]['isHost']:
        # Increment question index
        meetings[meetingID]['currentQuestionIndex'] = currentQuestionIndex + 1

        # Reinitialize answer data for meetingID
        meetings[meetingID]['startTimeUTC'] = startTimeUTC
        meetings[meetingID]['showResults'] = False
        meetings[meetingID]['showScores'] = False
        meetings[meetingID]['answers'] = defaultdict(int)
        for user in meetings[meetingID]['users'].values():
            user['answer'] = -1

        # If there are no more questions, then end the game
        if currentQuestionIndex + 1 >= len(questions):
            meetings[meetingID]['startTimeUTC'] = 0
            meetings[meetingID]['answers'] = defaultdict(int)
            meetings[meetingID]['currentQuestionIndex'] = -1
            for user in meetings[meetingID]['users'].values():
                user['answer'] = -1
                user['score'] = 0

        emit('meeting_update', meetings[meetingID], broadcast=True)


@socketio.on('end_game')
def handle_end_game(data):
    """
    Should only be called by the host
    """
    userEmail = data['userEmail']
    meetingID = data['meetingID']

    print(f'game ended by user {userEmail}')
    if meetings[meetingID]['users'][userEmail]['isHost']:
        # Reinitialize answer data
        meetings[meetingID]['startTimeUTC'] = 0
        meetings[meetingID]['showResults'] = False
        meetings[meetingID]['showScores'] = False
        meetings[meetingID]['answers'] = defaultdict(int)
        meetings[meetingID]['currentQuestionIndex'] = -1
        for user in meetings[meetingID]['users'].values():
            user['answer'] = -1
            user['score'] = 0
        emit('meeting_update', meetings[meetingID], broadcast=True)


@socketio.on('show_results')
def handle_show_results(data):
    """
    Should only be called by the host
    """
    userEmail = data['userEmail']
    meetingID = data['meetingID']

    if meetings[meetingID]['users'][userEmail]['isHost']:
        print(f'show results by user {userEmail}')
        meetings[meetingID]['showResults'] = True
        emit('meeting_update', meetings[meetingID], broadcast=True)


@socketio.on('show_scores')
def handle_show_scores(data):
    """
    Should only be called by the host
    """
    userEmail = data['userEmail']
    meetingID = data['meetingID']

    if meetings[meetingID]['users'][userEmail]['isHost']:
        print(f'show scores by user {userEmail}')
        meetings[meetingID]['showScores'] = True
        meetings[meetingID]['showResults'] = False
        emit('meeting_update', meetings[meetingID], broadcast=True)


@socketio.on('join')
def handle_join(data):
    userEmail = data['userEmail']
    meetingID = data['meetingID']
    userName = data['userName']
    avatar = data['avatar']

    print(f'user {userEmail} joined meeting {meetingID}')

    # Don't join twice
    if not (meetingID in meetings and userEmail in meetings[meetingID]['users']):
        print('...and they are a new user')

        # Join websocket room
        join_room(meetingID)

        # Add user to the meeting, as host if they're the first
        isHost = meetingID not in meetings
        meetings[meetingID]['users'][userEmail] = {
            "isHost": isHost,
            "answer": -1,
            "score": 0,
            "userName": userName,
            "avatar": avatar,
        }

    # Send updated meeting object to all members
    emit('meeting_update', meetings[meetingID], broadcast=True)


#
# Normal routes
#
@app.route('/get_questions', methods=("POST",))
def get_questions():
    return {
        "questions": questions
    }


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
