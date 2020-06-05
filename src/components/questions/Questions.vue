<template>
  <div class="quiz-container">
    <div v-if="question || showScores" class="question-container">
      {{ showScores ? "Leaderboard" : question.question}}
    </div>
    <div v-if="isHost && question" class="end-game" @click="endGame()">End Game</div>
    <img v-if="!question" :src="getLogo" alt="QuizMeet icon" class="logo" />
    <div v-if="!question && isHost" class="start-button" @click="startQuestion()">START</div>
    <div v-if="!question && !isHost" class="waiting" >Waiting for the host to start the game...</div>
    <div v-if="!showResults && !showScores">
      <img v-if="isHost && question" :src="getSkip" class="skip-button" @click="startQuestion()"/>
      <div v-if="question" :class="['timer', 'shadow', timeLeft===0 ? 'red' : '']">
        {{timeLeft}}
      </div>
    </div>


    <div v-if="showScores && question" class="score-container">
      <div v-for="(user, index) in topScoringUsers" :class='["score", "score"+(index+1)]'>
        <span class="score-letter">{{ordinalMap[index]}}</span>
        <span class="score-content">{{`${user.userName}: ${user.score}`}}</span>
        <img :src="user.avatar" class="score-avatar" alt="">
      </div>
    </div>
    <img v-if="isHost && showScores" :src="getNext" class="next-button" @click="startQuestion()"/>


    <div v-if="showResults && question && results">
      <div class="result-container">
        <div class="result resultA" :style="{height: getBarHeight(0)}">
          <span class="result-total">
            <span v-if="question.correctAnswerIndex === 0">&#10003;</span>
            {{results[0] || 0}}
          </span>
          <span class="result-label">A</span>
        </div>
        <div class="result resultB" :style="{height: getBarHeight(1)}">
          <span class="result-total">
            <span v-if="question.correctAnswerIndex === 1">&#10003;</span>
            {{results[1] || 0}}
          </span>
          <span class="result-label">B</span>
        </div>
        <div class="result resultC" :style="{height: getBarHeight(2)}">
          <span class="result-total">
            <span v-if="question.correctAnswerIndex === 2">&#10003;</span>
            {{results[2] || 0}}
          </span>
          <span class="result-label">C</span>
        </div>
        <div class="result resultD" :style="{height: getBarHeight(3)}">
          <span class="result-total">
            <span v-if="question.correctAnswerIndex === 3">&#10003;</span>
            {{results[3] || 0}}
          </span>
          <span class="result-label">D</span>
        </div>
      </div>
      <img v-if="isHost" :src="getNext" class="next-button" @click="goToScores()"/>
    </div>


    <div v-if="question && !showScores" class="answer-container">
      <div :class='["answer", "answerA", "shadow", myAnswer !== null && myAnswer!==0 ? "faded" : ""]' @click="sendAnswer(0)">
        <span class="answer-letter">A</span>
        <span class="answer-content">{{question.answers[0]}}</span>
      </div>
      <div :class='["answer", "answerB", "shadow", myAnswer !== null && myAnswer!==1 ? "faded" : ""]' @click="sendAnswer(1)">
        <span class="answer-letter">B</span>
        <span class="answer-content">{{question.answers[1]}}</span>
      </div>
      <div :class='["answer", "answerC", "shadow", myAnswer !== null && myAnswer!==2 ? "faded" : ""]' @click="sendAnswer(2)">
        <span class="answer-letter">C</span>
        <span class="answer-content">{{question.answers[2]}}</span>
      </div>
      <div :class='["answer", "answerD", "shadow", myAnswer !== null && myAnswer!==3 ? "faded" : ""]' @click="sendAnswer(3)">
        <span class="answer-letter">D</span>
        <span class="answer-content">{{question.answers[3]}}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { generateUUID } from "../../utils";

