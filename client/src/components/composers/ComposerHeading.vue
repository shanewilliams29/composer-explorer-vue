<template>
  <b-card class="heading-card composer-card">
    <b-form-group>
      <b-form-input v-model="composerSearchForm" v-debounce="composerSearch" type="text" @focus="onComposerFocus()" placeholder="Search composers" size="sm" autocomplete="off"></b-form-input>
      <v-select v-model="composerFilterForm" label="text" :options="composerOptions" @input="composerFilter()" :clearable="false" class="mt-3 composer-select" :searchable="false"></v-select>
    </b-form-group>
  </b-card>
</template>

<script>
import { eventBus } from "@/main.js";



export default {
  data() {
    return {
      composerFilterForm: { value: 1, text: "Most popular" },
      composerSearchForm: null,
      composerOptions: [
        { value: 1, text: "Most popular" },
        { value: 2, text: "Less popular" },
        // { value: 3, text: 'More obscure' },
        // { value: 4, text: 'Quite obscure' },
        { value: "early", text: "Early" },
        { value: "baroque", text: "Baroque" },
        { value: "classical", text: "Classical" },
        { value: "romantic", text: "Romantic" },
        { value: "20th", text: "20th/21st Century" },
        { value: "all", text: "All - by region" },
        { value: "alphabet", text: "All - alphabetically" },
      ],
    };
  },
  methods: {
    getOption(tier){
      const tierOptions = {
        1: { value: 1, text: "Most popular" }, 
        2: { value: 2, text: "Less popular" }, 
        3: { value: 3, text: 'More obscure' },
        4: { value: 4, text: 'Quite obscure' }
      }
      return tierOptions[tier];
    },
    composerFilter() {
      eventBus.$emit("requestComposersFromFilter", this.composerFilterForm.value);
      this.composerSearchForm = "";
    },
    composerSearch() {
      eventBus.$emit("requestComposersFromSearch", this.composerSearchForm);
      if (this.composerSearchForm) {
        this.composerFilterForm = `Search results for "${this.composerSearchForm}"`;
      } else {
        this.composerFilterForm = { value: 1, text: "Most popular" };
      }
    },
    onComposerFocus() {
      this.composerFilterForm = { value: 1, text: "Most popular" };
      this.composerSearchForm = "";
      eventBus.$emit("requestComposersFromSearch", "");
    },
    setComposerOmniSearch(composer){
      if(this.composerFilterForm.value != 'all'){
        this.composerFilterForm = { value: "all", text: "All - by region" };
        this.composerFilter();
      }
      this.$config.composer = composer.name_short;
      this.$config.tier = composer.tier;
      localStorage.setItem("config", JSON.stringify(this.$config));
    },
    setWorkOmniSearch(){
      if(this.composerFilterForm.value != 'all'){
        this.composerFilterForm = { value: "all", text: "All - by region" };
        this.composerFilter();
      }
    }
  },
  created() {
    this.composerFilterForm = this.getOption(this.$config.tier);
    eventBus.$on("fireComposerOmniSearch", this.setComposerOmniSearch);
    eventBus.$on("fireWorkOmniSearch", this.setWorkOmniSearch);
  },
  beforeDestroy() {
    eventBus.$off("fireComposerOmniSearch", this.setComposerOmniSearch);
    eventBus.$off("fireWorkOmniSearch", this.setWorkOmniSearch);
  },
};
</script>

<style scoped>
.composer-card {
  padding-top: 5px !important;
}
.form-group {
  margin-bottom: 1px;
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
.composer-select {
  margin-top: 5px !important;
  font-size: 14px;
  fill: yellow;
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
.form-control:focus{
  box-shadow: none; 
  -webkit-box-shadow: none;
} 
</style>