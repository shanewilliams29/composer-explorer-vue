import { eventBus } from "@/main.js";

export const albumsMixin = {
  data() {
    return {
      allowClear: {
        artist: false,
        work: false
      },
      clearInputActive: false,

      fieldData: {
        composer: null,
        period: null,
        artist: null,
        work: null,
        sort: "popular",
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
        { value: "early", text: "Early" },
        { value: "baroque", text: "Baroque" },
        { value: "classical", text: "Classical" },
        { value: "romantic", text: "Romantic" },
        { value: "20th", text: "20th/21st Century" },
      ],

      artistSelectField: null,
      workSelectField: null,

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
      return this.fieldData.composer || this.fieldData.period || this.fieldData.artist || this.fieldData.work;
    },
  },
  watch: {
    gotComposerList() {
      this.makeComposerDropdown(this.$lists.composerList);
    },
    inputsMade(bool) {
      this.clearInputActive = bool;
    }
  },
  methods: {
    clearArtistInputOnFocus() {
      let value = this.artistSelectField
      if (value && this.allowClear.artist) {
        this.artistSelectField = null;
        this.resetArtistField();
      } else if (value && !this.allowClear.artist) {
        this.allowClear.artist = true;
      }
    },
    clearWorkInputOnFocus() {
      let value = this.workSelectField
      if (value && this.allowClear.work) {
        this.workSelectField = null;
        this.resetWorkField();
      } else if (value && !this.allowClear.work) {
        this.allowClear.work = true;
      }
    },
    clearInputs() {
      this.composerSelectField = null;
      this.periodSelectField = null;
      this.artistSelectField = null;
      this.workSelectField = null;
      this.albumSortField = { value: "popular", text: "Most popular" };
      this.fieldData.composer = null;
      this.fieldData.period = null;
      this.fieldData.artist = null;
      this.fieldData.work = null;
      this.fieldData.sort = this.albumSortField.value
      eventBus.$emit("requestAlbumViewAlbums", this.fieldData);
    },
    filterFieldSelect() {
      // clear fields on selection of filter type
      this.composerSelectField = null;
      this.periodSelectField = null;
    },
    makeComposerDropdown(composers) {
      this.composerOptions = [];
      for (const composer of composers) {
        this.composerOptions.push({ value: composer, text: composer });
      }
    },
    composerSelect() {
      this.fieldData.composer = null;
      this.fieldData.period = null;
      if (this.composerSelectField) {
        this.fieldData.composer = this.composerSelectField.value;
      }
      // reset works field as well upon composer change
      this.workSelectField = null;
      this.fieldData.work = null;
      eventBus.$emit("requestAlbumViewAlbums", this.fieldData);
    },
    periodSelect() {
      this.fieldData.composer = null;
      this.fieldData.period = null;
      if (this.periodSelectField) {
        this.fieldData.period = this.periodSelectField.value
      }
      // reset works field as well upon period change
      this.workSelectField = null;
      this.fieldData.work = null;
      eventBus.$emit("requestAlbumViewAlbums", this.fieldData);
    },
    workSearch(work) {
      this.fieldData.work = work;
      eventBus.$emit("requestAlbumViewAlbums", this.fieldData);
    },
    artistSearch(artist) {
      this.fieldData.artist = artist;
      eventBus.$emit("requestAlbumViewAlbums", this.fieldData);
    },
    resetArtistField(input) {
      this.allowClear.artist = false;
      if (!input) {
        this.fieldData.artist = null;
        eventBus.$emit("requestAlbumViewAlbums", this.fieldData);
      }
    },
    resetWorkField(input) {
      this.allowClear.work = false;
      if (!input) {
        this.fieldData.work = null;
        eventBus.$emit("requestAlbumViewAlbums", this.fieldData);
      }
    },
    albumSortSelect() {
      this.fieldData.sort = this.albumSortField.value
      eventBus.$emit("requestAlbumViewAlbums", this.fieldData);
    }
  },
  created() {
    if (this.$lists.composerList.length > 0) {
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