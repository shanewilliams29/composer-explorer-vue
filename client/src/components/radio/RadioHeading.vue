<template>
  <div class="container-fluid">
    <b-row class="headings-row flex-nowrap">
      <b-col>
        <div>
          <b-form-group>
            <v-select v-model="radioTypeField" label="text" :options="radioTypeOptions" @input="radioTypeSelect()" :clearable="false" class="mt-3 selector" :searchable="false"></v-select>
            <v-select
              multiple
              v-if="radioTypeField.value == 'composer'"
              v-model="composerSelectField"
              label="text"
              :options="composerOptions"
              @input="composerSelect()"
              placeholder="Select composers"
              :clearable="true"
              class="mt-3 selector allow-wrap"
              :searchable="true"
            ></v-select>
            <v-select
              v-if="radioTypeField.value == 'period'"
              v-model="periodSelectField"
              label="text"
              :options="periodOptions"
              @input="periodSelect()"
              placeholder="Select period/era"
              :clearable="false"
              class="mt-3 selector allow-wrap"
              :searchable="false"
            ></v-select>
            <vue-typeahead-bootstrap 
              v-if="radioTypeField.value == 'performer'" 
              v-model="artistSelect" 
              placeholder="Search for a performer" 
              class="mt-3 selector performer-search" 
              @hit="artistSearch" 
              size="sm" 
              :data="$lists.artistList" />
          </b-form-group>
        </div>
      </b-col>
      <b-col>
        <b-form-group>
          <b-col class="col-no-padding-left">
            <v-select
              multiple
              v-model="genreSelectField"
              :deselectFromDropdown="false"
              :closeOnSelect="true"
              label="text"
              :options="genreOptions"
              @input="genreSelect()"
              placeholder="Select genres"
              :clearable="false"
              class="mt-3 selector allow-wrap"
              :searchable="true"
            ></v-select>
          </b-col>
          <b-row class="sub-row flex-nowrap">
            <b-col class="col-padding-right">
              <b-form-input 
                class="work-search-field" 
                v-model="workSearchField" 
                v-debounce="workSearch" 
                placeholder="Search filter" 
                size="sm">
              </b-form-input>
            </b-col>
            <b-col class="col-padding-left">
              <v-select 
                v-model="workFilterField" 
                label="text" 
                :options="workOptions" 
                @input="genreSelect()" 
                :clearable="false" 
                class="mt-3 selector" 
                :searchable="false"
              ></v-select>
            </b-col>
          </b-row>
        </b-form-group>
      </b-col>
      <b-col class="last-col">
        <b-form-group>
          <b-row class="sub-row flex-nowrap">
            <b-col class="col-padding-right">
              <v-select 
                v-if="!$view.favoritesAlbums" 
                v-model="performanceFilterField" 
                label="text" 
                :options="performanceOptions" 
                @input="performanceFilter()" 
                :clearable="false" 
                class="mt-3 selector" 
                :searchable="false"></v-select>
            </b-col>
            <b-col class="col-padding-left">
              <v-select 
                v-if="!$view.favoritesAlbums" 
                v-model="limitFilterField" 
                label="text" 
                :options="limitOptions" 
                @input="limitFilter()" 
                :clearable="false" 
                class="mt-3 selector" 
                :searchable="false"></v-select>
            </b-col>
          </b-row>
          <b-row class="sub-row flex-nowrap">
            <b-col cols="9" class="col-padding-right">
              <b-button class="radio-button-off" size="sm" 
                v-if="!$view.radioPlaying && $view.enableRadio && $auth.clientToken" 
                @click="toggleRadio()" block>Radio Off</b-button>
              <b-button class="radio-button-off-disabled" size="sm" 
                v-if="!$view.radioPlaying && !$view.enableRadio || !$auth.clientToken" 
                @click="toggleRadio()" disabled block>Radio Off</b-button>
              <b-button class="radio-button-on" size="sm" 
                v-if="$view.radioPlaying && $auth.clientToken" 
                @click="toggleRadio()" block variant="warning">Radio On</b-button>
            </b-col>
            <b-col cols="3" class="col-padding-left">
              <b-button 
                v-if="$view.enableExport && $auth.clientToken" 
                class="spotify-export-button" size="sm" 
                @click="prepareForExport()" block variant="success">Export</b-button>
              <b-button 
                v-else 
                class="spotify-export-button-disabled" size="sm" 
                block variant="success" disabled>Export</b-button>
            </b-col>
          </b-row>
        </b-form-group>
      </b-col>
    </b-row>
    <PlaylistModal @submit="exportSpotify"/>
  </div>
</template>

<script>
import { radioMixin } from "./RadioHeading.js"
export default {
  mixins: [radioMixin],
}
</script>

<style scoped src="./RadioHeading.css"></style>
