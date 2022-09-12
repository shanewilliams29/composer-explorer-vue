<template>
  <div>
  <div class="container-fluid">
    <b-row class="footer-row">
      <b-col v-show="false" class="info-col">
        <AlbumInfo />
      </b-col>
      <b-col>
          <b-button class="info-panel-button" @click="togglePanel()">
          <span class="icon-inactive" v-if="!buttonActive"><b-icon-info-circle></b-icon-info-circle></span>
          <span class="icon-active" v-if="buttonActive"><b-icon-info-circle></b-icon-info-circle></span>
        </b-button>
        <MobilePlayerControls />
      </b-col>
    </b-row>
  </div>
<div class="floating-img">
  <img class="header-image" src="https://storage.googleapis.com/composer-explorer.appspot.com/headers/Tristan%20und%20Isolde.jpg">
</div>
</div>
</template>

<script>
import AlbumInfo from '@/components/subcomponents/AlbumInfo.vue'
import MobilePlayerControls from '@/components/mobile/MobilePlayerControls.vue'

export default {
  components: {
    AlbumInfo,
    MobilePlayerControls,
  },
  data() {
    return {
      buttonActive: false
    };
  },
  methods:{
    togglePanel(){
      this.$parent.togglePanel();
      this.buttonActive = !this.buttonActive;
    }
  }
};
</script>
<style scoped>
.header-image {
  position: absolute;
  height: 120px;
  width: auto;
/*  left: 50%;
  transform: translate(-50%, 0);*/
  left: 0px;
  bottom: 0px;
  z-index: -5;
  opacity: 0.3;
}
.container-fluid {
  position: relative;
  background:  none;
  padding-bottom: 0px;
  border-radius: 0px;
  border-radius: 0px;
}
.album-cover-col {
  padding-right: 0px;
}
.footer-row {
  color: white;
  z-index: 10;
  opacity: 1;
}
.col {
  padding: 0px;
}
.info-panel-button {
  position: absolute;
  right: 13px;
  font-size: 18px !important;
  border-radius: 50% !important;
  padding-left: 2.8px !important;
  padding-right: 2.8px !important;
  padding-top: 1.2px;
  padding-bottom: 0px;
  bottom: calc(117px - 22.5px - 13px);
  z-index: 1;
  background: none;
  border: none !important;
  box-shadow: none !important;
}
.btn:hover, .btn:focus, .btn:active{
   outline: none !important;
   box-shadow: none;
}
.icon-inactive{
  color: white !important;
}
.icon-active{
  color: var(--yellow) !important;
}
</style>
