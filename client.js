var pc = null;
var serverUrl = '/webrtc';
const config = { sdpSemantics: 'unified-plan', iceServers: [{ urls: ['stun:stun.l.google.com:19302'] }] };

let frameCount = 0; // Frame counter
let lastTimestamp = performance.now(); // Last timestamp

async function fetchFromServer(type, data) {
    const response = await fetch(serverUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    return response.json();
}

async function negotiate() {
    const offerResponse = await fetchFromServer('request', { 
        type: 'request', 
        video_transform: document.getElementById('video-transform').value
    });
    
    if (offerResponse.error) {
        console.error('Error requesting offer:', offerResponse.error);
        return;
    }

    const offer = new RTCSessionDescription({
        sdp: offerResponse.sdp,
        type: offerResponse.type
    });

    await pc.setRemoteDescription(offer);

    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);

    const answerResponse = await fetchFromServer('answer', {
        type: pc.localDescription.type,
        sdp: pc.localDescription.sdp,
        id: offerResponse.id
    });

    if (answerResponse.error) {
        console.error('Error sending answer:', answerResponse.error);
    }
}

function calculateFPS() {
    const now = performance.now();
    frameCount++;

    if (now - lastTimestamp >= 1000) {
        const fps = frameCount; // Calculate FPS
        document.getElementById('fpsCount').innerText = `FPS: ${fps}`;
        frameCount = 0; // Reset count
        lastTimestamp = now; // Update timestamp
    }

    requestAnimationFrame(calculateFPS);
}

function start() {
    pc = new RTCPeerConnection(config);

    pc.addEventListener('track', (evt) => {
        if (evt.track.kind == 'video') {
            document.getElementById('video').srcObject = evt.streams[0];
            const videoElement = document.getElementById('video');
            videoElement.addEventListener('playing', () => {
                requestAnimationFrame(calculateFPS); // Start FPS calculation
            });
        } else {
            document.getElementById('audio').srcObject = evt.streams[0];
        }
    });

    document.getElementById('start').style.display = 'none';
    negotiate();
    document.getElementById('stop').style.display = 'inline-block';
}

function stop() {
    document.getElementById('stop').style.display = 'none';

    setTimeout(() => {
        if (pc) {
            pc.close();
            pc = null;
        }
    }, 500);
}
