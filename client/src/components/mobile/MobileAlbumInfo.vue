<template>
  <b-card no-body bg-variant="dark">
    <b-row no-gutters>
      <b-col cols="auto" class="album-cover-col">
        <b-card-img :src="$config.albumData.album_img" alt="Album Cover" class="rounded-0"></b-card-img>
      </b-col>
      <b-col>
        <b-card-body class="info-card-body">
          <b-card-text>
            <div class="centered album-data">
              <span>{{$config.composer}}</span>
              <span style="font-weight: bold;">{{$config.workTitle}}</span>
              <span style="color: var(--medium-dark-gray); font-size: 13px;">{{$config.albumData.artists}}</span>
            </div>
          </b-card-text>
        </b-card-body>
      </b-col>
    </b-row>
  </b-card>
</template>

<style scoped>
.album-cover-col {
  padding-right: 0px;
}
.info-card-body {
  background: none !important;
  border: 0px;
  width: 100%;
  overflow-x: hidden;
  height: 100px;
  color: var(--white) !important;
}
.card{
  background: none !important;
  border: none !important;
  width: 100%;
}
.card-img {
  height: 100%;
  width: auto;
  max-width: 100px;
  max-height: 100px;
}
.card-body {
  font-size: 14px;

  margin-right: 6px;
  padding-top: 0px;
  height: 100px;
  overflow-y: hidden;
}
.centered {
  padding-left: 8px;
  display: flex;
  flex-direction: column;
  column-gap: 0px;
  justify-content: center;
  height: 100px;
}
.album-data {
  padding-left: 10px;
  line-height: 130%;
}
</style>
