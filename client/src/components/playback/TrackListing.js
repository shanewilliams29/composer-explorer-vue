import { eventBus } from "@/main.js";
import spotify from "@/SpotifyFunctions.js";

export const trackMixin = {
    data() {
        return {
            album: [],
            selectedTrack: "Track",
            selectedTrackNo: "",
            numTracks: "",
            genre: "",
        };
    },
    methods: {
        strFix(item) {
            let fixed = item.replace(/[^A-Z0-9]+/gi, "");
            return fixed;
        },
        trackMatch(track) {
            // match on IDs
            if (this.selectedTrack[1] == track[1]) {
                return true;

                //match on name if IDs are not valid (Spotify redirected track for licensing purposes)
            } else if (this.strFix(this.selectedTrack[0]) == this.strFix(track[0])) {
                return true;
            } else {
                return false;
            }
        },
        playTracks(tracks, progress) {
            let uriList = {};
            let jsonList = {};
            let selectedTrack = tracks.split(" ")[0];
            let allTracks = this.$config.allTracks.split(" ");

            let index = allTracks.indexOf(selectedTrack);
            this.$view.trackIndex = index;
            let previousTracks = "";

            if (index == 0) {
                previousTracks = this.$config.allTracks;
            } else {
                for (var i = index - 1; i < allTracks.length; i++) {
                    previousTracks = previousTracks + " " + allTracks[i];
                }
            }
            this.$config.previousTracks = previousTracks.trim();
            this.$config.playTracks = tracks;
            localStorage.setItem("config", JSON.stringify(this.$config));

            // ensure no unnecessary whitespace in track list (gives spotify erors):
            let smushTracks = tracks.replace(/\s/g, "");
            let cleanTracks = smushTracks.replaceAll("spotify", " spotify").trim();

            uriList["uris"] = cleanTracks.split(" ");
            uriList["position_ms"] = progress;
            jsonList = JSON.stringify(uriList);
            spotify.playTracks(this.$auth.clientToken, this.$auth.deviceID, jsonList);
        },
    },
    created() {
        // eslint-disable-next-line
        eventBus.$on("firePlayerStateChanged", (track_data, position, duration, paused) => {
            let track = [];
            track[1] = track_data["id"];
            track[0] = track_data["name"];
            this.selectTrack(track);
        });
    },
};