<template>
  <b-container class="playback-container">
 <b-row class="buttons-row">
  <b-col class="text-center text-nowrap">
  <b-button class="playback-button gray" id="shuffle-play" v-show="!$view.shuffle && $view.mode == 'radio'" @click="shufflePlayback()"><b-icon-shuffle></b-icon-shuffle></b-button>
  <b-button class="playback-button" id="shuffle-play" v-show="$view.shuffle && $view.mode == 'radio'" @click="shufflePlayback()" ><b-icon-shuffle variant="warning"></b-icon-shuffle></b-button>
  <b-button class="playback-button gray" id="random-button" v-show="$view.mode != 'radio'" @click="playRandom()" ><b-icon-dice5></b-icon-dice5></b-button>
  <b-button class="playback-button" v-show="$view.mode == 'radio'" id="previous-work-button" @click="previousWork()"><b-icon-arrow-left-circle></b-icon-arrow-left-circle></b-button>
  <b-button class="playback-button" id="back-button" @click="back()"><b-icon-skip-start-fill></b-icon-skip-start-fill></b-button>
  <b-button class="playback-button" id="play-button" v-show="!playing" @click="play()"><b-icon-play-fill></b-icon-play-fill></b-button>
  <b-button class="playback-button" id="pause-button" v-show="playing" @click="pause()"><b-icon-pause-fill></b-icon-pause-fill></b-button>
  <b-button class="playback-button" id="forward-button" @click="next()"><b-icon-skip-end-fill></b-icon-skip-end-fill></b-button>
  <b-button class="playback-button" v-show="$view.mode == 'radio'" id="next-work-button" @click="nextWorkNoDebounce()"><b-icon-arrow-right-circle></b-icon-arrow-right-circle></b-button>
  <b-button class="playback-button gray" id="like-work-button" v-show="!$view.like" @click="toggleLike()"><b-icon-heart></b-icon-heart></b-button>
  <b-button class="playback-button red" id="unlike-work-button" v-show="$view.like" @click="toggleLike()"><b-icon-heart-fill></b-icon-heart-fill></b-button>
</b-col>
</b-row>
 <b-row class="seekbar-row">
  <b-col class="text-center">
<table class="seekbar-table" width="100%">
  <tr>
    <td class="footertable" width="10%"><div class="time" id="time-progress">{{ display_progress }}</div></td>
    <td class="footertable" width="80%">
        <div class="slidecontainer">
            <b-form-input class="slider" id="progressbar" step="1000" v-model="progress" @input="setPlayback(progress, duration); suspendTimer();" @change="seek(progress)" type="range" min="0" :max="Math.floor(duration/1000) * 1000"></b-form-input>
            <!-- <input type="range" min="0" max="100" value="0" class="slider" id="progressbar" oninput="holdrange(this.value)" onchange="seekspotify(this.value)"> -->
        </div>
    </td>
    <td class="footertable" width="10%"><div class="time" id="time-duration">{{ display_duration }}</div></td>
  </tr>
</table>
</b-col>
</b-row>
</b-container>
</template>

<script>
import spotify from '@/SpotifyFunctions.js'
import {eventBus} from "../../main.js";
import axios from 'axios';

// function debounce(func, timeout = 500){
//   let timer;
//   return (...args) => {
//     if (!timer) {
//       func.apply(this, args);
//     }
//     clearTimeout(timer);
//     timer = setTimeout(() => {
//       timer = undefined;
//     }, timeout);
//   };
// }

const debouncedNext = debounce(() => fireNextWork());
let allowNext = false;

function debounce(func, timeout = 2000){
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => { func.apply(this, args); }, timeout);
  };
}

