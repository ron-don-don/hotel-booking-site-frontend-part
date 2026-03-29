document.addEventListener("DOMContentLoaded", () => {
    // 1. Handle notifications (flash messages)
    const urlParams = new URLSearchParams(window.location.search);
    const message = urlParams.get('message');
    if (message) {
        const flashDiv = document.getElementById('flash-message');
        if (flashDiv) {
            flashDiv.textContent = message;
            flashDiv.style.display = 'block';
        }
        const cleanUrl = window.location.origin + window.location.pathname;
        window.history.replaceState({}, '', cleanUrl);
    }

    // 2. Universal JSON form handler
    const jsonForms = document.querySelectorAll('.js-json-form');
    jsonForms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const url = form.getAttribute('action');
            const method = (form.getAttribute('data-method') || form.getAttribute('method') || 'POST').toUpperCase();

            const formData = new FormData(form);
            const data = {};
            formData.forEach((value, key) => {
                const input = form.elements[key];
                if (input && input.type === 'number') data[key] = value ? Number(value) : null;
                else if (input && input.type === 'checkbox') data[key] = input.checked;
                else data[key] = value;
            });

            try {
                const response = await fetch(url, {
                    method: method,
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                handleResponse(response);
            } catch (error) {
                console.error('Fetch error:', error);
                alert("Connection error occurred.");
            }
        });
    });

    // 3. Hotel accordions (load rooms)
    document.querySelectorAll('.hotel-expandable').forEach(details => {
        details.addEventListener('toggle', async () => {
            if (details.open && !details.dataset.loaded) {
                const hotelId = details.dataset.hotelId;
                const container = details.querySelector('.rooms-container');
                try {
                    const response = await fetch(`/rooms/${hotelId}/rooms`);
                    const rooms = await response.json();
                    container.innerHTML = rooms.length ? renderRoomsTable(rooms) : '<p style="color: #94a3b8;">No rooms found.</p>';
                    details.dataset.loaded = "true";
                } catch (error) {
                    container.innerHTML = '<p style="color: red;">Error loading rooms.</p>';
                }
            }
        });
    });
});

// --- Global functions (extracted from DOMContentLoaded for onclick access) ---

async function handleResponse(response) {
    if (response.redirected) {
        window.location.href = response.url;
    } else {
        let result = {};
        try {
            // Safe parsing in case the server returns a 200 OK with no body after image upload
            result = await response.json();
        } catch (e) {
            console.warn("Could not parse JSON response");
        }

        alert(result.detail || result.message || (response.ok ? "Operation completed successfully" : "An error occurred"));
        if (response.ok) window.location.reload();
    }
}

window.deleteItem = async function(url) {
    if (!confirm('Are you sure you want to delete this?')) return;
    try {
        const response = await fetch(url, { method: 'DELETE' });
        handleResponse(response);
    } catch (e) { console.error(e); }
}

window.handleImageUpload = async function() {
    const hotelId = document.getElementById('upload_hotel_uuid').value;
    const form = document.getElementById('uploadPhotoForm');
    const fileInput = form.querySelector('input[type="file"]');

    if (!hotelId || !fileInput.files[0]) {
        alert("Please fill Hotel UUID and select an image");
        return;
    }

    const formData = new FormData();
    formData.append('image', fileInput.files[0]);

    try {
        const response = await fetch(`/hotels/image/${hotelId}`, {
            method: 'POST',
            body: formData // The browser will set the Content-Type automatically for FormData
        });
        handleResponse(response);
    } catch (e) {
        console.error("Upload error:", e);
        alert("Error during upload");
    }
}

window.handleImageDelete = async function() {
    const hotelId = document.getElementById('delete_hotel_uuid').value;
    if (!hotelId) {
        alert("Please fill Hotel UUID!");
        return;
    }
    if (!confirm('Delete hotel image?')) return;

    try {
        const response = await fetch(`/hotels/image/${hotelId}`, { method: 'DELETE' });
        handleResponse(response);
    } catch (e) { console.error(e); }
}

function renderRoomsTable(rooms) {
    let rows = rooms.map(room => `
        <tr>
            <td><span class="id-badge">${room.id}</span></td>
            <td><strong>${room.number}</strong></td>
            <td>${room.prestige}</td>
            <td>$${room.fine}</td>
            <td>
                <span class="status-badge" style="background: ${room.is_available ? '#dcfce7' : '#fee2e2'}; color: ${room.is_available ? '#166534' : '#991b1b'};">
                    ${room.is_available ? 'Available' : 'Occupied'}
                </span>
            </td>
            <td>
                <button class="btn-danger" style="width: auto; padding: 4px 10px; font-size: 0.75rem;" 
                        onclick="deleteItem('/rooms/delete/${room.id}')">Delete</button>
            </td>
        </tr>
    `).join('');
    return `<table class="rooms-table"><thead><tr><th>ID</th><th>No.</th><th>Type</th><th>Price</th><th>Status</th><th>Action</th></tr></thead><tbody>${rows}</tbody></table>`;
}