<template>
  <div></div>
</template>

<script>
import axios from 'axios';
import {eventBus} from "@/main.js";
import {startTracks} from "@/main.js";
import spotify from '@/SpotifyFunctions.js'

let spotifyPlayerScript = document.createElement('script');
spotifyPlayerScript.setAttribute('src', 'https://sdk.scdn.co/spotify-player.js');
document.head.appendChild(spotifyPlayerScript);

export default {
  data() {
    return {};
  },
  methods: {
    initializeSpotify() {
      window.onSpotifyWebPlaybackSDKReady = () => {
        const path = 'api/get_token';
        axios.get(path, {withCredentials: true})
        .then((res) => {
          if (res.data.status == "success") {
            if (res.data.client_token !== null && res.data.premium) {
              this.$auth.clientToken = res.data.client_token;
              this.$auth.appToken = res.data.app_token;
              this.$auth.userid = res.data.user_id;
              this.$auth.knowledgeKey = res.data.knowledge_api;
              this.$auth.avatar = res.data.avatar;
              // eslint-disable-next-line
              window.player = new Spotify.Player({
                name: 'Composer Explorer',
                getOAuthToken: cb => {
                  cb(this.$auth.clientToken);
                },
                volume: 1
              });
              // Ready
              window.player.addListener('ready', ({
                device_id
              }) => {
                this.device_id = device_id;
                this.$auth.deviceID = device_id;
                window.device_id = device_id;
                console.log('Ready with Device ID', device_id);
              });
              // Not Ready
              window.player.addListener('not_ready', ({
                device_id
              }) => {
                console.log('Device ID has gone offline', device_id);
                alert('DEVICE NOT READY');
              });
              window.player.addListener('initialization_error', ({
                message
              }) => {
                alert(message);
                console.error(message);
              });
              window.player.addListener('authentication_error', ({
                message
              }) => {
                alert('AUTHENTICATION ERROR: ' + message);
                console.error(message);
              });
              window.player.addListener('account_error', ({
                message
              }) => {
                alert('ACCOUNT ERROR ' + message);
                console.error(message);
              });
              window.player.addListener('playback_error', ({
                message
              }) => {
                alert('PLAYBACK ERROR ' + message);
                console.error(message);
              });
              window.player.addListener('autoplay_failed', () => {
                console.log('Autoplay is not allowed by the browser autoplay rules');
                // eventBus.$emit('fireAutoplayFailed');
              });
              window.player.addListener('player_state_changed', ({
                position,
                duration,
                paused,
                track_window: {
                  current_track
                }
              }) => {
                eventBus.$emit('firePlayerStateChanged', current_track, position, duration, paused);
                //console.log(position , duration, paused);
                //console.log('Duration of Song', duration);
              });
              window.player.connect();
              // for Safari autoplay enable
              
              document.getElementById("play-button").addEventListener("click", function() {
                window.player.activateElement();
                let uriList = {}
                let jsonList = {}
                let tracks = startTracks;


                // ensure unnecessary whitespace in track list (gives spotify erors):
                var smushTracks = tracks.replace(/\s/g,'');
                var cleanTracks = smushTracks.replaceAll('spotify', ' spotify').trim();

                uriList['uris'] = cleanTracks.split(' ');
                jsonList = JSON.stringify(uriList);
                spotify.playTracks(res.data.client_token, window.device_id, jsonList);
              }, {
                once: true
              });
              document.getElementById("play-button").addEventListener("click", function() {
                window.player.togglePlay();
              });
            } else if (res.data.client_token !== null){
              this.$auth.clientToken = res.data.client_token;
              this.$auth.userid = res.data.user_id;
              this.$auth.appToken = res.data.app_token;
              this.$auth.knowledgeKey = res.data.knowledge_api;
              this.$auth.avatar = res.data.avatar;
              eventBus.$emit('notPremium');
            } else {
              this.$auth.appToken = res.data.app_token;
              this.$auth.knowledgeKey = res.data.knowledge_api;
              this.$view.banner = true;
            }
          }
        }).catch((error) => {
          alert('OTHER ERROR: ' + error);
          this.$auth.appToken = null;
          this.$auth.clientToken = null;
          console.error(error);
        });
      }
    },

  reInitializeSpotify() {
        // When spotify doesnt find track, it breaks device connection. Re-establish here
        window.player.disconnect()
        window.player.connect().then(success => {
        if (success) {
          console.log('The Web Playback SDK successfully connected to Spotify!');
        }
      })
    },

  refreshToken(){
        const path = 'api/get_token';
        axios.get(path, {withCredentials: true})
        .then((res) => {
          if (res.data.status == "success") {
            if (res.data.client_token !== null) {
              this.$auth.clientToken = res.data.client_token;
              this.$auth.appToken = res.data.app_token;
              this.$auth.knowledgeKey = res.data.knowledge_api;
            } else {
              this.$auth.appToken = res.data.app_token;
              this.$auth.knowledgeKey = res.data.knowledge_api;
            }
          }
        }).catch((error) => {
          this.$auth.appToken = null;
          this.$auth.clientToken = null;
          console.error(error);
        });
    },
    test(){
      console.log("TEST");
    }
  },
  mounted() { 
    this.initializeSpotify();

    //Timer for refreshing tokens
    setInterval(() => {
      this.refreshToken();
    }, 3300000);

    //Re-initialize Spotify player
    eventBus.$on('notAvailable', this.reInitializeSpotify);
  },
};
</script>
