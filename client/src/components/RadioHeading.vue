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
                :inputId="radioTypeField"
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
                :inputId="composerSelectField"
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
              <v-select multiple
                v-model="genreSelectField"
                :deselectFromDropdown="false"
                :closeOnSelect="true"
                label="text"
                :options="genreOptions"
                @input="genreSelect()"
                :inputId="genreSelectField"
                placeholder="Select genres"
                :clearable="true"
                class="mt-3 style-chooser"
                :searchable="true"
              ></v-select>
                <v-select
                v-model="workFilterField"
                label="text"
                :options="workOptions"
                @input="genreSelect()"
                :inputId="workFilterField"
                :clearable="false"
                class="mt-3 style-chooser"
                :searchable="false"
              ></v-select>
            </b-form-group>
        </b-card>
      </b-col>
      <b-col class="last-col">
        <b-card class="heading-card albums-card">
          <b-form-group>
                <v-select
                v-model="performerFilterField"
                label="text"
                :options="performerOptions"
                @input="performerFilter()"
                :inputId="performerFilterField"
                :clearable="false"
                class="mt-3 style-chooser"
                :searchable="false"
              ></v-select>
              <b-button class="radio-button" size="sm" v-if="RadioOff" @click="toggleRadio()" block variant="">Radio Off</b-button>
              <b-button class="radio-button" size="sm" v-if="!RadioOff" @click="toggleRadio()" block variant="warning">Radio On</b-button>
          </b-form-group>
        </b-card>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import {eventBus} from "../main.js";

export default {
  data() {
    return {
      RadioOff: true,
      artist_list: [],
      title: "",
      OpenIndicator: {
          render: createElement => createElement('span',''),
      },
      radioTypeField: { value: 'composer', text: 'Composer Radio' },
      radioTypeOptions: [
          { value: 'composer', text: 'Composer Radio' },
          { value: 'period', text: 'Period/Era Radio'},
          { value: 'performer', text: 'Performer Radio'}
        ],

      composerSelectField: null,
      composerOptions: [],

      genreSelectField: null,
      genreOptions: [],

      workFilterField: { value: 'recommended', text: 'Recommended works' },
      workOptions: [
          { value: 'recommended', text: 'Recommended works' },
          { value: 'obscure', text: 'Less popular'},
          { value: 'all', text: 'All works'}
        ],

      performerFilterField: { value: 'allartists', text: 'All performers' },
      performerOptions: [
          { value: 'allartists', text: 'All performers' },
          { value: 'favoriteartists', text: 'My favorite performers'}
        ],
    };
  },
  methods: {
    toggleRadio(){
      this.RadioOff = !this.RadioOff;
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
        eventBus.$emit('fireGenreSelectRadio', this.genreSelectField, this.workFilterField.value);
        for (const genre of genreList) {
          this.genreOptions.push({ value: genre, text: genre });
        }
    },
    genreSelect(){
        eventBus.$emit('fireGenreSelectRadio', this.genreSelectField, this.workFilterField.value);
    },
  },
  created() {
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
