<template>
  <div class="container-fluid">
    <b-row>
      <b-col>
      </b-col>
      <b-col>
      </b-col>
      <b-col class="last-col">
        <b-card class="heading-card albums-card">
          <b-form-group>
              <v-select
                v-model="albumFilterField"
                label="text"
                :options="albumOptions"
                @input="albumFilter()"
                :inputId="albumFilterField"
                :clearable="false"
                :autoscroll="false"
                :components="{OpenIndicator}"
                class="mt-3 performer-search"
              ></v-select>
              <v-select
                v-model="albumSortField"
                label="text"
                :options="albumSortOptions"
                @input="albumSort()"
                :inputId="AlbumSortField"
                :clearable="false"
                class="mt-3 style-chooser"
                :searchable="false"
              ></v-select>
          </b-form-group>
        </b-card>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import axios from 'axios';
import {eventBus} from "../main.js";
import {currentConfig} from "../main.js";

export default {
  data() {
    return {
      artist_list: [],
      title: "",
      OpenIndicator: {
          render: createElement => createElement('span',''),
        },

      composerFilterForm: { value: 'popular', text: 'Most popular' },
      composerSearchForm: null,
      composerOptions: [
              { value: 'popular', text: 'Most popular' },
              { value: 'early', text: 'Early' },
              { value: 'baroque', text: 'Baroque' },
              { value: 'classical', text: 'Classical' },
              { value: 'romantic', text: 'Romantic' },
              { value: '20th', text: '20th/21st Century' },
              { value: 'all', text: 'All - by region' },
              { value: 'alphabet', text: 'All - alphabetically' }
            ],

      workFilterField: { value: 'recommended', text: 'Recommended works' },
      workSearchField: null,
      workSearchPlaceholder: "Search works by " + currentConfig.composer,
      workOptions: [
          { value: 'recommended', text: 'Recommended works' },
          { value: 'all', text: 'All works'}
        ],

      albumFilterField: { value: 'allartists', text: 'All performers of ' + '"' + currentConfig.workTitle+ '"'},
      albumOptions: [],

      albumSortField: { value: 'recommended', text: 'Recommended sorting' },
      albumSortOptions: [
          { value: 'recommended', text: 'Recommended sorting' },
          { value: 'dateascending', text: 'Sort by date, earliest to latest' },
          { value: 'datedescending', text: 'Sort by date, latest to earliest' }
        ],
    };
  },
  methods: {
    composerFilter() {
      console.log(this.composerFilterForm.value);
      eventBus.$emit('fireComposerFilter', this.composerFilterForm.value);
      this.composerSearchForm = '';
      //console.log(this.composerFilterForm);
    },
    composerSearch() {
      eventBus.$emit('fireComposerSearch', this.composerSearchForm);
      this.composerFilterForm = 'Search results for "' + this.composerSearchForm + '"';
      //console.log(this.composerSearchForm);
    },
    onComposerFocus() {
      this.composerFilterForm = { value: 'popular', text: 'Most popular' };
      this.composerSearchForm = '';
      eventBus.$emit('fireComposerSearch', '');
    },
    workFilter() {
      eventBus.$emit('fireWorkFilter', this.workFilterField.value);
      this.workSearchField = '';
      //console.log(this.workFilterField);
    },
    workSearch() {
      eventBus.$emit('fireWorkSearch', this.workSearchField);
      this.workFilterField = 'Search results for "' + this.workSearchField + '"';
      //console.log(this.workSearchField);
    },
    onWorkFocus() {
      this.workFilterField = { value: 'recommended', text: 'Recommended works' }
      this.workSearchField = '';
      eventBus.$emit('fireWorkSearch', '');
    },
    albumFilter() {
      this.albumSearchPlaceholder = "Search performers";
      if (this.albumFilterField.value == "allartists") {
          eventBus.$emit('fireAlbumFilter', currentConfig.work, '');
      } else {
          eventBus.$emit('fireAlbumFilter', currentConfig.work, this.albumFilterField.value);
          this.albumSearchField = '';
    }
      //console.log(this.workFilterField);
    },
    albumSearch() {
      eventBus.$emit('fireAlbumSearch', currentConfig.work, this.albumSearchField);
      this.albumSearchPlaceholder = this.albumSearchField;
      this.albumSearchField = '';
      this.albumFilterField = null;
      //console.log(this.workSearchField);
    },
    onAlbumFocus() {
      this.$refs.typeahead.inputValue = ''
      eventBus.$emit('fireAlbumSearch', currentConfig.work, '');
    },
    getArtistList() {
      const path = 'api/artistlist';
      axios.get(path)
        .then((res) => {
          // this.artist_list = ['Canada', 'United States', 'Mexico'];
          this.artist_list = JSON.parse(res.data.artists);
          //console.log(this.artist_list);
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    }
  },
  created() {
    this.title = currentConfig.workTitle;
    eventBus.$on('fireComposers', (composer) => {
        this.workSearchPlaceholder = "Search works by " + composer;
        this.workSearchField = '';
        this.workFilterField = { value: 'recommended', text: 'Recommended works' };
    })
    eventBus.$on('fireAlbums', (work_id, title) => { // is this used?
      console.log(title);
        this.title = title;
        this.album_heading = "Albums for \"" + title + "\"";
        this.albumFilterField = { value: 'allartists', text: 'All performers of ' + '"' + this.title + '"'};
    })
    eventBus.$on('fireArtistList', (artistList) => {
        this.artist_list = []
        this.albumSearchPlaceholder = "Search performers of " + this.title;
        this.albumOptions = [
          { value: 'allartists', text: 'All performers of ' + '"' + this.title + '"'}
        ];
        for (var key in artistList) {
          this.albumOptions.push({ value: key, text: key });
          this.artist_list.push(key);
        }
    })
  },
};
</script>

<style>
.form-control{
  background-color: #3b4047 !important;
  border: none !important;
  color: white !important;
}
::-webkit-input-placeholder { /* Chrome/Opera/Safari */
  color: #9ea4ae !important;
}
::-moz-placeholder { /* Firefox 19+ */
  color: #9ea4ae !important;
}
:-ms-input-placeholder { /* IE 10+ */
  color: #9ea4ae !important;
}
:-moz-placeholder { /* Firefox 18- */
  color: #9ea4ae !important;
}
</style>

<style scoped>
.container-fluid{
  background-color: #54595f;
  color: #3b4047;
}
.last-col{
  padding-right: 5px !important;
}
.albums-card{
  padding-top: 3.5px !important;
}
.card-body{
  background: none !important;
  height: 74.5px;
}
.card {
  background: none;
  border: none;
}
.heading-card {
  padding-top: 5px;
  padding-bottom: 0px;
  padding-left: 5px;
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
}
.style-chooser{
  margin-top: 5px !important;
  font-size: 14px;
  fill: white;
}
>>> {
  --vs-controls-color: #fff;
  --vs-border-color: #3b4047;
  --vs-border-width: 1px;
  --vs-selected-bg: #3b4047;
  --vs-selected-color: #fff;
  --vs-line-height: 1;
  --vs-search-input-color: #fff;
}
.performer-search{
  margin-top: 1.3px !important;
  font-size: 14px;
  background-color: #3b4047 !important;
  height: 31px;
  border: none;
  border-radius: 4px;
}

/*.custom-select{

  border: solid 1px #3b4047;
  color: white;
    background: url("data:image/svg+xml,<svg height='10px' width='10px' viewBox='0 0 16 16' fill='white' xmlns='http://www.w3.org/2000/svg'><path d='M7.247 11.14 2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z'/></svg>") no-repeat;
    background-position: calc(100% - 0.75rem) center !important;
    -moz-appearance:none !important;
    -webkit-appearance: none !important;
    appearance: none !important;
    padding-right: 2rem !important;
}*/

</style>
