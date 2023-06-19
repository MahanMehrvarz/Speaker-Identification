let data;
let images = [];

function preload() {
  loadImages();
  setInterval(loadImages, 5000); // Reload the data every 5 seconds
}

function loadImages() {
  loadJSON('speakers.json', function(loadedData) {
    data = loadedData;
    images = []; // Clear the old images
    for (let i = 0; i < data.length; i++) {
      images[i] = loadImage(data[i].image);
    }
  });
}

function setup() {
  createCanvas(1920, 400);
}

function draw() {
  background(220);
  let x = 0;
  for (let i = 0; i < images.length; i++) {
    if (images[i]) {
      tint(255,(data[i].weight)*10)
      image(images[i], x, 0);
      x += images[i].width;
    }
  }
}
