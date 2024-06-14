import axios from "axios";

export function prepareTracksForSpotify(tracks) {
    let uriList = {};
    let jsonList = {};
    var smushTracks = tracks.replace(/\s/g, "");
    var cleanTracks = smushTracks.replaceAll("spotify", " spotify").trim();
    uriList["uris"] = cleanTracks.split(" ");
    jsonList = JSON.stringify(uriList);
    return jsonList;
}

export function addLineBreaksToParagraph(paragraph) {
  if (!paragraph) {
    return '';
  }
  // Remove existing line breaks
  let unbrokenText = paragraph.replace(/\n/g, "");
  let isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
  if (isSafari) { // Cant's use lookbehind regex in Safari
    return paragraph;
  } else {
    // Split the text into an array of sentences
    let regex = "/(?<![A-Z])(?<!No)(?<!Op)[.]/"
    let sentences = unbrokenText.split(eval(regex));
    // Initialize the result to the first sentence
    let result = sentences[0]
    // Loop through the remaining sentences, adding line breaks every 2 sentences
    for (let i = 1; i < sentences.length - 1; i++) {
      if (i % 2 === 0) {
        result += ".\n\n";
      } else {
        result += ". ";
      }
      result += sentences[i];
    }
    return result + ".";
  }
}

export function randomIntFromInterval(min, max) {
  // min and max included
  return Math.floor(Math.random() * (max - min + 1) + min);
}

export function msToHMS(ms) {
    let seconds = Math.floor(ms / 1000);
    let hours = Math.floor(seconds / 3600);
    seconds -= hours * 3600;
    let minutes = Math.floor(seconds / 60);
    seconds -= minutes * 60;

    // Pad minutes and seconds with a leading zero if they are single-digit.
    minutes = (hours > 0 && minutes < 10) ? '0' + minutes : minutes;
    seconds = (seconds < 10) ? '0' + seconds : seconds;

    let show_hours = ""
    if (hours < 1){
      show_hours = ""
    } else {
      show_hours = hours + ':'
    }

    return show_hours + minutes + ':' + seconds;
}

function matchOrchestra(name, description) {
  if (description == null) {
    description = "";
  }
  const orchestra_list = ['baroque', 'augsburger', 'antiqua', 'milano', 'quartet', 'orchest', 'philharm', 'symphony', 'concert', 'chamber', 'anonymous', 'academy', 'staats', 'consort', 'symphoniker', 'covent garden', 'akademie', 'stuttgart', 'llscher']
  for (var j = 0; j < orchestra_list.length; j++) {
    const regex = new RegExp(orchestra_list[j], 'i');
    if (regex.test(name.toLowerCase())) {
      return 5;
    }
    if (regex.test(description.toLowerCase())) {
      return 5;
    }
  }
  return 0;
}

export function getArtistDetails(personDict, peopleList, authKey) {
  const person = personDict['name'];
  let imageUrl = "";
  let spotifyImg = "";
  let description = personDict['description'];
  let rank = 0;
  if ('img' in personDict) {
    spotifyImg = personDict['img'];
  } else {
    spotifyImg = personDict['spotify_img'];
  }
  if ((spotifyImg != "NA") && (spotifyImg != null)) {
    imageUrl = spotifyImg;
    rank = rank + 1;
  }
  if(description != null){
    if (description.toLowerCase().includes('conductor')) {
      rank = rank + 20;
    }
  }

  const path = `https://kgsearch.googleapis.com/v1/entities:search?indent=true&types=Person&types=MusicGroup&query=${person} Music&limit=50&key=${authKey}`
  axios({
    method: "get",
    url: path,
  }).then((res) => {
    let wikiLink = "";
    let list = res.data.itemListElement;
    if (list[0] != null) {
      for (var i = 0; i < list.length; i++) {
        var personMatch = person.replace("Sir", "").replace("Dame", "").trim();
        if (list[i].result.name.includes(personMatch)) {
          if ((spotifyImg != "NA") && (spotifyImg != null)) {
            imageUrl = spotifyImg;
            rank = rank + 1;
          } else if ("image" in list[i].result) {
            imageUrl = list[i].result.image.contentUrl;
            rank = rank + 1;
          } else {
            imageUrl = "";
          }
          if (("description" in list[i].result) && (description == null)) {
            description = list[i].result.description;
            rank = rank + 1;
          }
          if(description != null){
            if (description.toLowerCase().includes('conductor')) {
              rank = rank + 20;
            }
          }
          rank = rank + matchOrchestra(person, description);
          try {
            if ("url" in res.data.itemListElement[i].result.detailedDescription) {
              wikiLink = res.data.itemListElement[i].result.detailedDescription.url;
            } else {
              wikiLink = null;
            }
          } catch (err) {
            wikiLink = null;
          }
          peopleList.push([person, description, imageUrl, rank, wikiLink]);
          peopleList.sort(function(a, b) {
            return b[3] - a[3];
          });
          break;
        }
        if (i == list.length - 1) {
          rank = rank + matchOrchestra(person, description);
          peopleList.push([person, description, imageUrl, rank, ""]);
          peopleList.sort(function(a, b) {
            return b[3] - a[3];
          });
        }
      }
    } else {
      rank = rank + matchOrchestra(person, description);
      peopleList.push([person, description, imageUrl, rank, ""]);
      peopleList.sort(function(a, b) {
        return b[3] - a[3];
      });
    }
  }).catch((error) => {
    console.error(error);
    rank = rank + matchOrchestra(person, description);
    peopleList.push([person, description, imageUrl, rank, ""]);
    peopleList.sort(function(a, b) {
      return b[3] - a[3];
    });
  });
}