import { eventBus } from "@/main.js";
import spotify from "@/SpotifyFunctions.js";
import PlaylistModal from "@/components/modals/PlaylistModal.vue";
import axios from "axios";

export const radioMixin = {
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
        eventBus.$emit("fireRandomWork");
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
    artistSearch(artist_name) {
    const path = "api/getperformerbyname?name=" + artist_name;
    axios
      .get(path)
      .then((res) => {
        const artist = res.data.artist;
        this.$config.artist = artist;
        eventBus.$emit("requestComposersForArtist", artist.id);
      })
      .catch((error) => {
        console.error(error);
      });
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
    this.$view.radioPlaying = false;
    this.$view.enableRadio = false;
    this.$view.enableExport = false;
    this.$view.favoritesAlbums = false;
    
    eventBus.$on("sendGenreListToRadio", this.makeGenreList);
  },
  mounted(){
    if (this.$route.query.artist) {
      this.radioTypeField = { value: "performer", text: "Performer Radio" }
    }
  },
  beforeCreate() {
    // Doesn't work reliably when coming from performers page or refreshing artist mode
    if (this.$route.query.artist) {
      const path = "api/getperformer?id=" + this.$route.query.artist;
      axios
        .get(path)
        .then((res) => {
          const artist = res.data.artist;
          this.$config.artist = artist;
          this.artistSelect = artist.name;
        })
        .catch((error) => {
          console.error(error);
        });
    } else {
      this.$config.artist = null;
    }
  },
  beforeDestroy() {
    eventBus.$off("sendGenreListToRadio", this.makeGenreList);
  },
};