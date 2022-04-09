<template>
  <div></div>
</template>

<script>
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
            this.token = 'BQAG-OUH4ILhlzFOd-c-wVBRgRaL5_eTNBLTKvKV9V-Y8LguBglcTDkDxdFhXX7CNDEinUMk4nxUpbggv0bAPMODgRIzr_PKCykm34ywc96k_q7ycYxr5fuNYqe8lWoSlN1ArdyWuGlqoxrrFL_ECwqoQUHnbn5x6ZB_';
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
