<template>
  <div class="container-fluid">
    <b-row>
      <b-col>
        <div>
          <b-card class="heading-card composer-card">
            <b-form-group>
              <b-form-input
                v-model="composerSearchForm"
                @input="composerSearch()"
                @focus="onComposerFocus()"
                placeholder="Search composers"
                size="sm"
              ></b-form-input>
              <b-form-select
                v-model="composerFilterForm"
                :options="composerOptions"
                @change="composerFilter()"
                size="sm"
                class="mt-3"
              ></b-form-select>
            </b-form-group>
          </b-card>
        </div>
      </b-col>
      <b-col>
        <b-card class="heading-card work-card">
            <b-form-group>
              <b-form-input
                v-model="workSearchField"
                @input="workSearch()"
                @focus="onWorkFocus()"
                :placeholder="workSearchPlaceholder"
                size="sm"
              ></b-form-input>
              <b-form-select
                v-model="workFilterField"
                :options="workOptions"
                @change="workFilter()"
                size="sm"
                class="mt-3"
              ></b-form-select>
            </b-form-group>
        </b-card>
      </b-col>
      <b-col>
        <b-card class="heading-card albums-card">
          <b-form-group>
            <b-form-input
              id="input-sm"
              placeholder="Search performers"
              size="sm"
            ></b-form-input>
            <b-form-select
              v-model="composerFilterForm"
              :options="composerOptions"
              size="sm"
              class="mt-3"
            ></b-form-select>
          </b-form-group>
        </b-card>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import {eventBus} from "../main.js";
import {currentConfig} from "../main.js";

export default {
  data() {
    return {
      work_heading: "",
      album_heading: "",
      composerFilterForm: 'popular',
      composerSearchForm: null,
      composerOptions: [
          { value: null, text: 'Filter composers', disabled: true},
          { label: 'Period',
            options: [
              { value: 'common', text: 'Common Practice' },
              { value: 'early', text: 'Early' },
              { value: 'all', text: 'All - by region' },
              { value: 'alphabet', text: 'All - alphabetically' }
            ]
          },
          { label: 'Era',
            options: [
              { value: 'baroque', text: 'Baroque' },
              { value: 'classical', text: 'Classical' },
              { value: 'romantic', text: 'Romantic' },
              { value: '20th', text: '20th/21st Century' }
            ]
          },
         { label: 'Misc',
            options: [
              { value: 'popular', text: 'Most popular' },
              { value: 'women', text: 'Women'}
            ]
          }
        ],

      workFilterField: 'recommended',
      workSearchField: null,
      workSearchPlaceholder: "Search works by " + currentConfig.composer,
      workOptions: [
          { value: null, text: 'Filter works', disabled: true},
          { value: 'recommended', text: 'Recommended works' },
          // { value: 'catalogued', text: 'Catalogued' },
          { value: 'all', text: 'All works'}
        ],
    };
  },
  methods: {
    composerFilter() {
      eventBus.$emit('fireComposerFilter', this.composerFilterForm);
      this.composerSearchForm = '';
      console.log(this.composerFilterForm);
    },
    composerSearch() {
      eventBus.$emit('fireComposerSearch', this.composerSearchForm);
      this.composerFilterForm = null;
      console.log(this.composerSearchForm);
    },
    onComposerFocus() {
      this.composerSearchForm = '';
      eventBus.$emit('fireComposerSearch', '');
    },
    workFilter() {
      eventBus.$emit('fireWorkFilter', this.workFilterField);
      this.workSearchField = '';
      console.log(this.workFilterField);
    },
    workSearch() {
      eventBus.$emit('fireWorkSearch', this.workSearchField);
      this.workFilterField = null;
      console.log(this.workSearchField);
    },
    onWorkFocus() {
      this.workSearchField = '';
      eventBus.$emit('fireWorkSearch', '');
    }
  },
  created() {
    this.work_heading = "Works by Beethoven";
    this.album_heading = "Albums for \"Piano Concerto No. 5 in E♭ major\"";
    eventBus.$on('fireComposers', (composer) => {
        this.workSearchPlaceholder = "Search works by " + composer;
        this.workSearchField = '';
        this.workFilterField = 'recommended';
    })
    eventBus.$on('fireAlbums', (work_id, title) => {
        this.album_heading = "Albums for \"" + title + "\"";
    })
  },
};
</script>

<style scoped>
.card {
  background: none;
  border: none;
}
.heading-card {
  padding-top: 20px;
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
</style>
