<template>
  <div class="container-fluid">
    <b-row>
      <b-col>
        <div>
          <b-card class="heading-card composer-card">
            <b-form-group>
              <v-select
                v-model="radioTypeField"
                label="text"
                :options="radioTypeOptions"
                @input="radioTypeSelect()"
                :clearable="false"
                class="mt-3 style-chooser"
                :searchable="false"
              ></v-select>
              <v-select multiple
                v-model="composerSelectField"
                label="text"
                :options="composerOptions"
                @input="composerSelect()"
                placeholder="Select composers"
                :clearable="true"
                class="mt-3 style-chooser"
                :searchable="true"
              ></v-select>
            </b-form-group>
          </b-card>
        </div>
      </b-col>
      <b-col>
        <b-card class="heading-card work-card">
            <b-form-group>
              <b-col col=12>
              <v-select multiple
                v-model="genreSelectField"
                :deselectFromDropdown="false"
                :closeOnSelect="true"
                label="text"
                :options="genreOptions"
                @input="genreSelect()"
                placeholder="Select genres"
                :clearable="true"
                class="mt-3 style-chooser"
                :searchable="true"
              ></v-select>
            </b-col>
            <b-row class="sub-row">
            <b-col col=6 class="col-padding-right">
              <b-form-input
                class="work-search-field"
                v-model="workSearchField"
                v-debounce="workSearch"
                @focus="onWorkFocus()"
                placeholder="Search filter"
                size="sm"
              ></b-form-input>
            </b-col>
              <b-col col=6 class="col-padding-left">
                <v-select
                v-model="workFilterField"
                label="text"
                :options="workOptions"
                @input="genreSelect()"
                :clearable="false"
                class="mt-3 style-chooser"
                :searchable="false"
              ></v-select>
            </b-col>
          </b-row>
            </b-form-group>
        </b-card>
      </b-col>
      <b-col class="last-col">
        <b-card class="heading-card albums-card">
          <b-form-group>
            <b-row class="sub-row">
            <b-col col=6 class="col-padding-right">
                <v-select
                v-model="performerFilterField"
                label="text"
                :options="performerOptions"
                @input="performerFilter()"
                :clearable="false"
                class="mt-3 style-chooser"
                :searchable="false"
              ></v-select>
            </b-col>
            <b-col col=6 class="col-padding-left">
              <v-select
                v-model="limitFilterField"
                label="text"
                :options="limitOptions"
                @input="limitFilter()"
                :clearable="false"
                class="mt-3 style-chooser"
                :searchable="false"
              ></v-select>
            </b-col>
          </b-row>
              <b-button class="radio-button" size="sm" v-if="!$view.radioPlaying" @click="toggleRadio()" block variant="">Radio Off</b-button>
              <b-button class="radio-button" size="sm" v-if="$view.radioPlaying" @click="toggleRadio()" block variant="warning">Radio On</b-button>
          </b-form-group>
        </b-card>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import {eventBus} from "../main.js";
import spotify from '@/SpotifyFunctions.js'

