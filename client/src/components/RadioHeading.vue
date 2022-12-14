<template>
  <div class="container-fluid">
    <b-row class="headings-row flex-nowrap">
      <b-col>
        <div>
          <b-form-group>
            <v-select v-model="radioTypeField" label="text" :options="radioTypeOptions" @input="radioTypeSelect()" :clearable="false" class="mt-3 style-chooser" :searchable="false"></v-select>
            <v-select
              multiple
              v-if="radioTypeField.value == 'composer'"
              v-model="composerSelectField"
              label="text"
              :options="composerOptions"
              @input="composerSelect()"
              placeholder="Select composers"
              :clearable="true"
              class="mt-3 style-chooser allow-wrap"
              :searchable="true"
            ></v-select>
            <v-select
              v-if="radioTypeField.value == 'period'"
              v-model="periodSelectField"
              label="text"
              :options="periodOptions"
              @input="periodSelect()"
              placeholder="Select period/era"
              :clearable="false"
              class="mt-3 style-chooser allow-wrap"
              :searchable="false"
            ></v-select>
            <vue-typeahead-bootstrap 
              v-if="radioTypeField.value == 'performer'" 
              v-model="query" 
              placeholder="Search for a performer" 
              class="mt-3 style-chooser performer-search" 
              @hit="artistSearch" 
              size="sm" 
              :data="this.artistList" />
          </b-form-group>
        </div>
      </b-col>
      <b-col>
        <b-form-group>
          <b-col class="col-no-padding-left">
            <v-select
              multiple
              v-model="genreSelectField"
              :deselectFromDropdown="false"
              :closeOnSelect="true"
              label="text"
              :options="genreOptions"
              @input="genreSelect()"
              placeholder="Select genres"
              :clearable="false"
              class="mt-3 style-chooser allow-wrap"
              :searchable="true"
            ></v-select>
          </b-col>
          <b-row class="sub-row flex-nowrap">
            <b-col class="col-padding-right">
              <b-form-input 
                class="work-search-field" 
                v-model="workSearchField" 
                v-debounce="workSearch" 
                placeholder="Search filter" 
                size="sm"></b-form-input>
            </b-col>
            <b-col class="col-padding-left">
              <v-select 
                v-model="workFilterField" 
                label="text" 
                :options="workOptions" 
                @input="genreSelect()" 
                :clearable="false" 
                class="mt-3 style-chooser" 
                :searchable="false"></v-select>
            </b-col>
          </b-row>
        </b-form-group>
      </b-col>
      <b-col class="last-col">
        <b-form-group>
          <b-row class="sub-row flex-nowrap">
            <b-col class="col-padding-right">
              <v-select 
                v-if="!$view.favoritesAlbums" 
                v-model="performerFilterField" 
                label="text" 
                :options="performerOptions" 
                @input="performerFilter()" 
                :clearable="false" 
                class="mt-3 style-chooser" 
                :searchable="false"></v-select>
            </b-col>
            <b-col class="col-padding-left">
              <v-select 
                v-if="!$view.favoritesAlbums" 
                v-model="limitFilterField" 
                label="text" 
                :options="limitOptions" 
                @input="limitFilter()" 
                :clearable="false" 
                class="mt-3 style-chooser" 
                :searchable="false"></v-select>
            </b-col>
          </b-row>
          <b-row class="sub-row flex-nowrap">
            <b-col cols="9" class="col-padding-right">
              <b-button class="radio-button-off" size="sm" v-if="!$view.radioPlaying && $view.enableRadio && $auth.clientToken" @click="toggleRadio()" block>Radio Off</b-button>
              <b-button class="radio-button-off-disabled" size="sm" v-if="!$view.radioPlaying && !$view.enableRadio || !$auth.clientToken" @click="toggleRadio()" disabled block>Radio Off</b-button>
              <b-button class="radio-button-on" size="sm" v-if="$view.radioPlaying && $auth.clientToken" @click="toggleRadio()" block variant="warning">Radio On</b-button>
            </b-col>
            <b-col cols="3" class="col-padding-left">
              <b-button v-if="$view.enableExport && $auth.clientToken" class="spotify-export-button" size="sm" @click="prepareForExport()" block variant="success">Export</b-button>
              <b-button v-else class="spotify-export-button-disabled" size="sm" block variant="success" disabled>Export</b-button>
            </b-col>
          </b-row>
        </b-form-group>
      </b-col>
    </b-row>
    <PlaylistModal @submit="exportSpotify"/>
  </div>
</template>


<script>
import axios from "axios";
import { eventBus } from "../main.js";
import spotify from "@/SpotifyFunctions.js";
import PlaylistModal from "./subcomponents/PlaylistModal.vue";

