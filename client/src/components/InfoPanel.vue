<template>
  <div v-if="$view.panelVisible && !$view.mobile" class="container-fluid">
    <b-row class="footer-row">
      <b-col class="info-col">
        <ComposerInfo />
      </b-col>
      <b-col class="info-col">
        <WorkInfo />
      </b-col>
      <b-col class="info-col last-col">
        <AlbumInfoPanel />
      </b-col>
    </b-row>
  </div>
</template>

<script>
import ComposerInfo from '@/components/subcomponents/ComposerInfo.vue';
import WorkInfo from '@/components/subcomponents/WorkInfo.vue';
import AlbumInfoPanel from '@/components/subcomponents/AlbumInfoPanel.vue';

export default {
  components: {
    ComposerInfo,
    WorkInfo,
    AlbumInfoPanel
  },
};
</script>

<style scoped>
.container-fluid {
  background-color: var(--light-gray);
  padding-bottom: 0px;
  border-radius: 0px;
}
.footer-row {
  height: 300px;
  color: black;
}
.col {
  padding: 5px;
  padding-right: 0px;
}
.last-col{
  padding-right: 5px;
}
</style>
