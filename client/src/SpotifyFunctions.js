import axios from 'axios';
import {eventBus} from "@/main.js";
import {startTracks} from "@/main.js";
import { prepareTracksForSpotify } from "@/HelperFunctions.js";

var spotify = {
  getSpotifyAlbum(token, album) {
    const path = 'https://api.spotify.com/v1/albums/' + album;
    axios({
      method: 'get',
      url: path,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      }
    }).then((res) => {
      eventBus.$emit('fireSpotifyAlbumData', res.data);
    }).catch((error) => {
      console.error(error);
    });
  }, 
  getSpotifyArtists(token, artistIdString) {
    const path = 'https://api.spotify.com/v1/artists?ids=' + artistIdString;
    axios({
      method: 'get',
      url: path,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      }
    }).then((res) => {
      eventBus.$emit('fireSpotifyArtistList', res.data.artists);
    }).catch((error) => {
      console.error(error);
    });
  },
  pressPlay(token, device_id) {
    const path = 'https://api.spotify.com/v1/me/player/play';
    axios({
      method: 'put',
      url: path,
      params: {
        'device_id': device_id
      },
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      }
    // eslint-disable-next-line
    }).then((res) => {
    // eslint-disable-next-line
    }).catch((error) => {
      // fails on first play of new startup, play from localstorage
      let jsonTracks = prepareTracksForSpotify(startTracks)
      this.playTracks(token, device_id, jsonTracks);
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
    // eslint-disable-next-line
    }).then((res) => {
    }).catch((error) => {
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
    }).then((res) => {
      if (res.status == 204) {
        this.pressPlay(token, window.device_id);
      }
    }).catch(function(error) {
      if (error.response.status == 401) {
        eventBus.$emit('notLoggedIn');
      } else {
        console.error(error);
      }
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
    }).then((res) => {
      if (res.status == 204) {
        this.pressPlay(token, window.device_id);
      }
    }).catch(function(error) {
      if (error.response.status == 401) {
        eventBus.$emit('notLoggedIn');
      } else {
        console.error(error);
      }
    });
  },
  playTracks(token, device_id, tracks) {
    const path = 'https://api.spotify.com/v1/me/player/play';
    axios({
      method: 'put',
      url: path,
      data: tracks,
      params: {
        'device_id': device_id
      },
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      }
    // eslint-disable-next-line
    }).then((res) => {

    }).catch(function(error) {
      if (error.response.status == 401) {
        eventBus.$emit('notLoggedIn');
      } else if (error.response.status == 404 || error.response.status == 502){
        eventBus.$emit('notAvailable');
      } else if (error.response.status == 500 || error.response.status == 503){
        eventBus.$emit('spotifyFail');
      } else {
        console.error(error);
      }
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
    }).then((res) => {
      if (res.status == 200) {
        eventBus.$emit('fireCurrentPlayerInfo', res.data);
      }
    }).catch((error) => {
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
    }).then((res) => {
      if (res.status == 204) {
        eventBus.$emit('fireSeekToPosition');
      } else {
        this.getCurrentPlayerInfo(token);
      }
    }).catch((error) => {
      console.error(error);
    });
  },
}

export default spotify
