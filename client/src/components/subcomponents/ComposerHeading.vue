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
      composerFilterForm: { value: "popular", text: "Most popular" },
      composerSearchForm: null,
      composerOptions: [
        { value: "popular", text: "Most popular" },
        { value: "tier2", text: "Less popular" },
        // { value: 'tier3', text: 'More obscure' },
        // { value: 'tier4', text: 'Quite obscure' },
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
    composerFilter() {
      eventBus.$emit("requestComposersFromFilter", this.composerFilterForm.value);
      this.composerSearchForm = "";
    },
    composerSearch() {
      eventBus.$emit("requestComposersFromSearch", this.composerSearchForm);
      if (this.composerSearchForm) {
        this.composerFilterForm = `Search results for "${this.composerSearchForm}"`;
      } else {
        this.composerFilterForm = { value: "popular", text: "Most popular" };
      }
    },
    onComposerFocus() {
      this.composerFilterForm = { value: "popular", text: "Most popular" };
      this.composerSearchForm = "";
      eventBus.$emit("requestComposersFromSearch", "");
    },
  }
};
</script>

<style scoped>
.composer-card {
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
.composer-select {
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
  --vs-controls-color: #fff;
  --vs-border-color: #3b4047;
  --vs-border-width: 1px;
  --vs-selected-bg: #3b4047;
  --vs-selected-color: #fff;
  --vs-line-height: 1;
  --vs-search-input-color: #fff;
}
</style>