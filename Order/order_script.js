let draggedItem = null;

        // Drag & Drop Event Listeners
        document.querySelectorAll('.place-box').forEach(box => {
            box.addEventListener('dragstart', function (event) {
                draggedItem = event.target;
                event.dataTransfer.effectAllowed = "move";
            });

            box.addEventListener('dragover', function (event) {
                event.preventDefault();
            });

            box.addEventListener('drop', function (event) {
                event.preventDefault();
                const list = document.getElementById("place-list");
                if (draggedItem !== event.target) {
                    list.insertBefore(draggedItem, event.target.nextSibling);
                }
            });

            // Touch support for drag
            box.addEventListener('touchstart', function (event) {
                draggedItem = event.target;
            });

            box.addEventListener('touchmove', function (event) {
                event.preventDefault();
                const touch = event.touches[0];
                const target = document.elementFromPoint(touch.clientX, touch.clientY);
                if (draggedItem && target && target.classList.contains('place-box') && draggedItem !== target) {
                    const list = document.getElementById("place-list");
                    list.insertBefore(draggedItem, target.nextSibling);
                }
            });

            box.addEventListener('touchend', function () {
                draggedItem = null;
            });
        });

        // Save Order Button
        document.getElementById('save-button').addEventListener('click', function () {
            const orderedPlaces = [];
            document.querySelectorAll('.place-box').forEach(item => {
                orderedPlaces.push(item.dataset.placeName); // 순서를 배열로 저장
            });

            // 페이지 이동을 통해 순서 전달
            fetch('/save_order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ orderedPlaces: orderedPlaces }),
            })
            .then(response => response.text())
            .then(html => {
                document.open();
                document.write(html);
                document.close();
            })
            .catch(error => console.error('Error saving order:', error));
        });