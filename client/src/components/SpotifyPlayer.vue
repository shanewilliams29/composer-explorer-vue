<template>
  <div></div>
</template>

<script>
import {eventBus} from "../main.js";
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
                this.token = eventBus.spotifyToken; // Improve this?
            } else {
                this.token = 'BQDkKYCSEz7UAzL9wgaGkiGSTDAytAijGYLgb4omaHNWd4_TghEJXSccyt_INmDJS3o0VdD0PNGKkzJoNP2qR8CjIb36iG2oG9yEpBUH2YeDlUpQRKxDn6odDt-iCSiE13yNO9wDJfVn54QLplsb-C-Q6D2hEFsO0Wx1';
            }
            window.token = this.token;
            // eslint-disable-next-line
            this.player = new Spotify.Player({
                name: 'Composer Explorer',
                getOAuthToken: cb => { cb(this.token); },
                volume: 1
            });

            // Ready
            this.player.addListener('ready', ({ device_id }) => {
                this.device_id = device_id;
                window.device_id = device_id;
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
            });

            // document.getElementById('togglePlay').onclick = function() {
            //     console.log(window.token);
            //   this.player.togglePlay().then(() => {
            //       console.log('Toggled playback!');
            //     });
            // };
            this.player.connect();
        }
  },
};
</script>
