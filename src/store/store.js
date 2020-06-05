import Vuex from "vuex";
import Vue from "vue";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    extensionID: "nhfoglnfaobjdcclkfnikaefmhfmekie",
    userData: null,
    meeting: null,
    questions: null,
  },
  getters: {
    getUser: (state) => (key) => {
      return state.userData ? state.userData[key] : null;
    },
    isHost: (state) => () => {
      if (state.meeting && state.userData ) {        
        const userEmail = state.userData['email'];
        return state.meeting['users'][userEmail]['isHost'];
      } else {
        return false;
      }
    },
    getCurrentQuestion: (state) => () => {
      if (state.meeting && state.questions && state.meeting['currentQuestionIndex'] > -1) {
        const currentQuestionIndex = state.meeting['currentQuestionIndex'];
        return state.questions[currentQuestionIndex];
      } else {
        return null;
      }
    },
    myAnswer: (state) => () => {
      if (state.meeting && state.questions && state.meeting['currentQuestionIndex'] > -1) {
        const userEmail = state.userData['email'];
        const myAnswer = state.meeting['users'][userEmail]['answer'];
        return myAnswer >= 0 ? myAnswer : null;
      } else {
        return null;
      }
    },
  },
  mutations: {
    addUserData(state, data) {
      state.userData = data;
    },
    setMeeting(state, meeting) {
      state.meeting = meeting;
    },
    setQuestions(state, questions) {
      state.questions = questions
    }
  },
  actions: {
    addUserData(context, data) {
      context.commit("addUserData", data);
    },
    setMeeting(context, meeting) {
      context.commit("setMeeting", meeting);
    },
    setQuestions(context, questions) {
      context.commit("setQuestions", questions);
    },
  },
});
