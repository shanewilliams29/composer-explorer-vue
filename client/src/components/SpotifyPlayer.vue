<template>
  <div></div>
</template>

<script>
// import {eventBus} from "../main.js";
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
            this.token = 'BQCMAl1uHbYfngac_C5InuKBiyl0g4enH8ePPSJGqzBtH0SOe1aI6QrsL6eupOYaZZtjw8cQcAg_xy9wzcu_dDxSVXW-h4iMoxwygZAYJDaeAtCw8D7nx4GG_7_bIhaKDcZpR0CBEnduth1SzC1e9yWee3PBrXJZn4By';
            //this.token = eventBus.spotifyToken;
            window.token = this.token;
            // eslint-disable-next-line
            this.player = new Spotify.Player({
                name: 'ComposerExplorer',
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
