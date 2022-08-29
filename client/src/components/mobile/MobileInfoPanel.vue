<template>
  <div v-if="true" class="container-fluid">
    <div class="footer-row">
      <b-row class="info-row">
        <ComposerInfo />
      </b-row>
      <b-row class="info-row">
        <WorkInfo />
      </b-row>
      <b-row class="info-row">
        <AlbumInfoPanel />
      </b-row>
    </div>
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
  background-color: #f1f2f4;
  padding-bottom: 0px;
  border-radius: 0px;
}
.footer-row {
  height: calc(100vh - 200px);
  color: black;
}
.col {
  padding: 5px;
  padding-right: 0px;
}
.last-col{
  padding-right: 5px;
}
.info-row{
 padding-left: 0px;
 padding-right: 0px;
 padding-top: 10px;
 padding-bottom: 0px;
 margin: 0px !important;
 height: auto !important;
}
>>> .composer-info-card{
  padding: 15px;
  padding-bottom: 5px;
  background-color: white !important;
  border: none !important;
  width: 100%;
}
>>> .album-info-card{
  padding: 15px;
  padding-bottom: 5px;
  background-color: white !important;
  border: none !important;
  width: 100%;
}
>>> .info-card-text{
  font-size: 13px;
  line-height: 130%;
  overflow-y: scroll;
  height: 100px;
  padding-left: 2px;
}
</style>