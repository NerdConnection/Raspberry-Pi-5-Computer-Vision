async function getCurrentIP(model) {
    try {
        const response = await fetch('/get-ip',{
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ model }),
        }); 
        const data = await response.json();
        return data.ip; // Return the IP from the response
    } catch (error) {
        console.error('Error fetching IP:', error);
        return null;
    }
}


async function move_tflite() {
    const ip = await getCurrentIP("tflite");
    if (ip) {
        window.location.href = `http://${ip}:80`; // Use the fetched IP
    } else {
        console.error('Unable to retrieve IP address');
    }
}




