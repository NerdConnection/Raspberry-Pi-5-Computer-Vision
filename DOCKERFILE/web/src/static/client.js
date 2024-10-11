async function getCurrentIP(model) {
    // get wlan0 ip and start container named model
    try {
        const response = await fetch('/get-ip',{
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ model }),
        }); 
        const data = await response.json();
        console.log(data.ip)
        return data.ip; // Return the IP from the response
    } catch (error) {
        console.error('Error fetching IP:', error);
        return null;
    }
}


async function move(container_name) {
    console.log(container_name);
    const ip = await getCurrentIP(container_name);
    if (container_name === "tflite") {
        window.location.href = `http://${ip}:80`;
    } 
    else if(container_name === "onnx"){
        window.location.href = `http://${ip}:81`;
    }
    else {
        console.error('Unable to retrieve IP address');
    }
}


async function checkContainers() {
    try {
        const response = await fetch('/get-containers',{
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
        }); 
            
            const containers = await response.json();
            console.log(containers)                
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            displayContainers(containers);
        } catch (error) {
            console.error('Error fetching container states:', error);}
}


async function stopContainer(containerName) {
    try {
        const response = await fetch('/stop-container', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: containerName }), // Send container name to server
        });

        const data = await response.json();
        if (data.status !== 'success') {
            console.error('Error stopping container:', data.message);
        } else {
            console.log(`Container ${containerName} stopped successfully`);
        }
    } catch (error) {
        console.error('Error stopping container:', error);
    }
}


function displayContainers(containers) {
    const containerList = document.getElementById('containerList');
    containerList.innerHTML = ''; // Clear previous list

    let runningContainer = null;
    // Check if any container is running
    containers.forEach(container => {
    if (container.status === 'running') {
        runningContainer = container;
        }
    });

    if (runningContainer) {
        containers.forEach(container => {
            const containerDiv = document.createElement('div');
            containerDiv.classList.add('container');
    
            const stateText = document.createElement('span');
            stateText.textContent = `${container.name} - ${container.status}`;
            containerDiv.appendChild(stateText);
    
            if (container.status === 'running') {
                // "Move" button to navigate to the container's web page
                const moveButton = document.createElement('button');
                moveButton.textContent = 'Move to ' + container.name;
                moveButton.onclick = () => {
                    move(container.name)
                };
    
                // "Stop" button to stop the running container
                const stopButton = document.createElement('button');
                stopButton.textContent = 'Stop ' + container.name;
                stopButton.onclick = async () => {
                    await stopContainer(container.name); // Call stopContainer to stop the container
                    checkContainers(); // Refresh the container list after stopping
                };
    
                containerDiv.appendChild(stopButton);
                containerDiv.appendChild(moveButton);
            }
            containerList.appendChild(containerDiv);
        });
    }
    else {
        containers.forEach(container => {
            const containerDiv = document.createElement('div');
            containerDiv.classList.add('container');

            const stateText = document.createElement('span');
            stateText.textContent = `${container.name} - ${container.status}`;
            containerDiv.appendChild(stateText);
        
            const button = document.createElement('button');
            button.textContent = 'Move to ' + container.name;
            button.onclick = () => {
                move(container.name)
            };
            containerDiv.appendChild(button);
            containerList.appendChild(containerDiv);
        });
    }
}
