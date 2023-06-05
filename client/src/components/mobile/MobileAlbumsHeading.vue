<template>
  <div class="container-fluid">
    <b-row class="headings-row flex-nowrap">
      <b-col>
        <div>
          <b-form-group>
            <v-select
              v-model="composerSelectField"
              label="text"
              :options="composerOptions"
              @input="composerSelect()"
              placeholder="Select composer"
              :clearable="true"
              class="mt-3 selector"
              :searchable="true"
            ></v-select>
            <v-select 
              v-model="albumSortField" 
              label="text" 
              :options="albumSortOptions" 
              @input="albumSortSelect()" 
              :clearable="false" 
              class="mt-3 selector" 
              :searchable="false">
          </v-select>
          </b-form-group>
        </div>
      </b-col>
      <b-col class="last-col">
        <b-form-group>
            <vue-typeahead-bootstrap 
              v-model="artistSelectField" 
              placeholder="Search for a performer" 
              class="mt-3 selector performer-search" 
              ref="artistTypeahead"
              @hit="artistSearch" 
              @input="resetArtistField"
              size="sm" 
              :data="$lists.artistList" />
            <vue-typeahead-bootstrap 
              v-model="workSelectField" 
              placeholder="Search for a work" 
              class="mt-3 selector work-search" 
              ref="workTypeahead"
              @hit="workSearch" 
              @input="resetWorkField"
              size="sm" 
              :data="$lists.albumViewWorks" />
        </b-form-group>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import { albumsMixin } from "@/components/albumsview/AlbumsViewHeading.js"
export default {
  mixins: [albumsMixin],
}
</script>

<style scoped src="@/components/albumsview/AlbumsViewHeading.css"></style>
