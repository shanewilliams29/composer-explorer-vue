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
  },
  created() {
    eventBus.$on("requestWorksList", this.newComposer);
  },
  beforeDestroy() {
    eventBus.$off("requestWorksList", this.newComposer);
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
  --vs-controls-color: #fff;
  --vs-border-color: #3b4047;
  --vs-border-width: 1px;
  --vs-selected-bg: #3b4047;
  --vs-selected-color: #fff;
  --vs-line-height: 1;
  --vs-search-input-color: #fff;
}
</style>