import axios from 'axios';
import {eventBus} from "./main.js";

var spotify = {

// may need to use flask endpoint for this
pressPlay(token, device_id) {
  const path = 'https://api.spotify.com/v1/me/player/play';
  axios({
      method: 'put',
      url: path,
      params: {
        'device_id' : device_id
      },
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      }
    })
    .then((res) => {
      if (res.status == 204) {
        eventBus.$emit('fireNowPlaying');
      } else {
        eventBus.$emit('fireNowPaused');
      }
    })
    .catch((error) => {
      console.error(error);
    });
},

pauseTrack(token) {
  const path = 'https://api.spotify.com/v1/me/player/pause';
  axios({
      method: 'put',
      url: path,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      }
    })
    .then((res) => {
      if (res.status == 204) {
        eventBus.$emit('fireNowPaused');
      } else {
        eventBus.$emit('fireNowPlaying');
      }
    })
    .catch((error) => {
      console.error(error);
    });
},

beginningTrack(token) {
  const path = 'https://api.spotify.com/v1/me/player/seek?position_ms=0';
  axios({
      method: 'put',
      url: path,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      }
    })
    .then((res) => {
      if (res.status == 204) {
        eventBus.$emit('fireNowPlaying');
      } else {
        eventBus.$emit('fireNowPaused');
      }
    })
    .catch((error) => {
      console.error(error);
    });
},

nextTrack(token) {
  const path = 'https://api.spotify.com/v1/me/player/next';
  axios({
      method: 'post',
      url: path,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      }
    })
    .then((res) => {
      if (res.status == 204) {
        eventBus.$emit('fireNowPlaying');
        this.getCurrentPlayerInfo(token);
      } else {
        eventBus.$emit('fireNowPaused');
      }
    })
    .catch((error) => {
      console.error(error);
    });
},

playTracks(token, device_id, tracks) {
  const path = 'https://api.spotify.com/v1/me/player/play';
  axios({
      method: 'put',
      url: path,
      data: tracks,
      params: {
        'device_id' : device_id
      },
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      }
    })
    .then((res) => {
      if (res.status == 204) {
        eventBus.$emit('fireNowPlaying');
        this.getCurrentPlayerInfo(token);
      } else {
        eventBus.$emit('fireNowPaused');
      }
    })
    .catch((error) => {
      console.error(error);
    });
},

getCurrentPlayerInfo(token) {
  const path = 'https://api.spotify.com/v1/me/player';
  axios({
      method: 'get',
      url: path,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      }
    })
    .then((res) => {
      if (res.status == 200) {
        eventBus.$emit('fireCurrentPlayerInfo', res.data);
      } else {
        eventBus.$emit('fireNowPaused');
      }
    })
    .catch((error) => {
      console.error(error);
    });
},
seekToPosition(token, position) {
  const path = 'https://api.spotify.com/v1/me/player/seek?position_ms=' + position;
  axios({
      method: 'put',
      url: path,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      }
    })
    .then((res) => {
      if (res.status == 204) {
        eventBus.$emit('fireSeekToPosition');
      } else {
        this.getCurrentPlayerInfo(token);
      }
    })
    .catch((error) => {
      console.error(error);
    });
},
}

export default spotify
