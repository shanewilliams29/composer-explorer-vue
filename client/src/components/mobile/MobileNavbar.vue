<template>
  <div v-if="$view.mobile">
    <div>
      <div class="container-fluid">
        <b-navbar type="dark" variant="dark" class="no-padding">
          <b-container fluid class="d-flex">
            <b-nav pills class="navbar-items buttons-nav flex-fill justify-content-around flex-nowrap">
              <b-nav-item class="small-text flex-fill text-center" id="search" :active='$route.path == "/mobilesearch"' @click="$router.push('/mobilesearch')">
                <b-icon-search></b-icon-search><br>Search
              </b-nav-item>
              <b-nav-item class="small-text flex-fill text-center" id="home" :active='$route.path == "/mobile"' @click="$router.push('/mobile')">
                <b-icon-music-note-list></b-icon-music-note-list><br>Browse
              </b-nav-item>
              <b-nav-item class="small-text flex-fill text-center" id="performer" :active='$route.name == "mobileperformers"' @click="$router.push('/mobileperformers')">
                <b-icon-person-lines-fill></b-icon-person-lines-fill><br>Performers
              </b-nav-item>
              <b-nav-item class="small-text flex-fill text-center" id="albums" :active='$route.name == "mobilealbums"' @click="$router.push('/mobilealbums')">
                <b-icon-record-circle-fill></b-icon-record-circle-fill><br>Albums
              </b-nav-item>
              <b-nav-item class="small-text flex-fill text-center" id="favorites" :active='$route.name == "mobilefavorites"' @click="$router.push('/mobilefavorites')">
                <b-icon-heart></b-icon-heart><br>Favorites
              </b-nav-item>
              <b-nav-item class="small-text flex-fill text-center" id="radio" :active='$route.name == "mobileradio"' @click="$router.push('/mobileradio')">
                <b-icon-soundwave></b-icon-soundwave><br>Radio
              </b-nav-item>
            </b-nav>
          </b-container>
        </b-navbar>
      </div>
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
     .overlay {
            display: block;
            position: absolute;
            top: 66;
            left: 0;
            width: 100%;
            height: calc(100% - 66px);
            background: rgba(52, 58, 64, 0.5);
            z-index: 10;
        }

.centered{
  text-align: center;
}
.small-text{
  font-size: 10px;
}
.nav-link{
  padding-left: 0px;
  padding-right: 0px;
  padding-top: 10px;
  padding-bottom: 10px;
}
svg{
  font-size: 18px !important;
}
.no-padding{
  padding: 0px;
}
#search .active{
  color: var(--yellow) !important;
  background: none;
}
#home .active{
  color: var(--yellow) !important;
  background: none;
}
#performer .active{
  color: var(--yellow) !important;
  background: none;
}
#albums .active{
  color: var(--yellow) !important;
  background: none;
}
#radio .active{
  color: var(--yellow) !important;
  background: none;
}
#favorites .active{
  color: var(--yellow) !important;
  background: none;
}

.radio-img{
  padding-bottom: 0px;
}

.container-fluid {
  padding: 0px;
}
.log-in-with .disabled {
  color: lightgrey !important;
}
.spotify-button {
  background-color: #1db954;
  border: none;
}
img {
  margin-left: 0px;
}
.navbar.navbar-dark.bg-dark {
  background-color: var(--dark-gray) !important;
}

.navbar-items a {
  color: var(--my-white) !important;
}
.menu-button a {
  padding-right: 0px !important;
}
.sidebar-text{
  font-size: 14px;
}
.avatar-button >>> .btn{
  border: none !important;
  padding: 0px !important;
  background: transparent !important;
  margin-left: 5px;
}
.search-icon{
  position: absolute;
  top: 21px;
  left: calc(165.3px + 600px + 38px);
  color: white;
}
.search-nav{
  width: 100% !important;
}
.omnisearch{
  background-color: var(--medium-gray) !important;
  width: 100% !important;
  margin-right: 30px;
  margin-left: 10px;
}
.form-control:focus{
  box-shadow: none; 
  -webkit-box-shadow: none;
}
input[type="search"]{
  padding-left: 31px !important;
}
input[type="search"]::-webkit-search-cancel-button {
  -webkit-appearance: none;
   height: 13px;
   width: 13px;
   background: url("data:image/svg+xml;charset=UTF-8,%3csvg viewPort='0 0 12 12' version='1.1' xmlns='http://www.w3.org/2000/svg'%3e%3cline x1='1' y1='11' x2='11' y2='1' stroke='white' stroke-width='2'/%3e%3cline x1='1' y1='1' x2='11' y2='11' stroke='white' stroke-width='2'/%3e%3c/svg%3e");
}
#search-results{
  position: absolute;
  top: 60px;
  left: calc(165.3px + 600px + 30px);
  z-index: 9999;
  width: calc(100% - 165.3px - 600px - 35px);
  box-shadow: rgba(0, 0, 0, 0.07) 0px 1px 2px, rgba(0, 0, 0, 0.07) 0px 2px 4px, rgba(0, 0, 0, 0.07) 0px 4px 8px, rgba(0, 0, 0, 0.07) 0px 8px 16px, rgba(0, 0, 0, 0.07) 0px 16px 32px, rgba(0, 0, 0, 0.07) 0px 32px 64px;
}
.spinner {
  text-align: center;
}
.m-5 {
    color: #9da6af;
}
.album-info-card {
  padding-left: 15px;
  padding-right: 15px;
  padding-top: 8px;
  padding-bottom: 10px;
  background-color: var(--my-white) !important;
  border: none !important;
}
.card-body {
  background-color: var(--my-white) !important;
  --scroll-bar-bg-color: var(--light-gray);
}
.info-card-text {
  font-size: 13px;
  line-height: 130%;
  overflow-y: scroll;
  max-height: 190px;
  padding-left: 2px;
}
.info-td {
  padding-left: 10px;
}
.born-died {
  font-size: 13px !important;
  color: grey !important;
}
.artist-name {
  color: black !important;
  font-weight: 600;
  font-size: 14px;
}
.artist-name:hover {
  color: black !important;
  text-decoration: underline !important;
  cursor: pointer;
}

/*scrollbars*/
.info-card-text {
  --scroll-bar-color: var(--scroll-color-light);
  --scroll-bar-bg-color: var(--my-white);
}
.info-card-text {
  scrollbar-width: thin;
  scrollbar-color: var(--scroll-bar-color) var(--scroll-bar-bg-color) !important;
}

/* Works on Chrome, Edge, and Safari */
.info-card-text::-webkit-scrollbar {
  width: 12px;
  height: 12px;
}
.info-card-text::-webkit-scrollbar-track {
  background: var(--scroll-bar-bg-color) !important;
}
.info-card-text::-webkit-scrollbar-thumb {
  background-color: var(--scroll-bar-color);
  border-radius: 20px;
  border: 3px solid var(--scroll-bar-bg-color) !important;
}

table {
  margin-bottom: 6px;
}
h6{
  padding-top: 5px;
}
</style>
