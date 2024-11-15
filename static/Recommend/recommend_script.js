let selectedPlaces = [];

function toggleSelection(placeId) {
    const placeElement = document.getElementById(`place-${placeId}`);
    if (selectedPlaces.includes(placeId)) {
        selectedPlaces = selectedPlaces.filter(id => id !== placeId);
        placeElement.classList.remove('selected');
    } else {
        selectedPlaces.push(placeId);
        placeElement.classList.add('selected');
    }
}

function submitSelection() {
    const query = selectedPlaces.map(id => `places=${id}`).join('&');
    window.location.href = `/next_page?${query}`;
}