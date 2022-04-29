<template>
  <div></div>
</template>

<script>
import axios from 'axios';
import {eventBus} from "../main.js";
import {spotifyConfig} from "../main.js";

let spotifyPlayerScript = document.createElement('script');
spotifyPlayerScript.setAttribute('src', 'https://sdk.scdn.co/spotify-player.js');
document.head.appendChild(spotifyPlayerScript);

export default {
  data() {
    return {
    };
  },

  methods: {
    initializeSpotify() {
        window.onSpotifyWebPlaybackSDKReady = () => {

            const path = 'api/get_token';
            axios.get(path, { withCredentials: true })
                .then((res) => {
                    if (res.data.status == "success") {
                        if (res.data.client_token !== null) {
                            spotifyConfig.clientToken = res.data.client_token;
                            spotifyConfig.appToken = res.data.app_token;
                            eventBus.$emit('fireLogIn');


                            // eslint-disable-next-line
                            window.player = new Spotify.Player({
                                name: 'Composer Explorer',
                                getOAuthToken: cb => { cb(spotifyConfig.clientToken); },
                                volume: 1
                            });

                            // Ready
                            window.player.addListener('ready', ({ device_id }) => {
                                this.device_id = device_id;
                                spotifyConfig.deviceID = device_id;
                                console.log('Ready with Device ID', device_id);
                            });

                            // Not Ready
                            window.player.addListener('not_ready', ({ device_id }) => {
                                console.log('Device ID has gone offline', device_id);
                            });

                            window.player.addListener('initialization_error', ({ message }) => {
                                console.error(message);
                            });

                            window.player.addListener('authentication_error', ({ message }) => {
                                console.error(message);
                            });

                            window.player.addListener('account_error', ({ message }) => {
                                console.error(message);
                            });

                            window.player.addListener('playback_error', ({ message }) => {
                                console.error(message);
                            });

                            window.player.addListener('autoplay_failed', () => {
                              console.log('Autoplay is not allowed by the browser autoplay rules');
                              eventBus.$emit('fireAutoplayFailed');
                            });

                            window.player.addListener('player_state_changed', ({
                              position,
                              duration,
                              paused,
                              track_window: { current_track }
                            }) => {
                                eventBus.$emit('firePlayerStateChanged', current_track, position, duration, paused);
                                //console.log(position , duration, paused);
                                //console.log('Duration of Song', duration);
                            });

                            window.player.connect();

                            // for Safari autoplay enable
                            document.getElementById("app").addEventListener("click", function() {
                                console.log("ACTIVATED");
                                window.player.activateElement();
                            }, { once: true });

                        } else {
                            spotifyConfig.appToken = res.data.app_token;
                      }
                    }
                  })
              .catch((error) => {
                spotifyConfig.appToken = null;
                spotifyConfig.clientToken = null;
                console.error(error);
      });
    }
  },
},
    mounted() {
    this.initializeSpotify();
    },
};
</script>