export default {
  components: {
    PlaylistModal,
  },
  data() {
    return {
      allowClear: true,
      artistList: [],
      query: null,
      title: "",
      OpenIndicator: {
        render: (createElement) => createElement("span", ""),
      },
      radioTypeField: { value: "composer", text: "Composer Radio" },
      radioTypeOptions: [
        { value: "composer", text: "Composer Radio" },
        { value: "period", text: "Period/Era Radio" },
        { value: "performer", text: "Performer Radio" },
        { value: "favorites", text: "Favorites Radio" },
      ],

      composerSelectField: null,
      composerOptions: [],

      periodSelectField: { value: "popular", text: "Most popular" },
      periodOptions: [
        // { value: "popular", text: "Most popular" },
        { value: "early", text: "Early" },
        { value: "baroque", text: "Baroque" },
        { value: "classical", text: "Classical" },
        { value: "romantic", text: "Romantic" },
        { value: "20th", text: "20th/21st Century" },
        // { value: "all", text: "All" },
      ],

      genreSelectField: [{ value: "all", text: "All Genres" }],
      genreOptions: [],

      workSearchField: "",

      workFilterField: { value: "recommended", text: "Recommended works" },
      workOptions: [
        { value: "recommended", text: "Recommended works" },
        { value: "obscure", text: "Less popular" },
        { value: "all", text: "All works" },
      ],

      performerFilterField: { value: "topartists", text: "Top performance" },
      performerOptions: [
        { value: "topartists", text: "Top performance" },
        { value: "randomartists", text: "Random performance" },
      ],

      limitFilterField: { value: "6", text: "Max no. of tracks: 6" },
      limitOptions: [
        { value: "1", text: "Max no. of tracks: 1" },
        { value: "2", text: "Max no. of tracks: 2" },
        { value: "3", text: "Max no. of tracks: 3" },
        { value: "4", text: "Max no. of tracks: 4" },
        { value: "5", text: "Max no. of tracks: 5" },
        { value: "6", text: "Max no. of tracks: 6" },
        { value: "10", text: "Max no. of tracks: 10" },
        { value: "100", text: "No track limit" },
      ],
    };
  },
  methods: {
    getArtistList() {
      const path = "api/artistlist";
      axios
        .get(path)
        .then((res) => {
          this.artistList = JSON.parse(res.data.artists);
        })
        .catch((error) => {
          console.error(error);
        });
    },
    toggleRadio() {
      if (this.$view.enableRadio) {
        this.$view.radioPlaying = !this.$view.radioPlaying;
      }
      if (this.$view.radioPlaying) {
        this.$view.shuffle = true;
        eventBus.$emit("fireNextWork");
      } else {
        spotify.pauseTrack(this.$auth.clientToken);
      }
    },
    radioTypeSelect() {
      // reset everything on radio type change
      this.$router.replace({ query: null });
      eventBus.$emit("fireRadioSelect", this.radioTypeField.value);
      eventBus.$emit("fireClearWorks");
      eventBus.$emit("fireClearAlbums");
      this.query = null;
      this.$config.artist = null;
      this.$config.genre = null;
      this.$view.radioPlaying = false;
      this.$view.enableRadio = false;
      this.$view.enableExport = false;
      this.composerSelectField = "";
      this.genreSelectField = [{ value: "all", text: "All Genres" }];
      this.workSearchField = "";
      this.workFilterField = { value: "recommended", text: "Recommended works" };
    },
    makeComposerDropdown(composers) {
      this.composerOptions = [];
      for (const composer of composers) {
        this.composerOptions.push({ value: composer, text: composer });
      }
    },
    composerSelect() {
      if (this.composerSelectField < 1) {
        this.$config.composer = null;
        this.radioTypeSelect(); // clears works and albums
      } else {
        eventBus.$emit("fireComposerSelectRadio", this.composerSelectField);
      }
    },
    makeGenreList(genreList) {
      if (genreList.length < 1) {
        this.genreSelectField = [{ value: "all", text: "All Genres" }];
        this.genreOptions = [];
      } else {
        this.genreOptions = [];
      }
      for (const genre of genreList) {
        this.genreOptions.push({ value: genre, text: genre });
      }
      eventBus.$emit("fireGenreSelectRadio", this.genreSelectField, this.workFilterField.value, this.workSearchField, this.query, this.radioTypeField.value);
    },
    periodSelect() {
      eventBus.$emit("fireComposerFilter", this.periodSelectField.value);
    },
    genreSelect() {
      if (this.genreSelectField.length > 1) {
        // removes All Genres from multiselect
        var newList = this.genreSelectField.filter((item) => item.value !== "all");
        this.genreSelectField = newList;
        this.allowClear = false;
      }
      if (this.genreSelectField.length < 1 && !this.allowClear) {
        // puts All Genres back into multiselect
        this.genreSelectField = [{ value: "all", text: "All Genres" }];
        this.allowClear = true;
      } else {
        this.allowClear = false;
      }
      eventBus.$emit("fireGenreSelectRadio", this.genreSelectField, this.workFilterField.value, this.workSearchField, this.query, this.radioTypeField.value);
    },
    workSearch() {
      eventBus.$emit("fireGenreSelectRadio", this.genreSelectField, this.workFilterField.value, this.workSearchField, this.query, this.radioTypeField.value);
    },
    limitFilter() {
      this.$view.radioTrackLimit = this.limitFilterField.value;
    },
    performerFilter() {
      if (this.performerFilterField.value == "randomartists") {
        this.$view.randomAlbum = true;
      } else {
        this.$view.randomAlbum = false;
      }
    },
    artistSearch(artist) {
      this.$config.artist = artist;
      eventBus.$emit("fireArtistComposers", artist);
    },
    prepareForExport() {
      eventBus.$emit("firePlaylistExport", this.query, this.radioTypeField.value, this.genreSelectField, this.workFilterField.value, this.workSearchField, this.limitFilterField.value, true, "dummyname");
      this.$view.playlistError = false;
      this.$view.playlistSuccess = false;
    },
    exportSpotify(name) {
      eventBus.$emit("firePlaylistExport", this.query, this.radioTypeField.value, this.genreSelectField, this.workFilterField.value, this.workSearchField, this.limitFilterField.value, false, name);
    },
  },
  created() {
    this.getArtistList();
    this.$config.genre = null;
    if (this.$route.query.artist) {
      this.$config.artist = this.$route.query.artist;
    } else {
      this.$config.artist = null;
    }
    this.$view.radioPlaying = false;
    this.$view.enableRadio = false;
    this.$view.enableExport = false;
    eventBus.$on("fireComposerListToRadio", this.makeComposerDropdown);
    eventBus.$on("fireRadioGenreList", this.makeGenreList);
  },
  mounted() {
    if (this.$route.query.artist) {
      this.radioTypeField = { value: "performer", text: "Performer Radio" };
      this.query = this.$route.query.artist;
      eventBus.$emit("fireRadioSelect", "performer");
    } else {
      eventBus.$emit("fireRadioSelect", "composer");
    }
  },
  beforeDestroy() {
    eventBus.$off("fireComposerListToRadio", this.makeComposerDropdown);
    eventBus.$off("fireRadioGenreList", this.makeGenreList);
  },
};
</script>

