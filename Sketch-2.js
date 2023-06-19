let buttonNames = ["Mahan", "Kostas", "Martin", "Sarah", "Dave"];
let buttons = [];
let buttonStates = [false, false, false, false, false];
let images = [];
let data;
let selectedNames = [];
let submitClicked = false; // new variable

function setup() {
  createCanvas(1920, 500);
  for (let i = 0; i < buttonNames.length; i++) {
    buttons[i] = createButton(buttonNames[i]);
    buttons[i].style('background-color', 'lightgray');
    buttons[i].mousePressed(() => {
      buttonStates[i] = !buttonStates[i];
      buttons[i].style('background-color', buttonStates[i] ? 'blue' : 'lightgray');
      updateSelectedNames();
    });
  }
  submitButton = createButton('Submit');
  submitButton.style('background-color', 'gray');
  submitButton.mousePressed(loadImages);
  submitButton.mouseOver(() => {
    if (selectedNames.length === 3) {
      submitButton.style('background-color', 'green');
      //redraw()
    }
  });
  submitButton.mouseOut(() => submitButton.style('background-color', 'gray'));
  noLoop();
  setInterval(loadImages, 10000);
}

function updateSelectedNames() {
  selectedNames = [];
  for (let i = 0; i < buttonStates.length; i++) {
    if (buttonStates[i]) selectedNames.push(buttonNames[i]);
    
  }
  if (selectedNames.length <= 3) {
    submitButton.style('background-color', 'gray');
    submitButton.style('visibility', 'visible');
    //redraw()
    
  } else {
    submitButton.style('background-color', 'gray');
    submitButton.style('visibility', 'hidden');
  }
}

function loadImages() {
    if (selectedNames.length !== 3) {
      console.log("Please select exactly 3 names before submitting");
      return;
    }
    loadJSON('speakers.json', function(loadedData) {
      data = loadedData;
      images = []; 
      for (let i = 0; i < data.length; i++) {
        if (selectedNames.includes(data[i].id)) {
          loadImage(data[i].image, 
            img => {
              console.log('Image loaded successfully', img);
              images[i] = img;
              loop();  // resume the draw loop
            },
            err => {
              console.error('Error loading image', err);
            }
          );
        }
      }
    });
  }
  
  

function draw() {
    console.log('draw function running')
    background(220);
    let x = 0;
    if(submitClicked){ // only draw images if submit was clicked
        for (let name of selectedNames) {
          // ... rest of your drawing code ...
        }
      }
    // loop over each selected name
    console.log('selectedNames:', selectedNames);
    for (let name of selectedNames) {
      console.log(selectedNames);
      console.log("for1");
      console.log(data.length)
      // find the matching data for this name and draw the image if found
      for (let i = 0; i < data.length; i++) {
        console.log("for2");

        console.log(`data[i].id: ${data[i].id}, name: ${name}, images[i]: ${images[i]}`);

        if (data[i].id === name && images[i]) {
            console.log("ifyes");
          console.log(`Drawing image for ${name}`);
          tint(255, (data[i].weight) * 8);
          //tint(255, 255);
          image(images[i], x, 50);
          x += images[i].width;
        }
      }
    }
  }
  