navigator.geolocation.watchPosition(
    (position) => {
        const userCoords = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
        };

        console.log("사용자 위치:", userCoords);

        // OpenStreetMap 타일 추가
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap'
        }).addTo(map);

        // 사용자 위치를 마커로 지도에 추가
        L.marker([userCoords.latitude, userCoords.longitude], { title: '현재 위치' }).addTo(map);

        // 장소 데이터 가져오기
        fetch('/get-places')
            .then(response => response.json())
            .then(places => {

                // 반경 확인
                fetch('/check-location', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(userCoords)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.in_radius) {
                        if (data.audio_url) {
                            const audio = new Audio(data.audio_url);
                            audio.play(); // TTS 오디오 재생
                        }
                    } else {
                        console.log(data.message); // 반경 외 메시지
                    }
                });
            });
    },
    { enableHighAccuracy: true }
);
