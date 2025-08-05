<template>
	<div v-show="showBanner && !$view.mobile" class="patreon-banner">
		<div class="container">
			<p class="patreon">Help with Composer Explorer's development and hosting costs. <a href="https://www.patreon.com/composerexplorer" target="_blank" class="patreon-link">Support us on Patreon! </a><a class="patreonclosebtn" @click="toggleBanner()">&times;</a></p>
		</div>
	</div>
</template>

<script>


export default {
  data() {
    return {
      showBanner: false,
    };
  },
  computed: {
    patreonChanged() {
      return this.$auth.patreon;
    },
  },
  watch: {
    patreonChanged(patreonStatus) {
      this.showBanner = !patreonStatus;
      if(this.showBanner){
        document.documentElement.style.setProperty("--workingheight", `279px`);
      } else {
        document.documentElement.style.setProperty("--workingheight", `244px`);
      }
    },
  },
  methods: {
    toggleBanner() {
      this.showBanner = !this.showBanner;
      if(this.showBanner){
        document.documentElement.style.setProperty("--workingheight", `279px`);
      } else {
        document.documentElement.style.setProperty("--workingheight", `244px`);
      }
    },
  },
};

</script>

<style scoped>
.patreon-banner{
  background-color: #f0f3f4 !important;
  text-align: center;
  height: 35px;
}

.patreonclosebtn {
    position: absolute;
    top: -2px;
    right: 20px;
    font-size: 26px;
    margin-left: 10px;
    cursor: pointer;
}

.patreon {
  padding-top:5px;
  padding-bottom:5px;
  margin-bottom: 0px;
}
</style>