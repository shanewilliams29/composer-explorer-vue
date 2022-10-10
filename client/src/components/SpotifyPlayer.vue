<template>
  <div></div>
</template>

<script>
import axios from "axios";
import { eventBus } from "@/main.js";
import { startTracks } from "@/main.js";
import spotify from "@/SpotifyFunctions.js";

let spotifyPlayerScript = document.createElement("script");
spotifyPlayerScript.setAttribute("src", "https://sdk.scdn.co/spotify-player.js");
document.head.appendChild(spotifyPlayerScript);

export default {
  data() {
    return {
      firstLoad: true,
      reload: true,
    };
  },
  methods: {
    initializeSpotify() {
      window.onSpotifyWebPlaybackSDKReady = () => {
        const path = "api/get_token";
        axios
          .get(path, { withCredentials: true })
          .then((res) => {
            if (res.data.status == "success") {
              if (res.data.client_token !== null && res.data.premium) {
                this.$auth.clientToken = res.data.client_token;
                this.$auth.appToken = res.data.app_token;
                this.$auth.userid = res.data.user_id;
                this.$auth.patreon = res.data.patreon;
                this.$auth.knowledgeKey = res.data.knowledge_api;
                this.$auth.avatar = res.data.avatar;
                // eslint-disable-next-line
                window.player = new Spotify.Player({
                  name: "Composer Explorer",
                  getOAuthToken: (cb) => {
                    cb(this.$auth.clientToken);
                  },
                  volume: 1,
                });
                // Ready
                window.player.addListener("ready", ({ device_id }) => {
                  this.device_id = device_id;
                  this.$auth.deviceID = device_id;
                  window.device_id = device_id;
                  console.log("Ready with Device ID", device_id);
                  this.$view.showConnecting = false;

                  // THESE STEPS ARE NECESSARY BECAUSE SPOTIFY BREAKS CONNECTION WHEN TRACK NOT AVAILABLE
                  // FIRST LOAD OF PLAYER
                  if (this.firstLoad) {
                    window.player.activateElement();
                    this.firstLoad = false;

                    // RELOAD TRACKS IF ERROR AND TRY AGAIN (WEBVIEW GLITCH)
                  } else if (this.reload) {
                    let uriList = {};
                    let jsonList = {};
                    let tracks = this.$config.playTracks;
                    var smushTracks = tracks.replace(/\s/g, "");
                    var cleanTracks = smushTracks.replaceAll("spotify", " spotify").trim();
                    uriList["uris"] = cleanTracks.split(" ");
                    jsonList = JSON.stringify(uriList);
                    spotify.playTracks(this.$auth.clientToken, this.device_id, jsonList);
                    this.reload = false;
                  } else {
                    // NEXT ALBUM IF ERROR PERSISTS (Spotify Album not found, 404)
                    eventBus.$emit("fireNextAlbum");
                    console.log("NEXT ALBUM");
                    eventBus.$emit("fireNotFoundModal");
                    this.reload = true;
                  }
                });
                // Not Ready
                window.player.addListener("not_ready", ({ device_id }) => {
                  console.log("Device ID has gone offline", device_id);
                  this.$view.showConnecting = false;
                });
                window.player.addListener("initialization_error", ({ message }) => {
                  this.$view.showConnecting = false;
                  console.error(message);
                });
                window.player.addListener("authentication_error", ({ message }) => {
                  this.$view.showConnecting = false;
                  console.error(message);
                });
                window.player.addListener("account_error", ({ message }) => {
                  this.$view.showConnecting = false;
                  console.error(message);
                });
                window.player.addListener("playback_error", ({ message }) => {
                  console.error(message);

                  // Error due to no list loaded. Send list of tracks to player.
                  let uriList = {};
                  let jsonList = {};
                  let tracks = startTracks;
                  // ensure no unnecessary whitespace in track list (gives spotify erors):
                  var smushTracks = tracks.replace(/\s/g, "");
                  var cleanTracks = smushTracks.replaceAll("spotify", " spotify").trim();

                  uriList["uris"] = cleanTracks.split(" ");
                  jsonList = JSON.stringify(uriList);
                  spotify.playTracks(res.data.client_token, window.device_id, jsonList);
                });

                window.player.addListener("autoplay_failed", () => {
                  console.log("Autoplay is not allowed by the browser autoplay rules");
                });
                window.player.addListener("player_state_changed", ({ position, duration, paused, track_window: { current_track } }) => {
                  eventBus.$emit("firePlayerStateChanged", current_track, position, duration, paused);
                });
                window.player.connect();

                // For initial startup and playback
                document.getElementById("play-button").addEventListener("click", function () {
                  window.player.activateElement();
                  window.player.togglePlay();
                });

              } else if (res.data.client_token !== null) {
                this.$auth.clientToken = res.data.client_token;
                this.$auth.userid = res.data.user_id;
                this.$auth.appToken = res.data.app_token;
                this.$auth.knowledgeKey = res.data.knowledge_api;
                this.$auth.avatar = res.data.avatar;
                this.$auth.patreon = res.data.patreon;
                eventBus.$emit("notPremium");
                this.$view.showConnecting = false;
              } else {
                this.$auth.appToken = res.data.app_token;
                this.$auth.knowledgeKey = res.data.knowledge_api;
                this.$view.banner = true;
                this.$view.showConnecting = false;
                this.$auth.patreon = true;
              }
            }
          })
          .catch((error) => {
            this.$auth.appToken = null;
            this.$auth.clientToken = null;
            this.$auth.patreon = true;
            console.error(error);
            this.$view.showConnecting = false;
          });
      };
    },

    reInitializeSpotify() {
      // When spotify doesnt find track, it breaks device connection. Re-establish here
      window.player.disconnect();
      setTimeout(() => {
        window.player.connect().then((success) => {
          if (success) {
            console.log("The Web Playback SDK successfully connected to Spotify!");
          }
        });
      }, 1000);
    },
    refreshToken() {
      const path = "api/get_token";
      axios
        .get(path, { withCredentials: true })
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
        })
        .catch((error) => {
          this.$auth.appToken = null;
          this.$auth.clientToken = null;
          console.error(error);
        });
    },
  },
  mounted() {
    this.initializeSpotify();

    document.getElementById("play-button").addEventListener("click", () => {
      if (!this.$auth.clientToken || this.$auth.clientToken == "INVALID") {
        // Investigate why returning INVALID in app, should be null.
        eventBus.$emit("notLoggedIn");
      }
    });

    //Timer for refreshing tokens
    setInterval(() => {
      this.refreshToken();
    }, 3300000);

    //Re-initialize Spotify player
    eventBus.$on("notAvailable", this.reInitializeSpotify);
  },
};
</script>
