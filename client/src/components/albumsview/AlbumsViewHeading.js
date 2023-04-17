import { eventBus } from "@/main.js";

export const albumsMixin = {
  data() {
    return {
      allowClear: false,
      artistSelect: null,
      title: "",
      composer: null,
      period: null,
      artist: null,
      sort: 'popular',

      OpenIndicator: {
        render: (createElement) => createElement("span", ""),
      },
      filterField: { value: "composer", text: "Filter by composer" },
      filterFieldOptions: [
        { value: "composer", text: "Filter by composer" },
        { value: "period", text: "Filter by period/era" },
      ],

      composerSelectField: null,
      composerOptions: [],

      periodSelectField: null,
      periodOptions: [
        // { value: "popular", text: "Most popular" },
        { value: "all", text: "All" },
        { value: "early", text: "Early" },
        { value: "baroque", text: "Baroque" },
        { value: "classical", text: "Classical" },
        { value: "romantic", text: "Romantic" },
        { value: "20th", text: "20th/21st Century" },
        // { value: "all", text: "All" },
      ],

      albumSortField: { value: "popular", text: "Most popular" },
      albumSortOptions: [
        { value: "popular", text: "Most popular" },
        { value: "newest", text: "Newest releases" },
        { value: "oldest", text: "Older recordings" },
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
    clearInputOnFocus() {
      let value = this.artistSelect
      if (value && this.allowClear) {
        console.log("CLEAR INPUT");
        this.artistSelect = '';
        this.resetArtistField();
      } else if (value && !this.allowClear) {
        console.log("BLOCK CLEAR");
        this.allowClear = true;
      } else {
        console.log("DO NOTHING");
      }
    },
    filterFieldSelect(){
      this.composerSelectField = null;
      this.periodSelectField = null;
    },
    makeComposerDropdown(composers) {
      this.composerOptions = [];
      this.composerOptions.push({ value: "all", text: "All composers" });
      for (const composer of composers) {
        this.composerOptions.push({ value: composer, text: composer });
      }
    },
    composerSelect() {
      this.composer = null;
      this.period = null;
      if (this.composerSelectField) {
        this.composer = this.composerSelectField.value
      }
      eventBus.$emit("requestAlbumViewAlbums", this.composer, this.period, this.artist, this.sort);
    },
    periodSelect() {
      this.composer = null;
      this.period = null;
      if (this.periodSelectField) {
        this.period = this.periodSelectField.value
      }
      eventBus.$emit("requestAlbumViewAlbums", this.composer, this.period, this.artist, this.sort);
    },
    // workSearch() {
    //   eventBus.$emit("requestWorksForRadio", this.genreSelectField, this.workFilterField.value, this.workSearchField, this.artistSelect, this.radioTypeField.value);
    // },
    artistSearch(artist) {
      this.artist = artist;
      eventBus.$emit("requestAlbumViewAlbums", this.composer, this.period, this.artist, this.sort);
    },
    resetArtistField(input){
      this.allowClear = false;
      if (!input) {
        this.artist = null;
        eventBus.$emit("requestAlbumViewAlbums", this.composer, this.period, this.artist, this.sort);
      }
    },
    albumSortSelect(){
      this.sort = this.albumSortField.value
      eventBus.$emit("requestAlbumViewAlbums", this.composer, this.period, this.artist, this.sort);
    }
  },
  created() {
    if(this.$lists.composerList.length > 0){
      this.makeComposerDropdown(this.$lists.composerList);
    }
  },
  mounted() {
    const inputElement = this.$refs.typeahead.$el.querySelector('input');
    inputElement.addEventListener('focus', this.clearInputOnFocus);
  },
  beforeDestroy() {
    const inputElement = this.$refs.typeahead.$el.querySelector('input');
    inputElement.removeEventListener('focus', this.clearInputOnFocus);
  },
};