<style scoped>
.container-fluid{
  background-color: #54595f;
  color: #3b4047;
}
.form-group{
  margin-bottom: 5px;
}
.last-col{
  padding-right: 5px !important;
}
.card-body{
  background: none !important;
}
.card {
  background: none;
  border: none;
}
.heading-card {
  padding-top: 0px;
  padding-bottom: 5px;
  padding-left: 5px;
}
.radio-button-off{
  margin-top: 5px;
  border: 1px solid var(--yellow) !important;
  background-color: #805d07 !important;
  height: 31px;
}
.radio-button-off-disabled{
  margin-top: 5px;
  border: 1px solid darkgoldenrod !important;
  background-color: #54595f !important;
  height: 31px;
}
.radio-button-off:hover{
  margin-top: 5px;
  border: 1px solid var(--yellow) !important;
  background-color: darkgoldenrod !important;
  height: 31px;
}
.radio-button-on{
  margin-top: 5px;
  border: 1px solid var(--yellow) !important;
  background-color: var(--yellow) !important;
  height: 31px;
}
.spotify-export-button{
  margin-top: 5px;
  height: 31px;
  background-color: var(--green) !important;
  border: 1px solid var(--green) !important;
}
.spotify-export-button-disabled{
  margin-top: 5px;
  height: 31px;
  background-color: #54595f !important;
  border: 1px solid var(--green) !important;
}
.spotify-export-button:hover{
  background-color: #3daf57 !important;
  border: 1px solid var(--green) !important;
}
.form-row {
  margin-bottom: 0px;
}
.lead {
  font-weight: 500;
  font-size: 14px;
  margin: 0px;
  padding-left: 10px;
  padding-bottom: 1px;
}
.col {
  padding: 0px;
  padding-left: 5px;
}
.style-chooser{
  margin-top: 5px !important;
  font-size: 14px !important;
  fill: white;
}
>>> .vs__selected-options{
  flex-wrap: nowrap;
}
>>> .vs__selected{
  white-space:nowrap;
  overflow: hidden;
}
.allow-wrap >>> .vs__selected-options{
  flex-wrap: wrap !important;
}
input{
  font-size: 14px !important;
}
>>> {
  --vs-font-size: 14px;
  --vs-controls-color: #fff;
  --vs-border-color: #3b4047;
  --vs-border-width: 1px;
  --vs-selected-bg: #3b4047;
  --vs-selected-color: #fff;
  --vs-search-input-color: #fff;
}
.performer-search{
  margin-top: 5px !important;
  font-size: 14px;
  background-color: #3b4047 !important;
  height: 31px;
  border: none;
  border-radius: 4px;
}
.sub-row{
  margin: 0px;
}
.work-search-field{
  margin-top: 5px;
  height: 31px;
  border: 1px solid #343a40 !important;
}
.col-padding-right{
  padding-left: 0px;
  padding-right: 2.5px;
}
.col-padding-left{
  padding-left: 2.5px;
  padding-right: 0px;
}
.col-no-padding-left{
  padding-left: 0px;
}
</style>
