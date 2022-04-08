<template>
  <div class="container-fluid">
    <b-row>
      <b-col>
        <div>
          <b-card class="composer-card">
            <b-form-group>
              <b-form-input
                id="input-sm"
                placeholder="Search composers"
                size="sm"
              ></b-form-input>
              <b-form-select
                v-model="selected"
                :options="options"
                size="sm"
                class="mt-3"
              ></b-form-select>
            </b-form-group>
          </b-card>
        </div>
      </b-col>
      <b-col>
        <b-card class="work-card">
          <b-form-group>
            <b-form-input
              id="input-sm"
              placeholder="Search works"
              size="sm"
            ></b-form-input>
            <b-form-select
              v-model="selected"
              :options="options"
              size="sm"
              class="mt-3"
            ></b-form-select>
          </b-form-group>
        </b-card>
      </b-col>
      <b-col>
        <b-card class="albums-card">
          <b-form-group>
            <b-form-input
              id="input-sm"
              placeholder="Search performers"
              size="sm"
            ></b-form-input>
            <b-form-select
              v-model="selected"
              :options="options"
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

export default {
  data() {
    return {
      work_heading: "",
      album_heading: "",
        selected: null,
        options: [
          { value: null, text: 'Filter composers' },
          { value: 'a', text: 'This is First option' },
          { value: 'b', text: 'Selected Option' },
          { value: { C: '3PO' }, text: 'This is an option with object value' },
          { value: 'd', text: 'This one is disabled', disabled: true }
        ]
    };
  },
  created() {
    this.work_heading = "Works by Beethoven";
    this.album_heading = "Albums for \"Piano Concerto No. 5 in E♭ major\"";
    eventBus.$on('fireComposers', (composer) => {
        this.work_heading = "Works by " + composer;
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
.card-body {
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
