const currentCameraId = window.currentCameraId;
const cameraIds = window.cameraIds || [];
let currentIndex = cameraIds.indexOf(currentCameraId);

function openAddCamera() {
    document.getElementById('addCameraModal').classList.add('active');
}

function closeAddCamera() {
    document.getElementById('addCameraModal').classList.remove('active');
}

function openSettings() {
    document.getElementById('settingsModal').classList.add('active');
}

function closeSettings() {
    document.getElementById('settingsModal').classList.remove('active');
}

function previousCamera() {
    if (cameraIds.length <= 1) return;
    currentIndex = (currentIndex - 1 + cameraIds.length) % cameraIds.length;
    window.location.href = '?camera=' + cameraIds[currentIndex];
}

function nextCamera() {
    if (cameraIds.length <= 1) return;
    currentIndex = (currentIndex + 1) % cameraIds.length;
    window.location.href = '?camera=' + cameraIds[currentIndex];
}

function logout() {
    window.location.href = '/logout/';
}

function deleteCamera(id) {
    window.location.href = '/camera/' + id + '/delete/';
}

function startCalibration() {
    const name = document.getElementById('camera-name').value;
    const typeRadio = document.querySelector('input[name="type"]:checked');
    const type = typeRadio ? typeRadio.value : 'video';
    const url = type === 'ip' ? document.getElementById('camera-url').value : '';
    
    if (type === 'ip' && !url) return;
    
    const formData = new FormData();
    formData.append('name', name);
    formData.append('type', type);
    formData.append('url', url);
    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
    
    fetch('/camera/create/', {
        method: 'POST',
        body: formData
    })
    .then(r => r.json())
    .then(data => {
        if (data.camera_id) window.location.href = '/camera/' + data.camera_id + '/calibrate/';
    });
}

function acceptCamera() {
    closeAddCamera();
    window.location.reload();
}

document.querySelectorAll('input[name="type"]').forEach(radio => {
    radio.addEventListener('change', function() {
        document.getElementById('url-group').style.display = this.value === 'ip' ? 'block' : 'none';
    });
});

if (currentCameraId) {
    function updateSpaceStatus() {
        fetch('/detection/spaces-status/' + currentCameraId + '/')
            .then(r => r.json())
            .then(data => {
                data.spaces.forEach(space => {
                    const card = document.querySelector(`[data-slot="${space.number}"]`);
                    if (card) {
                        card.classList.remove('occupied', 'available');
                        card.classList.add(space.occupied ? 'occupied' : 'available');
                    }
                });
            });
    }
    
    setInterval(updateSpaceStatus, 1000);
}
