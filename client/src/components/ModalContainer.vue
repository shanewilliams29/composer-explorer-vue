<template>
  <div>
        <SpotifyModal />
        <AutoplayModal />
        <NotPremiumModal />
        <NotAvailableModal />
  </div>
</template>

<script>
import SpotifyModal from './subcomponents/SpotifyModal.vue'
import AutoplayModal from './subcomponents/AutoplayModal.vue'
import NotPremiumModal from './subcomponents/NotPremiumModal.vue'
import NotAvailableModal from './subcomponents/NotAvailableModal.vue'

import {eventBus} from "../main.js";

export default {
  components: {
    SpotifyModal,
    AutoplayModal,
    NotPremiumModal,
    NotAvailableModal
  },
  methods:{
    notLoggedIn(){
      this.$bvModal.show('spotify-modal');
    },
    notPremium(){
      this.$bvModal.show('not-premium-modal');
    },
    notAvailable(){
      this.$bvModal.show('not-available-modal');
      setTimeout(() => { this.$bvModal.hide('not-available-modal'); }, 3000);
      setTimeout(() => { eventBus.$emit('fireNextAlbum'); }, 3000);
    },
    autoplayDisabled(){
      this.$bvModal.show('autoplay-modal');
    }
  },
  mounted() {
    eventBus.$on('notLoggedIn', this.notLoggedIn);
    eventBus.$on('fireAutoplayFailed', this.autoplayDisabled);
    eventBus.$on('notPremium', this.notPremium);
    eventBus.$on('notAvailable', this.notAvailable);
  },
};
</script>
