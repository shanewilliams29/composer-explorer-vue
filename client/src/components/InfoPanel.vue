<template>
  <div class="container-fluid">
    <b-row class="footer-row">
      <b-col class="info-col">
        Composer Info
      </b-col>
      <b-col class="info-col">
        Work Info
      </b-col>
      <b-col class="info-col">
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
  background-color: #f1f2f4;
  padding-bottom: 0px;
  border-radius: 0px;
}
.footer-row {
  height: 300px;
  color: black;
}
.col {
  padding: 5px;
}
</style>
