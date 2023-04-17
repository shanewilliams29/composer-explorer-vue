<template>
  <div class="container-fluid">
    <b-row class="headings-row flex-nowrap">
      <b-col>
        <div>
          <b-form-group>
            <v-select v-model="filterField" label="text" :options="filterFieldOptions" @input="filterFieldSelect()" :clearable="false" class="mt-3 selector" :searchable="false"></v-select>
            <v-select
              v-if="filterField.value == 'composer'"
              v-model="composerSelectField"
              label="text"
              :options="composerOptions"
              @input="composerSelect()"
              placeholder="Select composer"
              :clearable="true"
              class="mt-3 selector allow-wrap"
              :searchable="true"
            ></v-select>
            <v-select
              v-if="filterField.value == 'period'"
              v-model="periodSelectField"
              label="text"
              :options="periodOptions"
              @input="periodSelect()"
              placeholder="Select period/era"
              :clearable="true"
              class="mt-3 selector allow-wrap"
              :searchable="false"
            ></v-select>
          </b-form-group>
        </div>
      </b-col>
      <b-col>
        <b-form-group>
            <vue-typeahead-bootstrap 
              v-model="artistSelect" 
              placeholder="Search for a performer" 
              class="mt-3 selector performer-search" 
              ref="typeahead"
              @hit="artistSearch" 
              @input="resetArtistField"
              size="sm" 
              :data="$lists.artistList" />
        </b-form-group>
      </b-col>
      <b-col class="last-col">
        <b-form-group>
          <v-select v-model="albumSortField" label="text" :options="albumSortOptions" @input="albumSortSelect()" :clearable="false" class="mt-3 selector" :searchable="false"></v-select>
        </b-form-group>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import { albumsMixin } from "./AlbumsViewHeading.js"
export default {
  mixins: [albumsMixin],
}
</script>

<style scoped src="./AlbumsViewHeading.css"></style>
