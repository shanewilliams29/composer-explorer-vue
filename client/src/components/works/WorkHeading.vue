<template>
  <b-card class="heading-card work-card">
    <b-form-group>
      <b-form-input 
        v-model="workSearchField" 
        v-debounce="workSearch" 
        type="text" 
        @focus="onWorkFocus()" 
        :placeholder="workSearchPlaceholder" 
        size="sm" 
        autocomplete="off">
      </b-form-input>
      <v-select 
        v-model="workFilterField" 
        label="text" 
        :options="workOptions" 
        @input="workFilter()" 
        :clearable="false" 
        class="mt-3 work-select" 
        :searchable="false">
      </v-select>
    </b-form-group>
  </b-card>
</template>

<script>
import { eventBus } from "@/main.js";

export default {
  data() {
    return {
      workFilterField: { value: "recommended", text: "Recommended works" },
      workSearchField: null,
      workSearchPlaceholder: "Search works by " + this.$config.composer,
      workOptions: [
        { value: "recommended", text: "Recommended works" },
        { value: "all", text: "All works" },
      ],
    };
  },
  methods: {
    workRecommended(recommended){
      const workOptionsList = {
        'recommended': { value: "recommended", text: "Recommended works" }, 
        'all': { value: "all", text: "All works" }
      }
      if (recommended == 1){
        return workOptionsList['recommended'];
      } else {
        return workOptionsList['all'];
      }
    },
    workFilter() {
      eventBus.$emit("fireWorkFilter", this.workFilterField.value);
      this.workSearchField = "";
    },
    workSearch() {
      eventBus.$emit("fireWorkSearch", this.workSearchField);
      if (this.workSearchField != "") {
        this.workFilterField = 'Search results for "' + this.workSearchField + '"';
      } else {
        this.workFilterField = { value: "recommended", text: "Recommended works" };
      }
    },
    onWorkFocus() {
      this.workFilterField = { value: "recommended", text: "Recommended works" };
      this.workSearchField = "";
      eventBus.$emit("fireWorkSearch", "");
    },
    newComposer(composer) {
      this.workSearchPlaceholder = "Search works by " + composer;
      this.workSearchField = "";
      this.workFilterField = { value: "recommended", text: "Recommended works" };
    },
    setWorkOmniSearch(work){
      if(this.workFilterField.value != 'all' || this.$config.composer != work.composer){
        this.workFilterField = { value: "all", text: "All works" };
        this.workSearchPlaceholder = "Search works by " + work.composer;
        this.$config.composer = work.composer;
        this.$config.work = work.id;
        this.$config.genre = work.genre;
        localStorage.setItem("config", JSON.stringify(this.$config));
        this.workFilter();
      } else {
        this.$config.composer = work.composer;
        this.$config.work = work.id;
        this.$config.genre = work.genre;
        localStorage.setItem("config", JSON.stringify(this.$config));
        eventBus.$emit("fireWorkScroll", work.genre);
      }

    }
  },
  created() {
    this.workFilterField = this.workRecommended(this.$config.workRecommended);
    eventBus.$on("requestWorksList", this.newComposer);
    eventBus.$on("fireWorkOmniSearch", this.setWorkOmniSearch);
  },
  beforeDestroy() {
    eventBus.$off("requestWorksList", this.newComposer);
    eventBus.$off("fireWorkOmniSearch", this.setWorkOmniSearch);
  },
};
</script>

<style scoped>
.work-card{
  padding-top: 5px !important;
}
.form-group{
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
.work-select {
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
  --vs-search-input-bg: none;
  --vs-controls-color: var(--my-white);
  --vs-border-color: var(--search-gray);
  --vs-border-width: 1px;
  --vs-selected-bg: var(--search-gray);
  --vs-selected-color: var(--my-white);
  --vs-line-height: 1;
  --vs-search-input-color: var(--my-white);
}
.form-control:focus{
  box-shadow: none; 
  -webkit-box-shadow: none;
} 
</style>