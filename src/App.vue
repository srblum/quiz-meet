<template>
  <div id="app">
    <Questions v-if="loaded" v-bind:socket="socket"/>
  </div>
</template>

<script>
import Questions from "./components/questions/Questions.vue";
import { contains } from "./utils";
import io from 'socket.io-client';

export default {
  name: "App",
  data() {
    return {
      socket: null,
    };
  },
  components: {
    Questions,
  },
  created: function() {
    this.scrapeUserData();
    this.getQuizData();
    this.setupWebSocket();
  },
  computed: {
    loaded() {
      return this.$store.state.questions && this.$store.state.meeting;
    },
  },
  methods: {
    scrapeUserData() {
      const dataScript = contains("script", "ds:7");
      const userData = JSON.parse(dataScript[1].text.match(/\[[^\}]*/)[0]);
      let data = {
        meetingID: document.querySelector("[data-unresolved-meeting-id]").getAttribute("data-unresolved-meeting-id"),
        email: userData[4],
        name: userData[6],
        team: userData[28],
        avatar: userData[5],
      };
      this.$store.dispatch("addUserData", data);
    },
    getQuizData() {
        const response = fetch("https://34.94.148.202/get_questions", {
          method: 'POST',
          mode: 'cors',
        })
        .then(response => response.json())
        .then(questions => {
          this.$store.dispatch("setQuestions", questions["questions"]);
        });
    },
    setupWebSocket() {
      const socket = io("wss://34.94.148.202");
      socket.on('connect', () => {  
        socket.emit("join", {
          userName: this.$store.getters.getUser("name"),
          userEmail: this.$store.getters.getUser("email"),
          avatar: this.$store.getters.getUser("avatar"),
          meetingID: this.$store.getters.getUser("meetingID"),
        });
      });
      socket.on("meeting_update", (meeting) => {
        this.$store.dispatch("setMeeting", meeting);
      });
      this.socket = socket;
    }
  },
};
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;700;900&display=swap');

#app {
  position: fixed;
  top: 0px;
  left: 0px;
  bottom: 0px;
  z-index: 100000;
  pointer-events: none;
  font-family: 'Rubik', sans-serif;
}

</style>
