<template>
  <b-container class="playback-container">
 <b-row class="buttons-row">
  <b-col class="text-center">
  <b-button class="playback-button" id="shuffle-play" v-show="!shuffle" @click="shufflePlayback()"><b-icon-shuffle></b-icon-shuffle></b-button>
  <b-button class="playback-button" id="shuffle-play" v-show="shuffle" @click="shufflePlayback()" ><b-icon-shuffle variant="success"></b-icon-shuffle></b-button>
  <b-button class="playback-button" id="previous-work-button" @click="previousWork()"><b-icon-arrow-left-circle></b-icon-arrow-left-circle></b-button>
  <b-button class="playback-button" id="back-button" @click="back()"><b-icon-skip-start-fill></b-icon-skip-start-fill></b-button>
  <b-button class="playback-button" id="play-button" v-show="!playing" @click="play()"><b-icon-play-fill></b-icon-play-fill></b-button>
  <b-button class="playback-button" id="pause-button" v-show="playing" @click="pause()"><b-icon-pause-fill></b-icon-pause-fill></b-button>
  <b-button class="playback-button" id="forward-button" @click="next()"><b-icon-skip-end-fill></b-icon-skip-end-fill></b-button>
  <b-button class="playback-button" id="next-work-button" @click="nextWorkNoDebounce()"><b-icon-arrow-right-circle></b-icon-arrow-right-circle></b-button>
  <b-button class="playback-button" id="next-work-button" @click="like()"><b-icon-heart></b-icon-heart></b-button>
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
import {currentConfig} from "../../main.js";
import {spotifyConfig} from "../../main.js";

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
    console.log('NEXT');
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
      delay: 1000,
      shuffle: false
    };
  },
  methods: {
    play() {
      window.player.activateElement();
      spotify.pressPlay(spotifyConfig.clientToken, spotifyConfig.deviceID);
    },
    pause() {
      spotify.pauseTrack(spotifyConfig.clientToken);
    },
    back() {
      if(this.progress > 2000){
          spotify.beginningTrack(spotifyConfig.clientToken, spotifyConfig.deviceID);
          this.setPlayback(0, this.duration);
      } else {
      let uriList = {}
      let jsonList = {}
      uriList['uris'] = currentConfig.previousTracks.split(' ');
      jsonList = JSON.stringify(uriList);
      spotify.playTracks(spotifyConfig.clientToken, spotifyConfig.deviceID, jsonList);
      }
    },
    next() {
      spotify.nextTrack(spotifyConfig.clientToken);
    },
    suspendTimer() {
      this.suspend = true;
    },
    seek(progress) {
      spotify.seekToPosition(spotifyConfig.clientToken, progress);
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
        console.log("next");
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
      this.shuffle = !this.shuffle;
      eventBus.$emit('fireToggleShuffle', this.shuffle);

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

    eventBus.$on('fireAutoplayFailed', () => {
        this.playing = false;
        this.suspend = true;
        this.setPlayback(0, this.duration);
    })

    eventBus.$on('firePlayerStateChanged', (track_data, position, duration, paused) => {
      console.log(position, paused);
      if (position == 0 && !paused){ //ignore at beginning of song (glitchy)
          this.playing = true;
          this.suspend = true;
          this.setPlayback(0, duration);
      }
      else if (position == 0 && paused && allowNext){ //advance to next work when play stops current work
          // Spotify API spams function with requests when changing track, debounce function
          this.nextWork();
      }
      else if (position > 0 && position < 3000 && !paused){
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
      let allTracks = currentConfig.allTracks.split(' ');

      let index = allTracks.indexOf(selectedTrack);
      let previousTracks = "";

      if (index == 0) {
          previousTracks = currentConfig.allTracks;
      } else if (index < 0 ){ // occurs when spotify redirects, track not found in list
          previousTracks = currentConfig.allTracks;
      } else {
        for (var i = index - 1; i < allTracks.length; i++) {
          previousTracks = previousTracks + " " + allTracks[i];
        }
      }

      currentConfig.previousTracks = previousTracks.trim();
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
  /*padding: calc((100px - 36px - 27px)/2);*/
  padding: 13px;
  padding-top: 18px;
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
