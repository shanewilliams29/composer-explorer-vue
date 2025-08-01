<template>
  <div>
    <b-modal id="playlist-modal" @show="resetForm" hide-footer>
      <template #modal-title>
        <img :src="spotifyLogoURL" alt="Spotify" height="32px" />
      </template>
      <div class="m-2 text-center">
        <h4>Export this radio as a Spotify playlist</h4>
        <div>&nbsp;</div>
        <b-spinner v-if="spinnerShow && !$view.playlistSuccess && !$view.playlistError" label="Large Spinner"></b-spinner>
        <div v-if="$view.playlistError" style="color: darkred;">
          Sorry, we encounted the following error:<br />
          "{{$view.playlistError}}".<br />
          <b-button class="mt-4" @click="$bvModal.hide('playlist-modal')">Close</b-button>
        </div>
        <div v-if="$view.playlistSuccess" style="color: darkgreen;">
          Success! Tracks added to playlist "{{form.name}}".<br />
          <b-button class="mt-4" @click="$bvModal.hide('playlist-modal')">Close</b-button>
        </div>

        <b-form @submit.prevent="onSubmit" v-if="formShow && !$view.playlistError">
          <div v-if="$view.playlistTrackCount">{{ $view.playlistTrackCount}} tracks will be added</div>
          <div v-else><b-spinner small label="Small Spinner"></b-spinner> Preparing tracks...</div>
          <b-form-group id="input-group">
            <b-form-input id="form-input" v-model="form.name" placeholder="Enter new playlist name" required></b-form-input>
          </b-form-group>
          <b-button v-if="$view.playlistTrackCount" type="submit" variant="success" class="mt-4">Export to Spotify</b-button>
        </b-form>
      </div>
    </b-modal>
  </div>
</template>

<script>
import { staticURL } from "@/main.js";

export default {
  data() {
    return {
      form: {
        name: "",
      },
      formShow: true,
      spinnerShow: false,
      spotifyLogoURL: staticURL + "/assets/Spotify_Logo_RGB_Black.png",
    };
  },
  methods: {
    onSubmit() {
      this.$emit('submit', this.form.name)
      this.formShow = false;
      this.spinnerShow = true;
    },
    resetForm() {
      this.formShow = true;
      this.spinnerShow = false;
      this.form.name = "";
      this.$view.playlistTrackCount = null;
    },
  },
};
</script>

<style scoped>
.mt-4{
  margin: 2px;
}
#input-group{
  margin-top: 10px;
}
input{
  color: #000 !important;
  background-color: var(--light-gray) !important;
}
</style>
