$(document).ready(function(){
  let namespace = "/test";
  let video = document.querySelector("#video");
  let canvas = document.querySelector("#canvas");
  let ctx = canvas.getContext('2d');

  var localMediaStream = null;

  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

  function sendImage() {
    if (!localMediaStream) {
      return;
    }

    ctx.drawImage(video, 0, 0, video.videoWidth, video.videoHeight, 0, 0, 300, 150);

    let dataURL = canvas.toDataURL('image/jpeg');
    socket.emit('input image', dataURL);
  }

  socket.on('connect', function() {
    console.log('Connected!');
  });

  var constraints = {
    video: {
      width: { min: 640 },
      height: { min: 480 }
    }
  };

  navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
    video.srcObject = stream;
    localMediaStream = stream;

        setInterval(function () {
          sendImage();
        }, 50);
      }).catch(function(error) {
        console.log(error);
      });
});

