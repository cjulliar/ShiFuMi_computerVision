var width, height, intervalID
var streaming = false
var started = false

video.addEventListener(
  "canplay",
  (ev) => {
    width = video.videoWidth
    height = video.videoHeight
    if (!streaming) {
      video.setAttribute("width", width);
      video.setAttribute("height", height);
      canvas.setAttribute("width", width);
      canvas.setAttribute("height", height);
      boxes.setAttribute("width", width);
      boxes.setAttribute("height", height);
      streaming = true
    }
  },
  false,
)

// Fonction pour capturer une image de la webcam
function captureFrame() {
  ctx.drawImage(video, 0, 0, width, height);

  // Convertir l'image en données JPEG
  const data = canvas.toDataURL('image/jpeg');

  // Envoyer les données JPEG au serveur Python
  fetch('http://localhost:8001/send-frame', {
    method: 'POST',
    body: data
  })
    .then(response => response.json())
    .then(data => {
      ctxBoxes.clearRect(0, 0, width, height)
      ctxBoxes.beginPath()

      data = JSON.parse(data)
      console.log('Détection YOLO:', data);
      if (data.length > 0) drawBoxes(data)
    })
    .catch(error => {
      console.error('Error sending frame:', error);
    });
}

function drawBoxes(boxes) {
  for (let i = 0; i < boxes.length; i++) {
    ctxBoxes.rect(boxes[i].box.x1, boxes[i].box.y1, boxes[i].box.x2, boxes[i].box.y2);
    ctxBoxes.lineWidth = "3";
    ctxBoxes.strokeStyle = "red";
    ctxBoxes.stroke();
  }
}

bt.addEventListener('click', function (e) {
  started = !started
  if (!started) {
    e.target.innerText = 'Start'
    clearInterval(intervalID)
  } else {
    e.target.innerText = 'Stop'
    intervalID = setInterval(captureFrame, 350);
  }
})