function fireNextWork(){
  if (allowNext) {
    allowNext = false;
    eventBus.$emit('fireNextWork');
  }
}


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
      delay: 1000
    };
  },
  methods: {
    play() {
      spotify.pressPlay(this.$auth.clientToken, this.$auth.deviceID);
    },
    pause() {
      spotify.pauseTrack(this.$auth.clientToken);
    },
    back() {
      if(this.progress > 2000){
          spotify.beginningTrack(this.$auth.clientToken, this.$auth.deviceID);
          this.setPlayback(0, this.duration);
      } else {
      let uriList = {}
      let jsonList = {}

      // ensure unnecessary whitespace in track list (gives spotify erors):
      var smushTracks = this.$config.previousTracks.replace(/\s/g,'');
      var cleanTracks = smushTracks.replaceAll('spotify', ' spotify').trim();

      uriList['uris'] = cleanTracks.split(' ');
      jsonList = JSON.stringify(uriList);
      spotify.playTracks(this.$auth.clientToken, this.$auth.deviceID, jsonList);
      }
    },
    next() {
      spotify.nextTrack(this.$auth.clientToken);
    },
    suspendTimer() {
      this.suspend = true;
    },
    seek(progress) {
      spotify.seekToPosition(this.$auth.clientToken, progress);
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
        if(!this.suspend) {

            this.progress = parseInt(this.progress) + 1000;
            this.setPlayback(this.progress, this.duration);

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
    nextWork(){
        debouncedNext();
    },
    nextWorkNoDebounce(){
        allowNext = true;
        fireNextWork();
    },
    previousWork(){
        eventBus.$emit('firePreviousWork');
    },
    shufflePlayback(){
      this.$view.shuffle = !this.$view.shuffle;
    },
    playRandom(){
      this.$view.shuffle = true;
      this.nextWorkNoDebounce();
    },
    likeDatabase(albumID, action){
      const path = 'api/like/' + albumID + '/' + action;
      // eslint-disable-next-line
      axios.get(path).then((res) => {
        eventBus.$emit('fireRefreshWorks');
      }).catch((error) => {
        console.error(error);
      })
    },
    toggleLike(){
      if (this.$auth.clientToken){
        this.$view.like = !this.$view.like;
        if(this.$view.like){
          this.likeDatabase(this.$config.album, 'like');
          eventBus.$emit('fireLikeAlbum');
        } else {
          this.likeDatabase(this.$config.album, 'unlike');
          eventBus.$emit('fireUnlikeAlbum');
        }
      }
    }
  },
  created() {
    eventBus.$on('fireNowPlaying', () => {
          // this.playing = true;
          // this.delayStartTimer();
    })
    eventBus.$on('fireNowPaused', () => {
          // this.playing = false;
          // this.suspend = true;
    })
    eventBus.$on('fireSeekToPosition', () => {
         if (this.playing === true) {
                  this.delayStartTimer();
                } else {
                  this.suspend = true;
                }
    })
    // eventBus.$on('fireCurrentPlayerInfo', (data) => {
    //       this.playing = data.is_playing;
    //       if (this.playing == true) {
    //         this.delayStartTimer();
    //       } else {
    //         this.suspend = true;
    //       }
    //       this.setPlayback(data.progress_ms, data.item.duration_ms);
    // })

    // eventBus.$on('fireAutoplayFailed', () => {
    //     this.playing = false;
    //     this.suspend = true;
    //     this.setPlayback(0, this.duration);
    // })

    eventBus.$on('firePlayerStateChanged', (track_data, position, duration, paused) => {
      if (position == 0 && !paused){ // can delay timer here if glitchy
          this.playing = true;
          this.startTimer();
          this.setPlayback(0, duration);
      }
      else if (position == 0 && paused && allowNext){ //advance to next work when play stops current work
          // Spotify API spams function with requests when changing track, debounce function
          this.nextWork();
      }
      else if (position > 0 && position < 3000 && !paused){ // used to need this, Spotify changed behavior to not need it though?
          allowNext = true;
          this.playing = true;
          this.startTimer();
      }
      else {
          this.playing = !paused;
          if (position > 0){ // prevent firefox crash
            allowNext = true;
          }
          if (this.playing == true) {
            this.startTimer();
          } else {
            this.suspend = true;
          }
          this.setPlayback(position, duration);
      }
      // update previousTracks
      let selectedTrack = track_data.uri;
      let allTracks = this.$config.allTracks.split(' ');

      let index = allTracks.indexOf(selectedTrack);
      let previousTracks = "";

      if (index == 0) {
          previousTracks = this.$config.allTracks;
      } else if (index < 0 ){ // occurs when spotify redirects, track not found in list
          previousTracks = this.$config.allTracks;
      } else {
        for (var i = index - 1; i < allTracks.length; i++) {
          previousTracks = previousTracks + " " + allTracks[i];
        }
      }

      this.$config.previousTracks = previousTracks.trim();
      // localStorage.setItem('currentConfig', JSON.stringify(currentConfig));

    })
  },
  mounted() {
    setInterval(this.playbackTimer, 1000);
  },
};
</script>

<style scoped>
.playback-container{
  /*top padding set in App.vue*/
  padding: 13px;
  padding-bottom: 0px;
  font-size: 14px;
}
td{
  vertical-align: top;
}
.time{
  margin-top: 0.5px;
}

.slidecontainer {
  width: 100%;
  padding-left: 10px;
  padding-right: 10px;
  padding-top: 1px;
  padding-bottom:  0px;
}

input[type="range"] {
  -webkit-appearance: none !important;
  appearance: none !important;
  background: transparent !important;
  cursor: pointer !important;
  width: 100% !important;
  opacity: 0.85;
}


input[type="range"]::-webkit-slider-runnable-track {
  background: #787f87;
  height: 6px;
}
input[type="range"]::-moz-range-track {
  background: #787f87;
  height: 6px;
  border-radius: 0px;
}

input[type="range"]:hover {
  opacity: 1;
}


input[type="range"]::-webkit-slider-thumb {
   -webkit-appearance: none; /* Override default look */
   appearance: none;
   margin-top: -3px; /* Centers thumb on the track */
   background-color: #fff;
   height: 0px;
   width: 0px;
}
input[type="range"]::-moz-range-thumb {
    border: none; /*Removes extra border that FF applies*/
    background-color: #fff;
    height: 0px;
    width: 0px;
}


input[type="range"]:focus {
  outline: none;
}
/*input[type="range"]:focus::-webkit-slider-thumb {
  outline: 1.5px solid rgba(255, 255, 255, 0.5);
  outline-offset: 0.125rem;
}
input[type="range"]:focus::-moz-range-thumb {
  outline: 1.5px solid rgba(255, 255, 255, 0.5);
  outline-offset: 0.125rem;
}*/

/*Chrome*/
@media screen and (-webkit-min-device-pixel-ratio:0) {

    input[type='range']::-webkit-slider-runnable-track {
      overflow: hidden;
      height: 6px;
      color: #ffc107;
      margin-top: -3px;
    }

    input[type='range']::-webkit-slider-thumb {
      box-shadow: -350px 0 0 350px #ffc107;
    }

}
/** FF*/
input[type="range"]::-moz-range-progress {
  background-color: #ffc107;
  height: 6px;
}








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
.gray{
    color: darkgray !important;
}
.red{
    color: var(--red) !important;
}
.btn:focus,.btn:active:focus,.btn.active:focus,
.btn.focus,.btn:active.focus,.btn.active.focus {
  border: none !important;
    outline: none !important;
    box-shadow: none !important;
    background-color: #343a40 !important;
}
</style>
