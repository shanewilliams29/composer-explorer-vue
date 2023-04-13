<template>
  <b-card class="heading-card albums-card">
    <b-form-group>
      <v-select v-model="albumFilterField" label="text" :options="albumOptions" @input="albumFilter()" :clearable="false" :autoscroll="false" :components="{OpenIndicator}" class="mt-3 performer-search"></v-select>
      <b-row class="flex-nowrap">
        <b-col style="padding-right: 0px;" cols="8">
          <v-select v-model="albumSortField" label="text" :options="albumSortOptions" @input="albumFilter()" :clearable="false" class="mt-3 filter-select" :searchable="false"></v-select>
        </b-col>
        <b-col style="padding-left: 5px;" cols="4">
          <v-select v-model="albumSizeField" label="text" :options="albumSizeOptions" @input="albumSize()" :clearable="false" class="mt-3 filter-select" :searchable="false"></v-select>
        </b-col>
      </b-row>
    </b-form-group>
  </b-card>
</template>

<script>
import { eventBus } from "@/main.js";

export default {
  data() {
    return {
      OpenIndicator: {
        render: (createElement) => createElement("span", ""),
      },

      albumFilterField: { value: "allartists", text: "All performers" },
      albumOptions: [],

      albumSortField: { value: "recommended", text: "Recommended sorting" },
      albumSortOptions: [
        { value: "recommended", text: "Recommended sorting" },
        { value: "dateascending", text: "Date, earliest to latest" },
        { value: "datedescending", text: "Date, latest to earliest" },
        { value: "durationascending", text: "Duration, shortest to longest" },
        { value: "durationdescending", text: "Duration, longest to shortest" },
      ],

      albumSizeField: { value: this.$config.albumSize, text: this.capitalize(this.$config.albumSize) },
      albumSizeOptions: [
        { value: "large", text: "Large" },
        { value: "small", text: "Small" },
      ],
    };
  },
  methods: {
    capitalize(string) {
      let capitalized = string[0].toUpperCase() + string.substring(1);
      return capitalized;
    },
    albumFilter() {
      eventBus.$emit("requestAlbums", this.$config.work, 
        this.albumFilterField.value === "allartists" ? "" : this.albumFilterField.value,
        this.albumSortField.value
      );
    },
    albumSize() {
      this.$config.albumSize = this.albumSizeField.value === "large" ? "large" : "small";
      localStorage.setItem("config", JSON.stringify(this.$config));
    },
    newWork() {
      this.albumFilterField = { value: "allartists", text: "All performers" };
      this.albumSortField = { value: "recommended", text: "Recommended sorting" };
    },
    createArtistList(artistList) {
      this.albumOptions = [{ value: "allartists", text: "All performers" }];
      for (var key in artistList) {
        this.albumOptions.push({ value: key, text: key });
      }
    },
  },
  created() {
    eventBus.$on("changeWork", this.newWork);
    eventBus.$on("sendArtistList", this.createArtistList);
  },
  beforeDestroy() {
    eventBus.$off("changeWork", this.newWork);
    eventBus.$off("sendArtistList", this.createArtistList);
  },
};
</script>

<style scoped>
.albums-card {
  padding-top: 5px !important;
}
.form-group {
  margin-bottom: 0px;
}
.card-body {
  background: none !important;
}
.card {
  background: none;
  border: none;
}
.form-row {
  margin-bottom: 0px;
}
.col {
  padding: 0px;
}
.filter-select {
  margin-top: 5px !important;
  font-size: 14px;
  fill: white;
}
>>> .vs__selected-options {
  flex-wrap: nowrap;
}
>>> .vs__selected {
  white-space: nowrap;
  overflow: hidden;
}
>>> {
  --vs-search-input-bg: none;
  --vs-controls-color: var(--my-white);
  --vs-border-color: var(--search-gray);
  --vs-border-width: 1px;
  --vs-selected-bg: var(--search-gray);
  --vs-selected-color: var(--my-white);
  --vs-line-height: 1;
  --vs-search-input-color: var(--my-white);
}
.performer-search {
  margin-top: 0px !important;
  padding-top: 3px;
  font-size: 14px !important;
  background-color: var(--search-gray) !important;
  height: 31px;
  border-radius: 4px;
}
.performer-search >>> {
  --vs-border-width: 0px;
  font-size: 14px !important;
  --vs-font-size: 14px;
}
</style>