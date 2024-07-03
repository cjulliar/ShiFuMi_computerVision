var width, height, intervalID
var streaming = false
var started = false
var lastShifumi = []
// Durée du compte à rebours en secondes
const duration = 5; // 60 secondes par défaut
var intervalRebours;

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
      if (data.length == 2) lastShifumi = data
      //console.log('Détection YOLO:', data);
      //if (data.length > 0) drawBoxes(data)
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

function rules(c1, c2) {
  if (c1 == 0 && c2 == 1) return true   // papier // rock
  if (c1 == 0 && c2 == 2) return false  // papier // ciseau
  if (c1 == 1 && c2 == 0) return false  // rock // papier
  if (c1 == 1 && c2 == 2) return true   // rock // ciseau
  if (c1 == 2 && c2 == 0) return true   // ciseau // papier
  if (c1 == 2 && c2 == 1) return false  // ciseau // rock

  return -1
}

function score() {
  console.log(lastShifumi)
  var centers = []
  for (let i = 0; i < lastShifumi.length; i++) {
    const { x1, y1, x2, y2 } = lastShifumi[i].box
    centers.push({ pos: getRectangleCenter(x1, y1, x2, y2), class: lastShifumi[i].class })
  }

  var rightSide = (centers[0].pos.x > 320) ? centers[0] : centers[1]
  var leftSide = (centers[0].pos.x <= 320) ? centers[0] : centers[1]
  console.log(rightSide.class, leftSide.class)
  var win = rules(rightSide.class, leftSide.class)

  if (win == -1) return
  if (win)
    scoreLeft.textContent = parseInt(scoreLeft.textContent) + 1
  else
    scoreRight.textContent = parseInt(scoreRight.textContent) + 1
}


var remainingSeconds
// Fonction pour mettre à jour le compte à rebours
function updateCountdown() {
  // Décrémenter le nombre de secondes restantes
  remainingSeconds--;

  // Afficher le temps restant (secondes uniquement)
  bt.textContent = remainingSeconds;

  // Vérifier si le compte à rebours est terminé
  if (remainingSeconds == 0) {
    clearInterval(intervalRebours);
    intervalRebours = null
    bt.click()
    score()
  }
}

function getRectangleCenter(topLeftX, topLeftY, bottomRightX, bottomRightY) {
  // Vérifier les valeurs d'entrée
  if (topLeftX > bottomRightX || topLeftY > bottomRightY) {
    throw new Error("Les coordonnées du rectangle ne sont pas valides.");
  }

  // Calculer les coordonnées du centre
  const centerX = (topLeftX + bottomRightX) / 2;
  const centerY = (topLeftY + bottomRightY) / 2;

  // Retourner le point central
  return { x: centerX, y: centerY };
}


bt.addEventListener('click', function (e) {
  started = !started
  if (!started) {
    e.target.innerText = 'Start'
    clearInterval(intervalID)
  } else {
    e.target.innerText = 'Stop'
    intervalID = setInterval(captureFrame, 350);

    if (!intervalRebours) {
      bt.textContent = duration
      remainingSeconds = duration;
      // Démarrer le compte à rebours
      intervalRebours = setInterval(updateCountdown, 1000);
    }
  }
})