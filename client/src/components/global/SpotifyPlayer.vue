<template>
    <div></div>
</template>

<script>
import axios from "axios";
import { eventBus } from "@/main.js";
import { startTracks } from "@/main.js";
import { prepareTracksForSpotify } from "@/HelperFunctions.js";
import spotify from "@/SpotifyFunctions.js";

let spotifyPlayerScript = document.createElement("script");
spotifyPlayerScript.setAttribute("src", "https://sdk.scdn.co/spotify-player.js");
document.head.appendChild(spotifyPlayerScript);

// Listeners for Spotify playback functionality
function addPlaybackListeners(vm) {
    // Player ready
    window.player.addListener("ready", ({ device_id }) => {
        vm.$auth.deviceID = device_id;
        window.device_id = device_id;
        console.log("Ready with Device ID", device_id);
        vm.$view.showConnecting = false;
    });

    // Spotify error listeners.
    window.player.addListener("not_ready", ({ device_id }) => {
        console.log("Device ID has gone offline", device_id);
        vm.$view.showConnecting = false;
    });
    window.player.addListener("initialization_error", ({ message }) => {
        vm.$view.showConnecting = false;
        console.error(message);
    });
    window.player.addListener("authentication_error", ({ message }) => {
        vm.$view.showConnecting = false;
        console.error(message);
    });
    window.player.addListener("account_error", ({ message }) => {
        vm.$view.showConnecting = false;
        console.error(message);
    });
    window.player.addListener("playback_error", ({ message }) => {
        // Error due to no list loaded (happens if player clicks play button on the first startup). Send list of tracks to player.
        if (message == "Cannot perform operation; no list was loaded.") {
            let jsonTracks = prepareTracksForSpotify(startTracks)
            spotify.playTracks(vm.$auth.clientToken, vm.$auth.deviceID, jsonTracks);
        } else {
            console.error(message);
        }
    });
    window.player.addListener("autoplay_failed", () => {
        console.log("Autoplay is not allowed by the browser autoplay rules");
    });
    window.player.addListener("player_state_changed", ({ position, duration, paused, track_window: { current_track } }) => {
        // console.log("STATE CHANGE:", position, duration, paused)
        eventBus.$emit("firePlayerStateChanged", current_track, position, duration, paused);
    });

    // Function to handle connection loss
    function handleConnectionLoss() {
        console.log("Internet connection lost. Trying to reconnect...");
        // window.player.disconnect();
        vm.$view.showConnecting = true;
    }

    // Function to reconnect the player when the internet connection is restored
    function reconnectPlayer() {
        console.log("Found the internet!");
        window.player.connect().then((success) => {
            if (success) {
            console.log("Reconnected to Spotify!");
            } 
        });
    }

    // Add event listeners for connection status
    window.addEventListener('offline', handleConnectionLoss);
    window.addEventListener('online', reconnectPlayer);

}

export default {
    data() {
        return {
            firstLoad: true,
            reload: true,
        };
    },
    methods: {
        activatePlayer() {

            console.log("Player activated!");

            // eslint-disable-next-line
            window.player = new Spotify.Player({
                name: "Composer Explorer",
                getOAuthToken: (cb) => {
                    cb(this.$auth.clientToken);
                },
                volume: 1,
            });

            // Add Spotify playback listeners
            addPlaybackListeners(this);

            // Connect to Spotify player
            window.player.connect();

            // Listeners for playback buttons.
            document.getElementById("play-button").addEventListener("click", function() {
                window.player.resume();
            });
            document.getElementById("pause-button").addEventListener("click", function() {
                window.player.pause();
            });
            document.getElementById("back-button").addEventListener("click", function() {
                window.player.getCurrentState().then(state => {
                  if (state.position < 3000) {
                    window.player.previousTrack();
                  } else {
                    window.player.seek(0);
                  }
                });
            });
            document.getElementById("forward-button").addEventListener("click", function() {
                window.player.nextTrack();
            });

        //window.player.activateElement();
        //console.log("Playback activated!");
        // Remove the event listener after the first click
        document.getElementById("app").removeEventListener("click", this.activatePlayer);
    },
        initializeSpotify() {
            window.onSpotifyWebPlaybackSDKReady = () => {
                const path = "api/get_token";
                axios
                    .get(path, { withCredentials: true })
                    .then((res) => {
                        if (res.data.status == "success") {
                            // Premium member, activate Spotify player
                            if (res.data.client_token !== null && res.data.premium) {
                                this.$auth.clientToken = res.data.client_token;
                                this.$auth.appToken = res.data.app_token;
                                this.$auth.userid = res.data.user_id;
                                this.$auth.displayName = res.data.display_name;
                                this.$auth.patreon = res.data.patreon;
                                this.$auth.avatar = res.data.avatar;
                                this.$view.showConnecting = false;
                                // Add the event listener on app to activate Spotify Player on first click. In Safari 16.5, Spotify.Player() constructor must be in a click handler for autoplay restriction reasons.
                                document.getElementById("app").addEventListener("click", this.activatePlayer);

                                // Non-premium member, no activation of Spotify player
                            } else if (res.data.client_token !== null) {
                                this.$auth.clientToken = res.data.client_token;
                                this.$auth.userid = res.data.user_id;
                                this.$auth.appToken = res.data.app_token;
                                this.$auth.displayName = res.data.display_name;
                                this.$auth.avatar = res.data.avatar;
                                this.$auth.patreon = res.data.patreon;
                                this.$view.showConnecting = false;
                                eventBus.$emit("notPremium");

                                // User not logged in. Show welcome banner.
                            } else {
                                this.$auth.appToken = res.data.app_token;
                                this.$view.banner = true;
                                this.$view.showConnecting = false;
                                this.$auth.patreon = true;
                            }
                        }
                    })
                    .catch((error) => {
                        console.error(error);
                        this.$auth.appToken = null;
                        this.$auth.clientToken = null;
                        this.$auth.patreon = true;
                        this.$view.banner = true;
                        this.$view.showConnecting = false;
                    });
            };
        },
        reInitializeSpotify() {
            console.log("reInitializeSpotify?");
            // When spotify doesnt find album or track, it breaks device connection. Re-establish here.
            // console.log('RE-INITIALIZE');
            // window.player.disconnect();
            // setTimeout(() => {
            //     window.player.connect().then((success) => {
            //         if (success) {
            //             console.log("The Web Playback SDK successfully re-connected to Spotify!");
            //             window.player.resume();
            //         }
            //     });
            // }, 1000);
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
                        } else {
                            this.$auth.appToken = res.data.app_token;
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
        }, 1200000);

        //Re-initialize Spotify player
        eventBus.$on("notAvailable", this.reInitializeSpotify);
    },
};
</script>