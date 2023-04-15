export function getPersonDetails(person_name, authKey) {
  const person = person_name;
  let description = "";

  const path = `https://kgsearch.googleapis.com/v1/entities:search?indent=true&types=Person&types=MusicGroup&query=${person} Music&limit=50&key=${authKey}`
  axios({
    method: "get",
    url: path,
  }).then((res) => {
    let list = res.data.itemListElement;
    if (list[0] != null) {
      for (var i = 0; i < list.length; i++) {
        var personMatch = person.replace("Sir", "").replace("Dame", "").trim();
        if (list[i].result.name.includes(personMatch)) {
          if ("description" in list[i].result) {
            description = list[i].result.description;
          } else {
            description = "NA";
          }
        }
      }
    } else {
      description = "NA";
    }
    return description;
  }).catch((error) => {
    console.log(error);
    return null;
  });
}