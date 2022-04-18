<template>
  <div id="home">
    <NavBar/>

  <div role="tablist">
    <b-card no-body class="mb-1 mobile-card">
      <b-card-header header-tag="header" class="p-1" role="tab">
        <b-button class="header-button" :disabled="composerDisabled" @click="composerToggle" block variant="secondary"><span class="heading-text">Composers</span><span class="mb-0 float-right"><b-icon-chevron-down></b-icon-chevron-down></span></b-button>
      </b-card-header>
      <b-collapse :visible="composerDisabled" id="accordion-1" accordion="my-accordion" role="tabpanel">
        <b-card-body>
<b-col class="composer-list-mobile"><ComposerList/></b-col>
        </b-card-body>
      </b-collapse>
    </b-card>

    <b-card no-body class="mb-1 mobile-card">
      <b-card-header header-tag="header" class="p-1" role="tab">
        <b-button class="header-button" :disabled="workDisabled" block @click="workToggle" variant="secondary"><span class="heading-text">Works by {{ composer }}</span><span class="mb-0 float-right"><b-icon-chevron-down></b-icon-chevron-down></span></b-button>
      </b-card-header>
      <b-collapse :visible="workDisabled" id="accordion-2" accordion="my-accordion" role="tabpanel">
        <b-card-body>
<b-col class="work-list-mobile"><WorkList/></b-col>
        </b-card-body>
      </b-collapse>
    </b-card>

    <b-card no-body class="mb-1 mobile-card">
      <b-card-header header-tag="header" class="p-1" role="tab">
        <b-button class="header-button last-button" :disabled="albumDisabled" @click="albumToggle" block variant="secondary"><span class="heading-text">{{ title }}</span><span class="mb-0 float-right"><b-icon-chevron-down></b-icon-chevron-down></span></b-button>
      </b-card-header>
      <b-collapse :visible="albumDisabled" id="accordion-3" accordion="my-accordion" role="tabpanel">
        <b-card-body>
 <b-col class="album-list-mobile"><AlbumList/></b-col>
        </b-card-body>
      </b-collapse>
    </b-card>
  </div>
<div id="footer">
    <MobileTracks/>
    <PageFooter/>
</div>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'
import ComposerList from '@/components/ComposerList.vue'
import WorkList from '@/components/WorkList.vue'
import AlbumList from '@/components/AlbumList.vue'
import MobileTracks from '@/components/mobile/MobileTracks.vue'
import PageFooter from '@/components/mobile/PageFooter.vue'
import axios from 'axios';
import {eventBus} from "../main.js";
import {currentConfig} from "../main.js";

export default {
  name: 'MobileView',
  components: {
    NavBar,
    ComposerList,
    WorkList,
    AlbumList,
    MobileTracks,
    PageFooter
  },
  data() {
    return {
      composer: currentConfig.composer,
      title: currentConfig.workTitle,
      // hold_title: "Piano Concerto No. 5 in E♭ major",
      composerDisabled: true,
      workDisabled: false,
      albumDisabled: false,
      initialWorksLoad: true,
      initialAlbumsLoad: true
    };
  },
  methods: {
    getSpotifyToken() {
      const path = 'api/get_token';
      axios.get(path)
        .then((res) => {
          if (res.data.status == "success") {
            if (res.data.client_token !== null) {
              eventBus.$emit('fireLogIn', currentConfig.loggedIn);
              window.token = res.data.client_token;
            } else {
              window.token = res.data.app_token;
            }
          }
          console.log(window.token);
        })
        .catch((error) => {
          window.token = null;
          console.error(error);
        });
    },
      composerToggle() {
        this.composerDisabled = true;
        this.workDisabled = false;
        this.albumDisabled = false;
      },
      workToggle() {
        this.composerDisabled = false;
        this.workDisabled = true;
        this.albumDisabled = false;

      },
      albumToggle() {
        this.composerDisabled = false;
        this.workDisabled = false;
        this.albumDisabled = true;
      },
  },
  created() {
    this.getSpotifyToken();
    eventBus.$on('fireComposers', (composer) => {
        this.composer = composer;
    })
    eventBus.$on('fireWorksLoaded', () => {
      if (this.initialWorksLoad != true){
        this.workToggle();
      } else{
        this.initialWorksLoad = false;
      }
    })
    // eslint-disable-next-line
    eventBus.$on('fireAlbums', (work_id, title) => {
          this.title = title;
          this.albumToggle();
    })
    // eslint-disable-next-line
    // eventBus.$on('fireAlbumData', (work_id, title) => {
    //     this.title = this.hold_title;
    // })
    let vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);

    window.addEventListener('resize', () => {
    // We execute the same script as before
      let vh = window.innerHeight * 0.01;
      document.documentElement.style.setProperty('--vh', `${vh}px`);
    });
  },

}
</script>

<style>
  #app{
    height: 100% !important;
    max-height: -webkit-fill-available !important;
  }
  .heading-text{
    padding-left: 20px;
  }
  .card-body{
    background: #f1f2f4 !important;
    padding: 0px !important;
  }
  #home{
    overflow-x: hidden;
    background: #f1f2f4 !important;
  }
  .btn-secondary{
    background-color: #343a40 !important;
    text-align: middle;
  }
  .btn-secondary:hover{
    background-color: #717579 !important;
  }

  .card-header{
    border: 0px !important;
  }
  .btn{
    border:  0px;
  }
  .header-button{
    border-radius: 0px !important;
    border-top: solid 2px white !important;
      outline: none !important;
      box-shadow: none !important;
  }
  .last-button{
    border-bottom: solid 2px white !important;
  }
  .p-1{
    padding: 0px !important;
    border-radius: 0px !important;
  }
  .mb-1{
    border: none;
    margin: 0px !important;
  }
  .composer-list-mobile{
    /*height: calc(100vh - 314px);*/
    height: calc(var(--vh, 1vh) * 100 - 314px + 8.5px);
    overflow-y: scroll;
  }
  .composer-list-mobile .composer-img{
    /*height: calc(100vh - 314px);*/
      height:  25px;
      width: 25px;
  }
  .composer-list-mobile .card{
    margin-bottom: 0px !important;
  }
  .composer-list-mobile table td{
    padding-top: 2px;
    padding-bottom: 2px;
    font-size: 14px !important;
    vertical-align: middle;
  }
  .work-list-mobile{
    /*height: calc(100vh - 314px);*/
    height: calc(var(--vh, 1vh) * 100 - 314px + 8.5px);
    overflow-y: scroll;
  }
  .work-list-mobile .card{
    margin-bottom: 0px !important;
  }
  .work-list-mobile table td{
    padding-top: 5px;
    padding-bottom: 5px;
    font-size: 14px !important;
  }
  .album-list-mobile{
    /*height: calc(100vh - 314px);*/
    height: calc(var(--vh, 1vh) * 100 - 314px + 8.5px);
    overflow-y: scroll;
    overflow-x: hidden;
  }
  .album-list-mobile .card{
    margin-bottom: 0px !important;
  }

  .album-list-mobile table{
    padding-top: 3px;
    font-size: 14px !important;
  }

  #footer{
    height: 124px;
    overflow-x: hidden;
    overflow-y: hidden;
  }

  #footer table{
    font-size: 14px !important;
    line-height: 130%;
  }

</style>
