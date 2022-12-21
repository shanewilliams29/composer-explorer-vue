<template>
  <div class="container-fluid">
    <b-row class="headings-row flex-nowrap">
      <b-col class="last-col">
        <div>
          <b-form-group>
            <v-select v-model="radioTypeField" label="text" :options="radioTypeOptions" @input="radioTypeSelect()" :clearable="false" class="mt-3 selector" :searchable="false"></v-select>
            <v-select
              multiple
              v-if="radioTypeField.value == 'composer'"
              v-model="composerSelectField"
              label="text"
              :options="composerOptions"
              @input="composerSelect()"
              placeholder="Select composers"
              :clearable="true"
              class="mt-3 selector allow-wrap"
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
              class="mt-3 selector allow-wrap"
              :searchable="false"
            ></v-select>
            <v-select
              v-if="radioTypeField.value == 'favorites'"
              placeholder="No futher options for favorites radio"
              class="mt-3 selector allow-wrap"
              disabled
            ></v-select>
            <vue-typeahead-bootstrap v-if="radioTypeField.value == 'performer'" v-model="artistSelect" placeholder="Search for a performer" class="mt-3 selector performer-search" @hit="artistSearch" size="sm" :data="$lists.artistList" />
          </b-form-group>
        </div>
      </b-col>
    </b-row>
    <b-row class="headings-row flex-nowrap">
      <b-col class="last-col">
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
              class="mt-3 selector allow-wrap"
              :searchable="true"
            ></v-select>
          </b-col>
          <b-row class="sub-row flex-nowrap">
            <b-col class="col-padding-right" v-show="false">
              <b-form-input 
                class="work-search-field" 
                v-model="workSearchField" 
                v-debounce="workSearch" 
                placeholder="Search filter" 
                size="sm"></b-form-input>
            </b-col>
            <b-col class="col-no-padding-left">
              <v-select 
                v-model="workFilterField" 
                label="text" 
                :options="workOptions" 
                @input="genreSelect()" 
                :clearable="false" 
                class="mt-3 selector" 
                :searchable="false"></v-select>
            </b-col>
          </b-row>
        </b-form-group>
      </b-col>
    </b-row>
    <b-row class="headings-row flex-nowrap">
      <b-col class="last-col">
        <b-form-group>
          <b-row class="sub-row flex-nowrap" v-show="false">
            <b-col class="col-padding-right">
              <v-select 
                v-if="!$view.favoritesAlbums" 
                v-model="performanceFilterField" 
                label="text" 
                :options="performanceOptions" 
                @input="performanceFilter()" 
                :clearable="false" 
                class="mt-3 selector" 
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
                class="mt-3 selector" 
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
    <PlaylistModal />
  </div>
</template>


<script>
import { eventBus } from "@/main.js";
import spotify from "@/SpotifyFunctions.js";
import PlaylistModal from "@/components/modals/PlaylistModal.vue";

