<template>
  <b-container class="playback-container">
 <b-row class="buttons-row">
  <b-col class="text-center">
  <b-button class="playback-button" id="back-button" @click="back()"><b-icon-skip-start-fill></b-icon-skip-start-fill></b-button>
  <b-button class="playback-button" id="play-button" v-show="!playing" @click="play()"><b-icon-play-fill></b-icon-play-fill></b-button>
  <b-button class="playback-button" id="pause-button" v-show="playing" @click="pause()"><b-icon-pause-fill></b-icon-pause-fill></b-button>
  <b-button class="playback-button" id="forward-button" @click="next()"><b-icon-skip-end-fill></b-icon-skip-end-fill></b-button>
</b-col>
</b-row>
 <b-row class="seekbar-row">
  <b-col class="text-center">
<table class="seekbar-table" width="100%">
  <tr>
    <td class="footertable" width="10%"><span id="time-progress">{{ display_progress }}</span></td>
    <td class="footertable" width="80%">
        <div class="slidecontainer">
            <b-form-input class="slider" id="progressbar" step="1000" v-model="progress" @input="setPlayback(progress, duration); suspendTimer();" @change="seek(progress)" type="range" min="0" :max="Math.floor(duration/1000) * 1000"></b-form-input>
            <!-- <input type="range" min="0" max="100" value="0" class="slider" id="progressbar" oninput="holdrange(this.value)" onchange="seekspotify(this.value)"> -->
        </div>
    </td>
    <td class="footertable" width="10%"><span id="time-duration">{{ display_duration }}</span></td>
  </tr>
</table>
</b-col>
</b-row>
</b-container>
</template>

<script>
import spotify from '@/SpotifyFunctions.js'
import {eventBus} from "../../main.js";

export default {
  data() {
    return {
      token: "",
      player: "",
      playing: false,
      progress: 0,
      duration: 0,  //CHANGE
      display_duration: "00:00",
      display_progress: "00:00",
      suspend: true,
      delay: 0
    };
  },
  methods: {
    play() {
      spotify.pressPlay(window.token, window.device_id);
    },
    pause() {
      spotify.pauseTrack(window.token);
    },
    back() {
      spotify.beginningTrack(window.token, window.device_id);
      this.setPlayback(0, this.duration);
    },
    next() {
      spotify.nextTrack(window.token);
      eventBus.$emit('fireNextTrack');
    },
    suspendTimer() {
      this.suspend = true; //CHANGE
    },
    seek(progress) {
      spotify.seekToPosition(window.token, progress);
      this.setPlayback(progress, this.duration);
    },
    setPlayback(progress, duration) {
      this.progress = progress;
      this.duration = duration;
      this.display_progress = this.msToHMS(progress);
      this.display_duration = this.msToHMS(duration);
    },
    msToHMS(duration) {
        if (duration < 0) {
          duration = 0;
        }
        var seconds = parseInt((duration / 1000) % 60),
            minutes = parseInt((duration / (1000 * 60)) % 60);
        minutes = (minutes < 10) ? "0" + minutes : minutes;
        seconds = (seconds < 10) ? "0" + seconds : seconds;
        return minutes + ":" + seconds;
    },
    playbackTimer(){
        if(!this.suspend) { // CHANGE
            this.setPlayback(this.progress, this.duration);
            this.progress = parseInt(this.progress) + 1000; // check ordering
            if(this.progress >= this.duration) {
                this.setPlayback(this.duration, this.duration);
                this.suspend = true;
            }
            if(this.progress < 0) {
                this.setPlayback(0, this.duration);
            }

        }
    },
    startTimer(){
        this.suspend = false;
    },
    delayStartTimer(){
        this.suspend = true;
        setTimeout(this.startTimer, this.delay);
    },
  },
  created() {
    eventBus.$on('fireNowPlaying', () => {
          this.playing = true;
          this.delayStartTimer();
    })
    eventBus.$on('fireNowPaused', () => {
          this.playing = false;
          this.suspend = true;
    })
    eventBus.$on('fireSeekToPosition', () => {
         if (this.playing === true) {
                  this.delayStartTimer();
                } else {
                  this.suspend = true;
                }
    })
    eventBus.$on('fireCurrentPlayerInfo', (data) => {
          this.playing = data.is_playing;
          if (this.playing == true) {
            this.delayStartTimer();
          } else {
            this.suspend = true;
          }
          this.setPlayback(data.progress_ms, data.item.duration_ms);
    })
  },
  mounted() {
    setInterval(this.playbackTimer, 1000);
  },
};
</script>

<style>
.playback-container{
  /*padding: calc((100px - 36px - 27px)/2);*/
  padding: 13px;
  font-size: 14px;
}

.slider {
  -webkit-appearance: none;
  width: 100%;
  height: 6px;
  background: #6a7682;
  outline: none;
  opacity: 0.8;
  -webkit-transition: .2s;
  transition: opacity .2s;
  cursor: pointer;
  border-radius: 3px;
  vertical-align: middle;
}

.slider:hover {
  opacity: 1; /* Fully shown on mouse-over */
}

/*.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 12px;
  height: 12px;
  background: #fff;
  cursor: pointer;
  border-radius: 50%;
  border: none;
}

.slider::-moz-range-thumb {
  width: 12px;
  height: 12px;
  background: #fff;
  cursor: pointer;
  border-radius: 50%;
  border: none;
}*/

.slidecontainer {
  width: 100%;
  padding-left: 10px;
  padding-right: 10px;
  padding-bottom:  1px;
}
/*.playback-row{
  padding: 30px;
}*/
.btn-secondary{
  background-color: #343a40 !important;
}
.btn:hover{
  background-color: #484e53 !important;
}
.btn{
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}
.btn:focus,.btn:active:focus,.btn.active:focus,
.btn.focus,.btn:active.focus,.btn.active.focus {
  border: none !important;
    outline: none !important;
    box-shadow: none !important;
    background-color: none !important;
}
</style>
