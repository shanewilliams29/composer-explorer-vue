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
                this.token = 'BQA-wfIhhqVFmulPTrFHAhN9UJ-rMUvzhCZolLFu0pWVG9sfs3pSRCChYGzAM9xGJS5ZqEMnBVfrbmj_OrOGytO0dy_cI0Kt3O0EYT00cHCXKLQTBgLycU6T1G_yEyUrSSh146uPAzVcrpavOaPVbRDPH2rweNawM-okZgNxGLG9vgJRi8VYeA7P5pbOmlF1TJUi71F7k14ZZPaoRMmnr9g';
            }
            window.token = this.token;
            this.token = eventBus.spotifyToken;

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

            this.player.addListener('player_state_changed', ({
              position,
              duration,
              paused,
              track_window: { current_track }
            }) => {
                eventBus.$emit('firePlayerStateChanged', current_track, position, duration, paused);
                //console.log('Currently Playing', current_track.name);
                console.log('Position in Song', position);
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