export default {
  components: {
    PlaylistModal,
  },
  data() {
    return {
      allowClear: true,
      artistSelect: null,
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

      periodSelectField: null,
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

      performanceFilterField: { value: "topartists", text: "Top performance" },
      performanceOptions: [
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
  computed: {
    gotComposerList() {
      return this.$lists.composerList;
    },
  },
  watch: {
    gotComposerList() {
      this.makeComposerDropdown(this.$lists.composerList);
    },
  },
  methods: {
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
      this.$view.favoritesAlbums = false;

      if(this.radioTypeField.value == 'favorites'){
        this.$view.favoritesAlbums = true;
        eventBus.$emit("requestFavoritesComposers");
      }

      eventBus.$emit("clearComposersList");
      eventBus.$emit("clearWorksList");
      eventBus.$emit("clearAlbumsList");

      // reset everything on radio type change
      if (this.$route.query.artist){
        this.$router.replace({ query: null });
      }
      this.artistSelect = null;
      this.$config.artist = null;
      this.$config.genre = null;
      this.$view.radioPlaying = false;
      this.$view.enableRadio = false;
      this.$view.enableExport = false;
      this.composerSelectField = "";
      this.genreSelectField = [{ value: "all", text: "All Genres" }];
      this.genreOptions =[];
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
        this.$config.composer = '';
        this.radioTypeSelect(); // resets everything
      } else {
        eventBus.$emit("requestComposersFromRadioMultiselect", this.composerSelectField);
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
      eventBus.$emit("requestWorksForRadio", this.genreSelectField, this.workFilterField.value, this.workSearchField, this.artistSelect, this.radioTypeField.value);
    },
    periodSelect() {
      if (this.periodSelectField) {
        eventBus.$emit("requestComposersFromFilter", this.periodSelectField.value);
      }
    },
    genreSelect() {
      if (this.genreSelectField.length > 1) {
        // removes All Genres from multiselect upon genre selection
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
      eventBus.$emit("requestWorksForRadio", this.genreSelectField, this.workFilterField.value, this.workSearchField, this.artistSelect, this.radioTypeField.value);
    },
    workSearch() {
      eventBus.$emit("requestWorksForRadio", this.genreSelectField, this.workFilterField.value, this.workSearchField, this.artistSelect, this.radioTypeField.value);
    },
    limitFilter() {
      this.$view.radioTrackLimit = this.limitFilterField.value;
    },
    performanceFilter() {
      if (this.performanceFilterField.value == "randomartists") {
        this.$view.randomAlbum = true;
      } else {
        this.$view.randomAlbum = false;
      }
    },
    artistSearch(artist) {
      this.$config.artist = artist;
      eventBus.$emit("requestComposersForArtist", artist);
    },
    prepareForExport() {
      eventBus.$emit("firePlaylistExport", this.artistSelect, this.radioTypeField.value, this.genreSelectField, this.workFilterField.value, this.workSearchField, this.limitFilterField.value, true, "dummyname");
      this.$view.playlistError = false;
      this.$view.playlistSuccess = false;
    },
    exportSpotify(name) {
      eventBus.$emit("firePlaylistExport", this.artistSelect, this.radioTypeField.value, this.genreSelectField, this.workFilterField.value, this.workSearchField, this.limitFilterField.value, false, name);
    },
  },
  created() {
    if(this.$lists.composerList.length > 0){
      this.makeComposerDropdown(this.$lists.composerList);
    }
    this.$config.genre = null;
    if (this.$route.query.artist) {
      this.$config.artist = this.$route.query.artist;
    } else {
      this.$config.artist = null;
    }
    this.$view.radioPlaying = false;
    this.$view.enableRadio = false;
    this.$view.enableExport = false;
    this.$view.favoritesAlbums = false;
    
    eventBus.$on("sendGenreListToRadio", this.makeGenreList);
  },
  mounted() {
    if (this.$route.query.artist) {
      this.radioTypeField = { value: "performer", text: "Performer Radio" };
      this.artistSelect = this.$route.query.artist;
    }
  },
  beforeDestroy() {
    eventBus.$off("sendGenreListToRadio", this.makeGenreList);
  },
};
</script>

<style scoped>
/*NOTE: Text sizes overriden in MobileRadio.vue */
.container-fluid{
  background-color: var(--medium-gray);
  color: var(--search-gray);
}
.form-group{
  margin-bottom: 5px;
}
.last-col{
  padding-right: 5px !important;
}
.card-body{
  background: none !important;
/*  height: 73px;*/
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
  background-color: var(--medium-gray) !important;
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
  background-color: var(--medium-gray) !important;
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
.selector{
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
  --vs-search-input-bg: none;
  --vs-font-size: 14px;
  --vs-controls-color: var(--my-white);
  --vs-border-color: var(--search-gray);
  --vs-border-width: 1px;
  --vs-selected-bg: var(--search-gray);
  --vs-selected-color: var(--my-white);
  --vs-search-input-color: var(--my-white);
}
>>> {
    --vs-disabled-bg: none;
}

.performer-search{
  margin-top: 5px !important;
  font-size: 14px;
  background-color: var(--search-gray) !important;
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
  border: 1px solid var(--dark-gray) !important;
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
