<template>
  <div v-if="$view.mode != 'favorites'" class="container-fluid">
    <b-row class="flex-nowrap">
      <b-col>
        <ComposerHeading />
      </b-col>
      <b-col>
        <b-card class="heading-card work-card">
          <b-form-group>
            <b-form-input v-model="workSearchField" v-debounce="workSearch" type="text" @focus="onWorkFocus()" :placeholder="workSearchPlaceholder" size="sm"></b-form-input>
            <v-select v-model="workFilterField" label="text" :options="workOptions" @input="workFilter()" :clearable="false" class="mt-3 style-chooser" :searchable="false"></v-select>
          </b-form-group>
        </b-card>
      </b-col>
      <b-col class="last-col">
        <b-card class="heading-card albums-card">
          <b-form-group>
            <v-select v-model="albumFilterField" label="text" :options="albumOptions" @input="albumFilter()" :clearable="false" :autoscroll="false" :components="{OpenIndicator}" class="mt-3 performer-search"></v-select>
            <b-row class="flex-nowrap">
              <b-col style="padding-right: 0px;" cols="8">
                <v-select v-model="albumSortField" label="text" :options="albumSortOptions" @input="albumFilter()" :clearable="false" class="mt-3 style-chooser" :searchable="false"></v-select>
              </b-col>
              <b-col style="padding-left: 5px;" cols="4">
                <v-select v-model="albumSizeField" label="text" :options="albumSizeOptions" @input="albumSize()" :clearable="false" class="mt-3 style-chooser" :searchable="false"></v-select>
              </b-col>
            </b-row>
          </b-form-group>
        </b-card>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import ComposerHeading from '@/components/subcomponents/ComposerHeading.vue'
import {eventBus} from "../main.js";

export default {
  name: 'ColumnHeadings',
  components: {
    ComposerHeading
  },
  data() {
    return {
      artist_list: [],
      title: "",
      OpenIndicator: {
          render: createElement => createElement('span',''),
        },

      workFilterField: { value: 'recommended', text: 'Recommended works' },
      workSearchField: null,
      workSearchPlaceholder: "Search works by " + this.$config.composer,
      workOptions: [
          { value: 'recommended', text: 'Recommended works' },
          { value: 'all', text: 'All works'}
        ],

      albumFilterField: { value: 'allartists', text: 'All performers'},
      albumOptions: [],

      albumSortField: { value: 'recommended', text: 'Recommended sorting' },
      albumSortOptions: [
          { value: 'recommended', text: 'Recommended sorting' },
          { value: 'dateascending', text: 'Sort by date, earliest to latest' },
          { value: 'datedescending', text: 'Sort by date, latest to earliest' }
        ],
      albumSizeField: { value: this.$config.albumSize, text: this.capitalize(this.$config.albumSize)},
      albumSizeOptions: [
          { value: 'large', text: 'Large' },
          { value: 'small', text: 'Small' }
        ],
    };
  },
  methods: {
    capitalize(string){
      let capitalized = string[0].toUpperCase() + string.substring(1);
      return capitalized;
    },
    workFilter() {
      eventBus.$emit('fireWorkFilter', this.workFilterField.value);
      this.workSearchField = '';
    },
    workSearch() {
      eventBus.$emit('fireWorkSearch', this.workSearchField);
      if(this.workSearchField != ''){
        this.workFilterField = 'Search results for "' + this.workSearchField + '"';
      } else {
        this.workFilterField = { value: 'recommended', text: 'Recommended works' };
      }
    },
    onWorkFocus() {
      this.workFilterField = { value: 'recommended', text: 'Recommended works' }
      this.workSearchField = '';
      eventBus.$emit('fireWorkSearch', '');
    },
    albumFilter() {
      if (this.albumFilterField.value == "allartists") {
          eventBus.$emit('fireAlbums', this.$config.work, '', this.albumSortField.value);
      } else {
          eventBus.$emit('fireAlbums', this.$config.work, this.albumFilterField.value, this.albumSortField.value);
      }
    },
    albumSize() {
      if (this.albumSizeField.value == "large") {
        this.$config.albumSize = 'large';
        localStorage.setItem('config', JSON.stringify(this.$config));
      } else {
        this.$config.albumSize = 'small';
        localStorage.setItem('config', JSON.stringify(this.$config));
      }
    },
    newComposer(composer) {
        this.workSearchPlaceholder = "Search works by " + composer;
        this.workSearchField = '';
        this.workFilterField = { value: 'recommended', text: 'Recommended works' };
    },
    newWork() {
        this.albumFilterField = { value: 'allartists', text: 'All performers'};
        this.albumSortField = { value: 'recommended', text: 'Recommended sorting' }
    },
    createArtistList(artistList){
        this.artist_list = []
        this.albumOptions = [{ value: 'allartists', text: 'All performers'}];
        for (var key in artistList) {
          this.albumOptions.push({ value: key, text: key });
          this.artist_list.push(key);
        }
    },
  },
  created() {
    this.title = this.$config.workTitle;
    eventBus.$on('fireComposers', this.newComposer);
    eventBus.$on('changeWork', this.newWork);
    eventBus.$on('fireArtistList', this.createArtistList);
  },
  beforeDestroy() {
    eventBus.$off('fireComposers', this.newComposer);
    eventBus.$off('changeWork', this.newWork);
    eventBus.$off('fireArtistList', this.createArtistList);
  },
};
</script>

<style>
.form-control {
  background-color: #3b4047 !important;
  border: none !important;
  color: white !important;
}
.heading-card {
  padding-top: 5px;
  padding-bottom: 0px;
  padding-left: 5px;
}
::-webkit-input-placeholder {
  /* Chrome/Opera/Safari */
  color: #9ea4ae !important;
}
::-moz-placeholder {
  /* Firefox 19+ */
  color: #9ea4ae !important;
}
:-ms-input-placeholder {
  /* IE 10+ */
  color: #9ea4ae !important;
}
:-moz-placeholder {
  /* Firefox 18- */
  color: #9ea4ae !important;
}
</style>
<style scoped>
.container-fluid {
  background-color: #54595f;
  color: #3b4047;
}
.last-col {
  margin-right: 5px;
}
.albums-card {
  padding-top: 3.5px !important;
}
.card-body {
  background: none !important;
  height: 73px;
}
.card {
  background: none;
  border: none;
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
.style-chooser {
  margin-top: 5px !important;
  font-size: 14px;
  fill: white;
}
>>> .vs__selected-options{
  flex-wrap: nowrap;
}
>>> .vs__selected{
  white-space:nowrap;
  overflow: hidden;
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
.performer-search {
  margin-top: 1.3px !important;
  font-size: 14px;
  background-color: #3b4047 !important;
  height: 31px;
  border: none;
  border-radius: 4px;
}
</style>
