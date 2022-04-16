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
                this.token = 'BQAoq93p8JTHdxegT5r6isa9pC-FAq9oxVtujcoX2tW38deLY1_Xpgh9cMqhpiZUjEkdmHRnW2QTyY4yUN01JDGtYZ_XErku8Ij0PJVl0OWAORu8wd_wkeYEDnFpC0hZXp5zqXvr41kW944hTVGne7wW_4WOi4gomyeh0CYd6VCOF8-uQODm-1DiBr21ZQCBU3qcW_OYXsXkV9MpZF4aMxc';
            }
            window.token = this.token;

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
                eventBus.$emit('firePlayerReady');
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
                //console.log('Currently Playing', current_track.name);
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