export default {
  data() {
    return {
      timeLeft: 60,
      timerInterval: null,
      ordinalMap: {0: "1st", 1: "2nd", 2: "3rd", 3: "4th"}
    }
  },
  computed: {
    question() {
      return this.$store.getters.getCurrentQuestion();
    },
    isHost() {
      return this.$store.getters.isHost();
    },
    meeting() {
      return this.$store.state.meeting;
    },
    showResults() {
      return this.$store.state.meeting.showResults;
    },
    showScores() {
      return this.$store.state.meeting.showScores;
    },
    startTimeUTC() {
      return this.$store.state.meeting.startTimeUTC;
    },
    getLogo() {
      return `chrome-extension://${this.$store.state.extensionID}/img/logo.svg`;
    },
    getNext() {
      return `chrome-extension://${this.$store.state.extensionID}/img/NextButton.svg`;
    },
    getSkip() {
      return `chrome-extension://${this.$store.state.extensionID}/img/SkipButton.svg`;
    },
    myAnswer() {
      return this.$store.getters.myAnswer();
    },
    results() {
      return this.$store.state.meeting.answers;
    },
    topScoringUsers() {
      return Object.values(this.$store.state.meeting.users)
        .sort((a,b) => a.score - b.score)
        .slice(0,4);
    }
  },
  methods: {
    sendAnswer(answer) {
      const { socket } = this.$attrs;
      if (socket) {
        socket.emit("answer", {
          answer,
          userEmail: this.$store.getters.getUser("email"),
          meetingID: this.$store.getters.getUser("meetingID"),
        })
      }
    },
    startQuestion() {
      const { socket } = this.$attrs;
      if (socket) {
        const now = new Date();
        socket.emit("start_question", {
          userEmail: this.$store.getters.getUser("email"),
          meetingID: this.$store.getters.getUser("meetingID"),
          currentQuestionIndex: this.$store.state.meeting.currentQuestionIndex,
          startTimeUTC: Math.ceil(Date.now()/1000),
        });

        //start timer
        this.timerInterval = window.setInterval(this.computeTimeLeft.bind(this), 1000);
      }
    },
    goToScores() {
      const { socket } = this.$attrs;
      if (socket) {
        const now = new Date();
        socket.emit("show_scores", {
          userEmail: this.$store.getters.getUser("email"),
          meetingID: this.$store.getters.getUser("meetingID"),
        });
      }
    },
    endQuestion() {
      const { socket } = this.$attrs;
      if (socket) {
        socket.emit("show_results", {
          userEmail: this.$store.getters.getUser("email"),
          meetingID: this.$store.getters.getUser("meetingID"),
        });
        this.clearInterval();
      }
    },
    endGame() {
      const { socket } = this.$attrs;
      if (socket) {
        socket.emit("end_game", {
          userEmail: this.$store.getters.getUser("email"),
          meetingID: this.$store.getters.getUser("meetingID"),
        });
        this.clearInterval();
      }
    },
    getBarHeight(index) {
      // bars range from 40 - 240px
      const total = Object.values(this.results).reduce((a,b) => a+b, 0);
      const votes = this.results[index] || 0;
      const barHeight = total ? (40 + ((votes/total) * 200)) + "px" : "40px";
      return barHeight;
    },
    computeTimeLeft() {
      const now = Math.ceil(Date.now()/1000);
      let timeLeft = 60 - Math.ceil(now - this.startTimeUTC);
      if (timeLeft > 60) {
        timeLeft = 60;
      } else if (timeLeft <= 0) {
        this.endQuestion();
        timeLeft = 0;
      }
      if (this.showResults) {
        timeLeft = 60;
        this.clearInterval();
      }
      this.timeLeft = timeLeft;
    },
    clearInterval() {
      this.timeLeft = 60;
      if (this.timerInterval) {
        window.clearInterval(this.timerInterval);
      }
    }
  },
};
</script>

