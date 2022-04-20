<template>
  <div></div>
</template>

<script>
import {eventBus} from "../main.js";
import {spotifyConfig} from "../main.js";

export default {
  data() {
    return {
      token: "",
      player: ""
    };
  },
  methods: {
  },
  mounted() {
    let spotifyPlayerScript = document.createElement('script');
    spotifyPlayerScript.setAttribute('src', 'https://sdk.scdn.co/spotify-player.js');
    document.head.appendChild(spotifyPlayerScript);

        window.onSpotifyWebPlaybackSDKReady = () => {
            if (process.env.VUE_APP_BASE_URL != "http://localhost:5000/") {
                this.token = spotifyConfig.clientToken; // Need this?
            } else {
                this.token = 'BQCmXK-SHmi3KReRo1ajwXhxn6TdidTnduzAx69AFysuy_BXlaVsuarqV4PSyKnO4zXlQRvGqBr0j3s6T0xMQ4G3ej5qAf689Ae2NQzDxYoyeLx7pH_U49xpKkgOmdKDm3ehG4Jld6D8wP2ZON1G0FlowM-dFpmLM7BS6MFCoKzXV-14K9U3L4ekDGVrxeeBdXxm5gg1xI2KbX_B_QTMoHU';
                spotifyConfig.clientToken = this.token;
            }

        if(this.token){
            // eslint-disable-next-line
            this.player = new Spotify.Player({
                name: 'Composer Explorer',
                getOAuthToken: cb => { cb(this.token); },
                volume: 1
            });

            // Ready
            this.player.addListener('ready', ({ device_id }) => {
                this.device_id = device_id;
                spotifyConfig.deviceID = device_id;
                console.log('Ready with Device ID', device_id);
            });

            // Not Ready
            this.player.addListener('not_ready', ({ device_id }) => {
                console.log('Device ID has gone offline', device_id);
            });

            this.player.addListener('initialization_error', ({ message }) => {
                console.error(message);
            });

            this.player.addListener('authentication_error', ({ message }) => {
                console.error(message);
            });

            this.player.addListener('account_error', ({ message }) => {
                console.error(message);
            });

            this.player.addListener('autoplay_failed', () => {
              console.log('Autoplay is not allowed by the browser autoplay rules');
              eventBus.$emit('fireAutoplayFailed');
            });

            this.player.addListener('player_state_changed', ({
              position,
              duration,
              paused,
              track_window: { current_track }
            }) => {
                eventBus.$emit('firePlayerStateChanged', current_track, position, duration, paused);
                //console.log('Position in Song', position);
                //console.log('Duration of Song', duration);
            });

            // document.getElementById('togglePlay').onclick = function() {
            //     console.log(window.token);
            //   this.player.togglePlay().then(() => {
            //       console.log('Toggled playback!');
            //     });
            // };
            this.player.connect();
            }
        }
  },
};
</script>
