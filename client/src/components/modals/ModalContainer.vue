<template>
  <div>
    <SpotifyModal />
    <AutoplayModal />
    <NotPremiumModal />
    <NotAvailableModal />
    <SpotifyFailModal />
  </div>
</template>

<script>
import SpotifyModal from './SpotifyModal.vue'
import AutoplayModal from './AutoplayModal.vue'
import NotPremiumModal from './NotPremiumModal.vue'
import NotAvailableModal from './NotAvailableModal.vue'
import SpotifyFailModal from './SpotifyFailModal.vue'

import {eventBus} from "@/main.js";

export default {
  components: {
    SpotifyModal,
    AutoplayModal,
    NotPremiumModal,
    NotAvailableModal,
    SpotifyFailModal
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
      // Next album is fired from SpotifyPlayer.vue after connection to Spotify is re-established.
    },
    autoplayDisabled(){
      this.$bvModal.show('autoplay-modal');
    },
    spotifyFailure(){
      this.$bvModal.show('spotify-fail-modal');
    }
  },
  mounted() {
    eventBus.$on('notLoggedIn', this.notLoggedIn);
    eventBus.$on('fireAutoplayFailed', this.autoplayDisabled);
    eventBus.$on('notPremium', this.notPremium);
    eventBus.$on('fireNotFoundModal', this.notAvailable);
    eventBus.$on('spotifyFail', this.spotifyFailure);
  },
};
</script>
