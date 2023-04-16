import { eventBus } from "@/main.js";
import PlaylistModal from "@/components/modals/PlaylistModal.vue";

export const radioMixin = {
  components: {
    PlaylistModal,
  },
  data() {
    return {
      allowClear: true,
      artistSelect: null,
      title: "",
      artist: null,
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

      albumFilter: { value: "popular", text: "Most popular" },
      albumFilterOptions: [
        { value: "popular", text: "Most popular" },
        { value: "newest", text: "New releases" },
        { value: "oldest", text: "Historical recordings" },
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
        eventBus.$emit("requestAlbumViewAlbums", this.composerSelectField.value, this.periodSelectField, this.artist);
    },
    periodSelect() {
      if (this.periodSelectField) {
        eventBus.$emit("requestAlbumViewAlbums", this.composerSelectField.value, this.periodSelectField, this.artist);
      }
    },
    // workSearch() {
    //   eventBus.$emit("requestWorksForRadio", this.genreSelectField, this.workFilterField.value, this.workSearchField, this.artistSelect, this.radioTypeField.value);
    // },
    artistSearch(artist) {
      this.artist = artist;
      let composer = null;
      if (this.composerSelectField) {
        composer = this.composerSelectField.value
      }
      eventBus.$emit("requestAlbumViewAlbums", composer, this.periodSelectField, artist);
    },
  },
  created() {
    if(this.$lists.composerList.length > 0){
      this.makeComposerDropdown(this.$lists.composerList);
    }
  },
  mounted() {
  },
  beforeDestroy() {
  },
};