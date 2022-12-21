<template>
  <div id="home">
    <MobileRadioHeading />
    <div class="container-fluid">
      <b-row>
        <b-col v-show="false" class="display-list first-col" ref="scroll-box-comp"><ComposerList /></b-col>
        <b-col class="display-list disable-scrollbars work-list-radio-mobile" ref="scroll-box">
          <WorkList />
        </b-col>
        <b-col v-show="false" class="display-list last-col extra-margin"><AlbumList /></b-col>
      </b-row>
    </div>
  </div>
</template>

<script>
import MobileRadioHeading from '@/components/mobile/MobileRadioHeading.vue'
import ComposerList from "@/components/composers/ComposerList.vue";
import WorkList from "@/components/works/WorkList.vue";
import AlbumList from "@/components/albums/AlbumList.vue";

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
  background-color: var(--medium-gray);
  height: calc(var(--vh, 1vh) * 100 - 405px);
  overflow-y: scroll;
}

/* Text sizing for mobile */
>>> h6{
  font-size: 16px !important;
}
>>> input{
  font-size: 16px !important;
}
>>> .performer-search{
  height: 34.4px !important;
}
>>> .card{
  margin-bottom: 0px !important;
}
>>> .heading-text{
  font-size: 16px !important;
}
>>> .form-control-sm{
  font-size: 16px !important;
}
>>> .vs__selected{
  font-size: 16px !important;
}
>>> .vs__search{
  font-size: 16px !important;
}
>>> .style-chooser {
  font-size: 16px !important;
}
>>> .performer-search {
  font-size: 16px !important;
}
>>> .performer-search >>> {
  font-size: 16px !important;
  --vs-font-size: 16px;
}
>>> .btn{
  font-size: 16px !important;
}
>>> .cursor span{
  font-size: 16px !important;
}
>>> .works-table span{
  font-size: 16px !important;
}
>>> .works-table .heart-number span{
  font-size: 12px !important;
}
>>> .album_text_columns span{
  font-size: 14px !important;
}
>>> .album_text_columns .album-likes-class .likes span{
  font-size: 12px !important;
}
>>> .album_text_columns .album-likes-class .user-liked span{
  font-size: 14px !important;
}
>>> .album_text_columns .label{
  font-size: 12px !important;
}
>>> .album-titles {
  font-size: 14px !important;
}


</style>