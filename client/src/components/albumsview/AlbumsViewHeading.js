import { eventBus } from "@/main.js";

export const albumsMixin = {
  data() {
    return {
      allowArtistClear: false,
      allowWorkClear: false,
      artistSelect: null,
      workSelect: null,
      title: "",
      composer: null,
      period: null,
      artist: null,
      work: null,
      sort: 'popular',
      clearInputActive: false,

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
    inputsMade() {
      return this.composer || this.period || this.artist || this.work;
    },
  },
  watch: {
    gotComposerList() {
      this.makeComposerDropdown(this.$lists.composerList);
    },
    inputsMade(bool){
      this.clearInputActive = bool;
    }
  },
  methods: {
    clearArtistInputOnFocus() {
      let value = this.artistSelect
      if (value && this.allowArtistClear) {
        console.log("CLEAR INPUT");
        this.artistSelect = '';
        this.resetArtistField();
      } else if (value && !this.allowArtistClear) {
        console.log("BLOCK CLEAR");
        this.allowArtistClear = true;
      } else {
        console.log("DO NOTHING");
      }
    },
    clearWorkInputOnFocus() {
      let value = this.workSelect
      if (value && this.allowWorkClear) {
        console.log("CLEAR INPUT");
        this.workSelect = '';
        this.resetWorkField();
      } else if (value && !this.allowWorkClear) {
        console.log("BLOCK CLEAR");
        this.allowWorkClear = true;
      } else {
        console.log("DO NOTHING");
      }
    },
    clearInputs(){
      this.composerSelectField = null;
      this.periodSelectField = null;
      this.composer = null;
      this.period = null;
      this.artistSelect = '';
      this.workSelect = '';
      this.resetArtistField();
      this.resetWorkField();
      this.albumSortField.value = 'popular';
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
        this.composer = this.composerSelectField.value;
      }
      // reset works field as well
      this.workSelect = '';
      this.work = null;
      eventBus.$emit("requestAlbumViewAlbums", this.composer, this.period, this.artist, this.work, this.sort);
    },
    periodSelect() {
      this.composer = null;
      this.period = null;
      if (this.periodSelectField) {
        this.period = this.periodSelectField.value
      }
      // reset works field as well
      this.workSelect = '';
      this.work = null;
      eventBus.$emit("requestAlbumViewAlbums", this.composer, this.period, this.artist, this.work, this.sort);
    },
    workSearch(work) {
      this.work = work;
      eventBus.$emit("requestAlbumViewAlbums", this.composer, this.period, this.artist, this.work, this.sort);
    },
    artistSearch(artist) {
      this.artist = artist;
      eventBus.$emit("requestAlbumViewAlbums", this.composer, this.period, this.artist, this.work, this.sort);
    },
    resetArtistField(input){
      this.allowArtistClear = false;
      if (!input) {
        this.artist = null;
        eventBus.$emit("requestAlbumViewAlbums", this.composer, this.period, this.artist, this.work, this.sort);
      }
    },
    resetWorkField(input){
      this.allowWorkClear = false;
      if (!input) {
        this.work = null;
        eventBus.$emit("requestAlbumViewAlbums", this.composer, this.period, this.artist, this.work, this.sort);
      }
    },
    albumSortSelect(){
      this.sort = this.albumSortField.value
      eventBus.$emit("requestAlbumViewAlbums", this.composer, this.period, this.artist, this.work, this.sort);
    }
  },
  created() {
    if(this.$lists.composerList.length > 0){
      this.makeComposerDropdown(this.$lists.composerList);
    }
  },
  mounted() {
    const inputArtistElement = this.$refs.artistTypeahead.$el.querySelector('input');
    inputArtistElement.addEventListener('focus', this.clearArtistInputOnFocus);

    const inputWorkElement = this.$refs.workTypeahead.$el.querySelector('input');
    inputWorkElement.addEventListener('focus', this.clearWorkInputOnFocus);    
  },
  beforeDestroy() {
    const inputArtistElement = this.$refs.artistTypeahead.$el.querySelector('input');
    inputArtistElement.removeEventListener('focus', this.clearArtistInputOnFocus);

    const inputWorkElement = this.$refs.workTypeahead.$el.querySelector('input');
    inputWorkElement.removeEventListener('focus', this.clearWorkInputOnFocus);
  },
};