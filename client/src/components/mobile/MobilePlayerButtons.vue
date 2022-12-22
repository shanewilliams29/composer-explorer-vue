<!-- Parent is PlayerControls.vue -->
<template>  
  <b-col class="text-center text-nowrap">
    <b-button class="playback-button gray" id="shuffle-play" 
      v-show="!$view.shuffle && $view.mode == 'radio'" @click="$parent.shufflePlayback()">
      <b-icon-shuffle></b-icon-shuffle>
    </b-button>
    <b-button class="playback-button" id="shuffle-play" 
      v-show="$view.shuffle && $view.mode == 'radio'" @click="$parent.shufflePlayback()">
      <b-icon-shuffle variant="warning"></b-icon-shuffle>
    </b-button>
    <b-button class="playback-button gray" id="random-button" 
      v-show="$view.mode != 'radio'" @click="$parent.playRandom()">
      <b-icon-dice5></b-icon-dice5>
    </b-button>
    <b-button class="playback-button" id="previous-work-button" 
      v-show="$view.mode == 'radio'" @click="$parent.previousWork()">
      <b-icon-arrow-left-circle></b-icon-arrow-left-circle>
    </b-button>
    <b-button size="lg" class="playback-button" id="back-button" @click="$parent.back()">
      <b-icon-skip-start-fill></b-icon-skip-start-fill>
    </b-button>
    <!-- Play button is handled in the SpotifyPlayer.vue listener -->
    <b-button size="lg" class="playback-button" id="play-button" v-show="!$parent.playing">
      <b-icon-play-fill></b-icon-play-fill>
    </b-button>
    <b-button size="lg" class="playback-button" id="pause-button" 
      v-show="$parent.playing" @click="$parent.pause()">
      <b-icon-pause-fill></b-icon-pause-fill>
    </b-button>
    <b-button size="lg" class="playback-button" id="forward-button" @click="$parent.next()">
      <b-icon-skip-end-fill></b-icon-skip-end-fill>
    </b-button>
    <b-button class="playback-button" id="next-work-button" 
      v-show="$view.mode == 'radio'" @click="$parent.nextWorkNoDebounce()">
      <b-icon-arrow-right-circle></b-icon-arrow-right-circle>
    </b-button>
    <b-button class="playback-button gray" id="like-work-button" 
      v-show="!$view.like" @click="$parent.toggleLike()">
      <b-icon-heart></b-icon-heart>
    </b-button>
    <b-button class="playback-button red" id="unlike-work-button" 
      v-show="$view.like" @click="$parent.toggleLike()">
      <b-icon-heart-fill></b-icon-heart-fill>
    </b-button>
  </b-col>
</template>

<style scoped>
.btn-secondary {
  background: none !important;
}
.btn:hover {
  background-color: #484e53 !important;
}
.btn:active {
  background-color: #484e53 !important;
}
.btn {
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
}
.gray {
  color: var(--medium-dark-gray) !important;
}
.red {
  color: var(--red) !important;
}
.btn:focus,
.btn:active:focus,
.btn.active:focus,
.btn.focus,
.btn:active.focus,
.btn.active.focus {
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
  background: none !important;
}
</style>