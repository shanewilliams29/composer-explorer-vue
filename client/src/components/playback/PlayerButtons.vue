<template>  
  <b-col class="text-center text-nowrap">
    <b-button class="playback-button gray" id="shuffle-play-false" v-show="!$view.shuffle" 
      @click="$parent.shufflePlayback()">
      <b-icon-shuffle></b-icon-shuffle>
    </b-button>
    <b-button class="playback-button" id="shuffle-play-true" v-show="$view.shuffle" 
      @click="$parent.shufflePlayback()">
      <b-icon-shuffle variant="warning"></b-icon-shuffle>
    </b-button>
    <b-button class="playback-button" id="previous-work-button" 
      @click="$parent.previousWork()">
      <b-icon-arrow-left-circle></b-icon-arrow-left-circle>
    </b-button>
    <b-button class="playback-button" id="back-button">
      <b-icon-skip-start-fill></b-icon-skip-start-fill>
    </b-button>
    <b-button class="playback-button" id="play-button" v-show="!$parent.playing">
      <!-- Play button function is handled in the SpotifyPlayer.vue listener -->
      <b-icon-play-fill></b-icon-play-fill>
    </b-button>
    <b-button class="playback-button" id="pause-button" v-show="$parent.playing" >
      <b-icon-pause-fill></b-icon-pause-fill>
    </b-button>
    <b-button class="playback-button" id="forward-button">
      <b-icon-skip-end-fill></b-icon-skip-end-fill>
    </b-button>
    <b-button class="playback-button" id="next-work-button" 
      @click="$parent.nextWorkNoDebounce()">
      <b-icon-arrow-right-circle></b-icon-arrow-right-circle>
    </b-button>
    <b-button class="playback-button gray" id="like-work-button" v-show="!$view.like" 
      @click="$parent.toggleLike()">
      <b-icon-heart></b-icon-heart>
    </b-button>
    <b-button class="playback-button red" id="unlike-work-button" v-show="$view.like" 
      @click="$parent.toggleLike()">
      <b-icon-heart-fill></b-icon-heart-fill>
    </b-button>
  </b-col>
</template>

<style scoped>
.btn-secondary {
  background-color: var(--dark-gray) !important;
}
.btn:hover {
  background-color: #484e53 !important;
}
.btn {
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
}
.playback-button{
  color: var(--my-white);
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
  background-color: none !important;
}
</style>