export default {
  data() {
    return {
      artist_list: [],
      title: "",
      OpenIndicator: {
          render: createElement => createElement('span',''),
      },
      radioTypeField: { value: 'composer', text: 'Composer Radio' },
      radioTypeOptions: [
          { value: 'composer', text: 'Composer Radio' },
          { value: 'period', text: 'Period/Era Radio'},
          { value: 'performer', text: 'Performer Radio'},
          { value: 'favorites', text: 'Favorites Radio'}
        ],

      composerSelectField: null,
      composerOptions: [],

      genreSelectField: null,
      genreOptions: [],

      workSearchField: '',

      workFilterField: { value: 'recommended', text: 'Recommended works' },
      workOptions: [
          { value: 'recommended', text: 'Recommended works' },
          { value: 'obscure', text: 'Less popular'},
          { value: 'all', text: 'All works'}
        ],

      performerFilterField: { value: 'topartists', text: 'Top performance' },
      performerOptions: [
          { value: 'topartists', text: 'Top performance' },
          { value: 'randomartists', text: 'Random performers'}
        ],

      limitFilterField: { value: '4', text: 'Max # of tracks: 4' },
      limitOptions: [
          { value: '1', text: 'Max # of tracks: 1' },
          { value: '2', text: 'Max # of tracks: 2' },
          { value: '3', text: 'Max # of tracks: 3' },
          { value: '4', text: 'Max # of tracks: 4' },
          { value: '5', text: 'Max # of tracks: 5' },
          { value: '6', text: 'Max # of tracks: 6' },
          { value: '10', text: 'Max # of tracks: 10' },
          { value: '100', text: 'No track limit' },
        ],
    };
  },
  methods: {
    toggleRadio(){
      if(this.$view.enableRadio){
        this.$view.radioPlaying = !this.$view.radioPlaying;
      }
      if (this.$view.radioPlaying){
        this.$view.shuffle = true;
        eventBus.$emit('fireNextWork');
      } else {
        spotify.pauseTrack(this.$auth.clientToken);
      }
    },
    radioTypeSelect(){
      eventBus.$emit('fireRadioSelect', this.radioTypeField.value);
    },
    makeComposerDropdown(composers){
        this.composerOptions = [];
        for (const composer of composers) {
          this.composerOptions.push({ value: composer, text: composer });
        }
    },
    composerSelect(){
        eventBus.$emit('fireComposerSelectRadio', this.composerSelectField);
        console.log(this.composerSelectField);
    },
    makeGenreList(genreList){
        if(genreList.length < 1){
          this.genreSelectField = [];
          this.genreOptions = [];
        } else {
          this.genreOptions = [];
          this.genreOptions.push({ value: 'all', text: 'All Genres' });
        }
        eventBus.$emit('fireGenreSelectRadio', this.genreSelectField, this.workFilterField.value, this.workSearchField);
        for (const genre of genreList) {
          this.genreOptions.push({ value: genre, text: genre });
        }
    },
    genreSelect(){
        eventBus.$emit('fireGenreSelectRadio', this.genreSelectField, this.workFilterField.value, this.workSearchField);
    },
    workSearch() {
      eventBus.$emit('fireGenreSelectRadio', this.genreSelectField, this.workFilterField.value, this.workSearchField);
    },
    onWorkFocus() {
      this.workSearchField = '';
      eventBus.$emit('fireGenreSelectRadio', this.genreSelectField, this.workFilterField.value, this.workSearchField);
    },
    limitFilter() {
      this.$view.radioTrackLimit = this.limitFilterField.value;
      console.log(this.$view.radioTrackLimit);
    },
      performerFilter(){
        if(this.performerFilterField.value == 'randomartists'){
          this.$view.randomAlbum = true;
        } else {
          this.$view.randomAlbum = false;
        }
    },
  },
  created() {
    this.$view.radioPlaying = false;
    this.$view.enableRadio = false;
    eventBus.$on('fireComposerListToRadio', this.makeComposerDropdown);
    eventBus.$on('fireRadioGenreList', this.makeGenreList);
    eventBus.$on('fireComposerSelectRadio', this.makeGenreList);
  },
  mounted(){
    eventBus.$emit('fireRadioSelect', 'composer');
  }
};
</script>

<style scoped>
.container-fluid{
  background-color: #54595f;
  color: #3b4047;
}
.last-col{
  padding-right: 5px !important;
}
.card-body{
  background: none !important;
  height: 73px;
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
.radio-button{
  margin-top: 5px;
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
  font-size: 14px !important;
  fill: white;
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
  margin-top: 1.3px !important;
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
  height: 28.6px;
}
.col-padding-right{
  padding-right: 2.5px;
}
.col-padding-left{
  padding-left: 2.5px;
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
