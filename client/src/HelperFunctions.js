import axios from "axios";

export function addLineBreaksToParagraph(paragraph){

  if(!paragraph){
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

// Gets person info from Google API and adds to peopleList
export function getPeopleInfoFromGoogle(person, peopleList, authKey) {
    const path = `https://kgsearch.googleapis.com/v1/entities:search?indent=true&types=Person&types=MusicGroup&query=${person} Music&limit=50&key=${authKey}`
      axios({
        method: "get",
        url: path,
      })
        .then((res) => {
          let imageUrl = "";
          let description = "";
          let wikiLink = "";
          let list = res.data.itemListElement;

          if (list[0] != null) {
            for (var i = 0; i < list.length; i++) {

              var personMatch = person.replace("Sir", "").replace("Dame", "").trim();
              if (list[i].result.name.includes(personMatch)) {
                let rank = 0;

                if ("image" in list[i].result) {
                  imageUrl = list[i].result.image.contentUrl;
                  rank = rank + 1;
                } else {
                  imageUrl = "";
                }

                if ("description" in list[i].result) {
                  description = list[i].result.description;
                  rank = rank + 1;
                  if (description.toLowerCase().includes('conductor')) {
                    rank = rank + 10;
                  }
                } else {
                  description = "";
                }

                if ("url" in res.data.itemListElement[i].result.detailedDescription) {
                  wikiLink = res.data.itemListElement[i].result.detailedDescription.url;
                } else {
                  wikiLink = null;
                }

                  peopleList.push([person, description, imageUrl, rank, wikiLink]);
                    peopleList.sort(function (a, b) {
                  return b[3] - a[3];
                  });

                break;
              }

              if (i == list.length - 1) {
                peopleList.push([person, "", "", -1, ""]);
                peopleList.sort(function (a, b) {
                  return b[3] - a[3];
                });
              }
            }
          } else {
            peopleList.push([person, "", "", -1, ""]);
            peopleList.sort(function (a, b) {
              return b[3] - a[3];
            });
          }
        })
      .catch((error) => {
        console.error(error);
        peopleList.push([person, "", "", -1, ""]);
        peopleList.sort(function (a, b) {
          return b[3] - a[3];
        });
      });
    }


// Gets person info from Google API and adds to peopleList
export function getArtistDetails(personDict, peopleList, authKey) {
    const person = personDict['name'];
    const spotifyImg = personDict['spotify_img'];
    const path = `https://kgsearch.googleapis.com/v1/entities:search?indent=true&types=Person&types=MusicGroup&query=${person} Music&limit=50&key=${authKey}`
    console.log(personDict);
      axios({
        method: "get",
        url: path,
      })
        .then((res) => {
          let imageUrl = "";
          let description = "";
          let wikiLink = "";
          let list = res.data.itemListElement;

          if (list[0] != null) {
            for (var i = 0; i < list.length; i++) {

              var personMatch = person.replace("Sir", "").replace("Dame", "").trim();
              if (list[i].result.name.includes(personMatch)) {
                let rank = 0;

                if ("image" in list[i].result) {
                  imageUrl = list[i].result.image.contentUrl;
                  rank = rank + 2;
                  console.log('GOOGLE IMAGE');
                } else if (spotifyImg){
                  imageUrl = spotifyImg;
                  console.log('SPOTIFY IMAGE');
                  rank = rank + 1;
                } else {
                  imageUrl = "";
                  console.log('NO IMAGE');
                }

                if ("description" in list[i].result) {
                  description = list[i].result.description;
                  rank = rank + 1;
                  if (description.toLowerCase().includes('conductor')) {
                    rank = rank + 10;
                  }
                } else {
                  description = "";
                }

                try {
                  if ("url" in res.data.itemListElement[i].result.detailedDescription) {
                    wikiLink = res.data.itemListElement[i].result.detailedDescription.url;
                  } else {
                    wikiLink = null;
                  }
                }
                catch(err) {
                  wikiLink = null;
                }


                  peopleList.push([person, description, imageUrl, rank, wikiLink]);
                    peopleList.sort(function (a, b) {
                  return b[3] - a[3];
                  });

                break;
              }

              if (i == list.length - 1) {
                peopleList.push([person, "", "", -1, ""]);
                peopleList.sort(function (a, b) {
                  return b[3] - a[3];
                });
              }
            }
          } else {
            peopleList.push([person, "", "", -1, ""]);
            peopleList.sort(function (a, b) {
              return b[3] - a[3];
            });
          }
        })
      .catch((error) => {
        console.error(error);
        peopleList.push([person, "", "", -1, ""]);
        peopleList.sort(function (a, b) {
          return b[3] - a[3];
        });
      });
    }