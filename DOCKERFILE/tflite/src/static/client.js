var serverUrl = '/webrtc';
const config = { sdpSemantics: 'unified-plan', iceServers: [{ urls: ['stun:stun.l.google.com:19302'] }] };
var pc = new RTCPeerConnection(config);

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
    // Send a request to create an offer
    const offerResponse = await fetchFromServer('request',{ 
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

    // Create an answer
    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);

    // Send the answer to the server
    const answerResponse = await fetchFromServer('answer', {
        type: pc.localDescription.type,
        sdp: pc.localDescription.sdp,
        id: offerResponse.id
    });

    if (answerResponse.error) {
        console.error('Error sending answer:', answerResponse.error);
    }
}

function start() {
    //pc = new RTCPeerConnection(config);

    // Handle incoming tracks
    pc.addEventListener('track', (evt) => {
        if (evt.track.kind == 'video') {
            document.getElementById('video').srcObject = evt.streams[0];
        } else {
            document.getElementById('audio').srcObject = evt.streams[0];
        }
    });

    document.getElementById('start').style.display = 'none';
    negotiate();
}

async function get_home_IP() {
    try {
        const response = await fetch('/get-ip',{
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
        }); 
        const data = await response.json();
        return data.ip; // Return the IP from the response
    } catch (error) {
        console.error('Error fetching IP:', error);
        return null;
    }
}

// back to 8080 web container server
async function back_to_home() {
    const ip = await get_home_IP();
    if (ip) {
        if (pc) {
            pc.close();
            pc = null;
        }
        window.location.href = `http://${ip}:8080`; // Use the fetched IP
    } else {
        console.error('Unable to retrieve IP address');
    }
}

// Remove connection when the client closes the window
window.addEventListener('beforeunload', (event) => {
    setTimeout(() => {
        if (pc) {
            pc.close();
            pc = null;
        }
    }, 500);
});

async function logStats() {
    if (pc) {
        const stats = await pc.getStats();
        stats.forEach(report => {
            console.log(`Report: ${report.type} ${report.id}`);
            for (let [key, value] of Object.entries(report)) {
                if (key !== 'type' && key !== 'id' && key !== 'timestamp' && key !== 'streams') {
                    console.log(`  ${key}: ${value}`);
                }
            }
        });
    }
}

setInterval(logStats, 5000);
