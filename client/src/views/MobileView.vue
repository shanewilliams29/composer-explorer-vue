<template>
  <div id="home">
  <div role="tablist">
    <b-card no-body class="mb-1 mobile-card">
      <b-card-header header-tag="header" class="p-1" role="tab" v-show="!$view.mobileKeyboard">
        <b-button class="header-button" :disabled="composerDisabled" @click="composerToggle" block variant="secondary"><span class="heading-text">Composers</span><span class="mb-0 float-right"><b-icon-chevron-down></b-icon-chevron-down></span></b-button>
      </b-card-header>
      <b-collapse :visible="composerDisabled" id="accordion-1" accordion="my-accordion" role="tabpanel">
        <b-card-body>
          <b-col class="composer-list-mobile disable-scrollbars">
            <ComposerHeading />
            <ComposerList />
          </b-col>
        </b-card-body>
      </b-collapse>
    </b-card>

    <b-card no-body class="mb-1 mobile-card">
      <b-card-header header-tag="header" class="p-1" role="tab" v-show="!$view.mobileKeyboard">
        <b-button class="header-button" :disabled="workDisabled" block @click="workToggle" variant="secondary"><span class="heading-text">Works by {{ composer }}</span><span class="mb-0 float-right"><b-icon-chevron-down></b-icon-chevron-down></span></b-button>
      </b-card-header>
      <b-collapse :visible="workDisabled" id="accordion-2" accordion="my-accordion" role="tabpanel">
        <b-card-body>
          <b-col class="work-list-mobile disable-scrollbars">
            <WorkHeading />
            <WorkList/>
          </b-col>
        </b-card-body>
      </b-collapse>
    </b-card>

    <b-card no-body class="mb-1 mobile-card">
      <b-card-header header-tag="header" class="p-1" role="tab" v-show="!$view.mobileKeyboard">
        <b-button class="header-button last-button" :disabled="albumDisabled" @click="albumToggle" block variant="secondary"><span class="heading-text">{{ title }}</span><span class="mb-0 float-right"><b-icon-chevron-down></b-icon-chevron-down></span></b-button>
      </b-card-header>
      <b-collapse :visible="albumDisabled" id="accordion-3" accordion="my-accordion" role="tabpanel">
        <b-card-body>
          <b-col class="album-list-mobile disable-scrollbars">
           <AlbumHeading />
           <AlbumList/>
          </b-col>
        </b-card-body>
      </b-collapse>
    </b-card>
  </div>
  </div> 
</template>

<script>
import ComposerList from '@/components/ComposerList.vue'
import WorkList from '@/components/WorkList.vue'
import AlbumList from '@/components/AlbumList.vue'
import ComposerHeading from '@/components/subcomponents/ComposerHeading.vue'
import WorkHeading from '@/components/subcomponents/WorkHeading.vue'
import AlbumHeading from '@/components/subcomponents/AlbumHeading.vue'
import {eventBus} from "../main.js";

export default {
  name: 'MobileView',
  components: {
    ComposerList,
    WorkList,
    AlbumList,
    ComposerHeading,
    WorkHeading,
    AlbumHeading
  },
  data() {
    return {
      composer: this.$config.composer,
      title: this.$config.workTitle,
      composerDisabled: true,
      workDisabled: false,
      albumDisabled: false,
      initialWorksLoad: true,
      initialAlbumsLoad: true,
      composerListKey: 0
    };
  },
  methods: {
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
  beforeCreate(){
    this.$view.mobile = true;
    this.$config.albumSize = 'small';
  },
  created() {
    this.$view.mode = null;
    window.firstLoad = true; // prevent playback on first load
    eventBus.$on('fireComposers', (composer) => {
        this.composer = composer;
        this.workToggle();
    })
    // eventBus.$on('fireWorksLoaded', () => {
    //   if (this.initialWorksLoad != true){
    //     this.workToggle();
    //   } else{
    //     this.initialWorksLoad = false;
    //   }
    // })
    // eslint-disable-next-line
    eventBus.$on('fireAlbums', () => {
          this.title = this.$config.workTitle;
          this.albumToggle();
    })
    eventBus.$on('fireAlbumsAndPlay', () => {
          this.title = this.$config.workTitle;
    })
    // eslint-disable-next-line
    // eventBus.$on('fireAlbumData', (work_id, title) => {
    //     this.title = this.hold_title;
    // })
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
  },
}
</script>

<style>
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

<style scoped>
  >>> .card{
    color: #343a40;
  }
  >>> .composer-card{
    margin-left: -15px;
    margin-right: -10px;
  }
  >>> .work-card{
    margin-left: -15px;
    margin-right: -10px;
  }
  >>> .albums-card{
    margin-left: -15px;
    margin-right: -10px;
    padding-top: 6.5px !important;
  }
/* .playback-container{
    padding: 13px;
    padding-top: 3px !important;
    padding-bottom: 0px;
    font-size: 14px;
  }*/
  .heading-text{
    padding-left: 20px;
  }
  .heading-card{
    background: #54595f !important;
    padding-top:  10px;
    padding-right: 5px;
    margin-right: -15px;
    border-radius: 0px;
  }
  .card-body{
    background: #54595f !important;
    padding: 0px !important;
  }

  .btn-secondary{
    background-color: #343a40 !important;
    text-align: middle;
  }
/*  .btn-secondary:hover{
    background-color: #717579 !important;
  }*/

  .btn.disabled, .btn:disabled {
    opacity: 1;
}

  .card-header{
    border: 0px !important;
  }
  .btn{
    border:  0px;
  }
  .header-button{
    border-radius: 0px !important;
    border-top: solid 2px #54595f !important;
      outline: none !important;
      box-shadow: none !important;
  }
  .last-button{
    border-bottom: solid 2px #54595f !important;
  }
  .p-1{
    padding: 0px !important;
    border-radius: 0px !important;
  }
  .mb-1{
    border: none;
    margin: 0px !important;
  }
>>> .highlight{
  background-color: var(--blue);
}
>>> .highlight td{
  background-color: var(--blue);
}
>>> .music-note{
  color: var(--blue);
}
.disable-scrollbars::-webkit-scrollbar {
  background: transparent; /* Chrome/Safari/Webkit */
  width: 0px;
}
    
.disable-scrollbars {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none;  /* IE 10+ */
}
</style>