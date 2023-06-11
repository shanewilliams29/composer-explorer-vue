<template>
  <div id="home" >
    <div v-if="$view.mobile">
    <MobileRadioHeading />
    <div class="container-fluid">
      <b-row>
        <b-col v-show="false" class="display-list first-col" ref="scroll-box-comp"><ComposerList /></b-col>
        <b-col class="display-list disable-scrollbars work-list-radio-mobile" ref="scroll-box" @scroll="hideKeyboard">
          <WorkList />
        </b-col>
        <b-col v-show="false" class="display-list last-col extra-margin"><AlbumList /></b-col>
      </b-row>
    </div>
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
  methods: {
    hideKeyboard() {
      document.activeElement.blur();
    },
      detectKeyboard(){
      let vh = window.innerHeight * 0.01;
      // for mobile keyboard
      if (window.innerHeight < this.$view.initialWindowHeight) {
        this.$view.mobileKeyboard = true;
        vh = vh + 250 * 0.01;
      } else {
        this.$view.mobileKeyboard = false;
      }

      document.documentElement.style.setProperty("--vh", `${vh}px`);
    },
  },
  beforeCreate() {
    this.$view.mobile = true;
    document.documentElement.style.setProperty('--flex', '0 0 400px');
  },
  created(){
    this.$view.mode = 'radio';

    let vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty("--vh", `${vh}px`);

    window.addEventListener('resize', this.detectKeyboard);
  },
  beforeDestroy(){
    window.removeEventListener('resize', this.detectKeyboard);
  }
}
</script>

<style scoped src="./MobileOverrideStyles.css">
</style>

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
  background-color: var(--medium-gray);
  height: calc(var(--vh, 1vh) * 100 - 394.5px);
  overflow-y: scroll;
}
</style>