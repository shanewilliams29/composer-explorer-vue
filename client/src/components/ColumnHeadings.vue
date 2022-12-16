<template>
  <div v-if="$view.mode != 'favorites'" class="container-fluid">
    <b-row class="flex-nowrap">
      <b-col>
        <ComposerHeading />
      </b-col>
      <b-col>
        <WorkHeading />
      </b-col>
      <b-col class="last-col">
        <AlbumHeading />
      </b-col>
    </b-row>
  </div>
</template>

<script>
import ComposerHeading from '@/components/subcomponents/ComposerHeading.vue'
import WorkHeading from '@/components/subcomponents/WorkHeading.vue'
import AlbumHeading from '@/components/subcomponents/AlbumHeading.vue'

export default {
  name: 'ColumnHeadings',
  components: {
    ComposerHeading,
    WorkHeading,
    AlbumHeading
  }
};
</script>

<style>
.form-control {
  background-color: #3b4047 !important;
  border: none !important;
  color: var(--white) !important;
}
.heading-card {
  padding-bottom: 0px;
  padding-left: 5px;
}
::-webkit-input-placeholder {
  /* Chrome/Opera/Safari */
  color: #9ea4ae !important;
}
::-moz-placeholder {
  /* Firefox 19+ */
  color: #9ea4ae !important;
}
:-ms-input-placeholder {
  /* IE 10+ */
  color: #9ea4ae !important;
}
:-moz-placeholder {
  /* Firefox 18- */
  color: #9ea4ae !important;
}
</style>
<style scoped>
.container-fluid {
  background-color: var(--medium-gray);
  color: #3b4047;
}
.last-col {
  margin-right: 5px;
}
.col {
  padding: 0px;
}
.flex-nowrap{
  padding-bottom: 6.5px;
}
</style>
