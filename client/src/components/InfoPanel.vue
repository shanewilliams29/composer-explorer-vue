<template>
  <div class="container-fluid">
    <b-row class="footer-row">
      <b-col class="info-col">
        Composer Info
      </b-col>
      <b-col>
        Work Info
      </b-col>
      <b-col>
        Album Info
      </b-col>
    </b-row>
  </div>
</template>

<script>

export default {
  components: {
  },
};
</script>

<style scoped>
.float{
  position:fixed;
}

.container-fluid {
  position: relative;
  background-color: #484e53;
  padding-bottom: 0px;
  border-radius: 0px;
}
.info-col {
  height: 300px;
  overflow-y: hidden;
}
.album-cover-col {
  padding-right: 0px;
}
.footer-row {
  height: 300px;
  color: white;
}
.col {
  padding: 0px;
}
</style>
