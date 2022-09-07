<template>
  <div v-if="$view.mobile" class="container-fluid">
    <div class="footer-row disable-scrollbars">
      <b-row v-if="$view.panelVisible" class="info-row work-info">
        <WorkInfo />
      </b-row>
      <b-row v-if="$view.panelVisible" class="info-row">
        <AlbumInfoPanel />
      </b-row>
      <b-row class="info-row">
        <TrackListingMobile />
      </b-row>
    </div>
  </div>
</template>

<script>
import WorkInfo from '@/components/subcomponents/WorkInfo.vue';
import AlbumInfoPanel from '@/components/subcomponents/AlbumInfoPanel.vue';
import TrackListingMobile from '@/components/mobile/TrackListingMobile.vue'

export default {
  components: {
    WorkInfo,
    AlbumInfoPanel,
    TrackListingMobile
  }
};
</script>

<style scoped>
>>> a:hover{
  text-decoration: none !important;
}
.container-fluid {
  background-color: #454d54;
  padding-bottom: 0px;
  border-radius: 0px;
}
.footer-row {
  /*height: calc(var(--vh, 1vh) * 100 - 314px + 8.5px);*/
  height: calc(var(--vh, 1vh) * 100 - 117px - 66px);
  color: black;
  overflow-y: scroll;
  padding-bottom: 10px;
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
.track-listing-mobile{
  width: 100%;
}
>>> .composer-info-card{
  padding: 15px;
  padding-bottom: 0px;
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
>>> .heading-tr{
  height: auto !important;
}
>>> .card-title{
  height:  auto;
}
>>> .track-info-card{
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
  height: auto;
  padding-left: 2px;
}
>>> .card-deck{

}
>>> .track-card {
  width: 100vw;
  margin: 0px !important;
  padding-left: 6px;
  right: 3px;
  height: 94.58px;
  position: absolute;
  bottom: 0px;
  left: 0px;

}
.disable-scrollbars::-webkit-scrollbar {
  background: transparent; /* Chrome/Safari/Webkit */
  width: 0px;
}
    
.disable-scrollbars {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none;  /* IE 10+ */
}
</style>