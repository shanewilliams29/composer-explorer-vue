<template>
  <div id="home">
    <MobileRadioHeading/>
    <div class="container-fluid">
      <b-row>
        <b-col v-show="false" class="display-list first-col" ref="scroll-box-comp"><ComposerList/></b-col>
        <b-col class="display-list disable-scrollbars work-list-radio-mobile" ref="scroll-box">
                  <WorkList/>
        </b-col>
        <b-col v-show="false" class="display-list last-col extra-margin"><AlbumList/></b-col>
      </b-row>
    </div>
  </div>
</template>



<script>
import MobileRadioHeading from '@/components/mobile/MobileRadioHeading.vue'
import ComposerList from '@/components/ComposerList.vue'
import WorkList from '@/components/WorkList.vue'
import AlbumList from '@/components/AlbumList.vue'

export default {
  name: 'MobileRadio',
  components: {
    MobileRadioHeading,
    ComposerList,
    WorkList,
    AlbumList,
  },
  beforeCreate() {
    this.$view.mobile = true;
    document.documentElement.style.setProperty('--flex', '0 0 400px');
  },
  created(){
    this.$view.mode = 'radio';

    let vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);

    window.addEventListener('resize', () => {

      let vh = window.innerHeight * 0.01;

      // for mobile keyboard
      if (window.innerHeight < 550){
        this.$view.mobileKeyboard = true;
        vh = vh + (300 * 0.01);
      } else {
        this.$view.mobileKeyboard = false;
      }
      
      document.documentElement.style.setProperty('--vh', `${vh}px`);
    });
  }
}
</script>

<style scoped>
>>> .highlight{
  background-color: var(--green);
}
>>> .highlight td{
  background-color: var(--green);
}
>>> .music-note{
  color: var(--green);
}
/* .playback-container{
    padding: 13px;
    padding-top: 3px !important;
    padding-bottom: 0px;
    font-size: 14px;
  }*/
.disable-scrollbars::-webkit-scrollbar {
  background: transparent; /* Chrome/Safari/Webkit */
  width: 0px;
}
    
.disable-scrollbars {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none;  /* IE 10+ */
}
  .work-list-radio-mobile{
    /*height: calc(100vh - 314px);*/
    height: calc(var(--vh, 1vh) * 100 - 380px - 1px);
    overflow-y: scroll;
  }
</style>