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
const video = document.getElementById('video');
const fpsDisplay = document.getElementById('fpsDisplay');
let frameCount = 0;
let lastTime = performance.now();
        // FPS 계산 함수
function calculateFPS() {
    const currentTime = performance.now();
    frameCount++;

    // 매초 FPS 업데이트
    if (currentTime - lastTime >= 1000) {
        fpsDisplay.textContent = frameCount;
        frameCount = 0;
        lastTime = currentTime;
    }   

    requestAnimationFrame(calculateFPS);
    }

    // 비디오가 재생될 때 FPS 계산 시작
    video.addEventListener('playing', () => {
    frameCount = 0;
    lastTime = performance.now();
    calculateFPS();
});

        // 시스템 리소스 정보를 주기적으로 업데이트
async function updateSystemResources() {
    try {
        const response = await fetch('/system_resources');
        const data = await response.json();
        document.getElementById('cpu-temp').innerText = `CPU Temperature: ${data.cpu_temp.toFixed(1)} °C`;
        document.getElementById('memory-info').innerText = `Memory Usage: ${((data.memory_used / data.memory_total) * 100).toFixed(2)}% (${(data.memory_used / (1024**2)).toFixed(1)} MB / ${(data.memory_total / (1024**2)).toFixed(1)} MB)`;
        } 
        catch (error) {
            console.error("Failed to fetch system resources:", error);
        }
    }

        // 5초마다 시스템 리소스 업데이트
setInterval(updateSystemResources, 5000);

// Remove connection when the client closes the window
window.addEventListener('beforeunload', (event) => {
    setTimeout(() => {
        if (pc) {
            pc.close();
            pc = null;
        }
    }, 500);
});
