export function addLineBreaksToParagraph(paragraph){
  // Remove existing line breaks
  let unbrokenText = paragraph.replace(/\n/g, "");

  let isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);

  if (isSafari) { // Cant's use lookbehind regex in Safari
    return unbrokenText;

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