<style lang="scss" scoped>
.quiz-container {
  position: absolute;
  top: 0;
  left: 10vw;
  width: 60vw;
  height: 100vh;
  .question-container {
    position:absolute;
    background: white;
    border-radius: 25px;
    top: 60px;
    left: 0;
    color: black;
    font-size: 32px;
    width: calc(100% - 24px);
    text-align: center;
    padding: 20px 12px;
    border: 5px solid #42CFCA;
  }
  .logo {
    height: 250px;
    width: 250px;
    position: absolute;
    bottom: calc(50vh + 50px);
    left: calc(50% - 125px);
    animation:spin 4s linear infinite;
  }
  @keyframes spin {
    100% { transform:rotate(360deg); }
  }
  .waiting {
    position: absolute;
    top: 50vh;
    background: white;
    border-radius: 25px;
    left: 0;
    color: black;
    font-size: 32px;
    width: calc(100% - 24px);
    text-align: center;
    padding: 20px 12px;
    border: 5px solid #42CFCA;
  }
  .start-button {
    pointer-events: all;
    height: 100px;
    width: 540px;
    background: #42CFCA;
    position: absolute;
    top: 50vh;
    left: calc(50% - 270px);
    border-radius: 50px;
    line-height: 100px;
    letter-spacing: 7.5px;
    cursor: pointer;
    text-align: center;
    font-size: 75px;
    color: white;
    font-weight: 900;
    text-shadow: 0px 4px #000000;
    box-shadow: 0px 4px #A4B0BE;
  }
  .next-button {
    pointer-events: all;
    cursor: pointer;
    width: 150px;
    height: 50px;
    position: absolute;
    top: 200px;
    right: 0px;
  }
  .end-game {
    pointer-events: all;
    cursor: pointer;
    width: 125px;
    height: 50px;
    border-radius: 10px;
    background: #A4B0BE;
    box-shadow: 0px 2px black;
    color: white;
    font-size: 18px;
    text-align: center;
    position: absolute;
    top: 200px;
    left: 0px;
    font-weight: 700;
    line-height: 50px;
    letter-spacing: 1.8px;
  }
  .skip-button {
    pointer-events: all;
    cursor: pointer;
    width: 150px;
    height: 50px;
    position: absolute;
    top: 200px;
    right: 0px;
  }
  .timer {
    background: #42CFCA;
    border-radius: 50%;
    height: 200px;
    width: 200px;
    position: absolute;
    top: 200px;
    left: calc(50% - 100px);
    color: white;
    font-size: 100px;
    text-align: center;
    font-family: rubik sans-serif;
    line-height: 200px;
    letter-spacing: 10px;
    font-weight: 900;
    text-shadow: 2px 2px #000000;
  }
  .red {
    background: red !important;
  }
  .shadow {
    box-shadow: 0px 2px #A4B0BE;
  }
  .result-container {
    position: absolute;
    width: 600px;
    height: 400px;
    bottom: 40vh;
    left: 12vh;
    .result {
      position: absolute;
      width: 150px;
      border-radius: 10px;
      font-size: 30px;
      text-align: center;
      bottom: 0;
      .result-label {
        color: white;
        position: absolute;
        font-weight: 900;
        bottom: 5px;
        left: 65px;
        text-shadow: 0px 2px black;
      }
      .result-total {
        display: inline-block;
        position: absolute;
        font-weight: 900;
        top: -43px;
        left: 0px;
        font-size: 40px;
        width: 150px;
        text-align: center;
        text-shadow: 0px 2px #C4C4C4;
      }
    }
    .resultA {
      background: #FF7388;
      color: #FF7388;
      left: 85px;
    }
    .resultB {
      background: #86FFAC;
      color: #86FFAC;
      left: 245px;
    }
    .resultC {
      background: #70A1FF;
      color: #70A1FF;
      left: 405px;
    }
    .resultD {
      background: #FFDF7B;
      color: #FFDF7B;
      left: 565px;
    }
  }
  .score-container {
    position: absolute;
    top: 290px;
    left: 8vw;
    height: 500px;
    .score {
      height: 70px;
      width: 40vw;
      line-height: 50px;
      font-size: 30px;
      color: black;
      position: absolute;
      border-radius: 50px;
      .score-letter {
        box-shadow: 0px -4px #A4B0BE;
        position: absolute;
        left: 10px;
        background: white;
        border-radius: 25px;
        height: 50px;
        width: 50px;
        top: 12px;
        color: black;
        text-align: center;
        font-weight: 700;
        font-size: 25px;
      }
      .score-content {
        position: absolute;
        left: 72px;
        top: 12px;
        font-weight: 400;
      }
      .score-avatar {
        position: absolute;
        right: 10px;
        border-radius: 25px;
        height: 50px;
        width: 50px;
        top: 12px;
        text-align: center;
      }
    }
    .score1 {
      background: #FF7388;
      top: 0;
      left: 0;
    }
    .score2 {
      background: #86FFAC;
      top: 80px;
      left: 0;
    }
    .score3 {
      background: #70A1FF;
      top: 160px;
      left: 0;
    }
    .score4 {
      background: #FFDF7B;
      top: 240px;
      left: 0;
    }
  }
  .answer-container {
    position: relative;
    margin-top: 65vh;
    left: 0;
    height: 180px;
    .answer {
      pointer-events: all;
      cursor: pointer;
      height: 80px;
      width: 45%;
      line-height: 50px;
      font-size: 45px;
      color: black;
      position: absolute;
      border-radius: 50px;
      .answer-letter {
        box-shadow: 0px -4px #A4B0BE;
        position: absolute;
        left: 17.5px;
        background: white;
        border-radius: 25px;
        height: 50px;
        width: 50px;
        top: 17.5px;
        color: black;
        text-align: center;
        font-weight: 900;
      }

      .answer-content {
        position: absolute;
        left: 80px;
        top: 17.5px;
        font-weight: 700;
      }
    }
    .answerA {
      background: #FF7388;
      top: 0;
      left: 0;
    }
    .answerB {
      background: #86FFAC;
      top: 0;
      right: 0;
    }
    .answerC {
      background: #70A1FF;
      bottom: 0;
      left: 0;
    }
    .answerD {
      background: #FFDF7B;
      bottom: 0;
      right: 0;
    }
    .faded {
      opacity: 0.5;
    }
  }
}
</style>
