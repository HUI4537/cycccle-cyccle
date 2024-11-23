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
                orderedPlaces.push(item.dataset.placeName);
            });

            const urlParams = new URLSearchParams(window.location.search);
            
            fetch('/save_order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    orderedPlaces: orderedPlaces,
                    startDate: urlParams.get('start_date'),
                    endDate: urlParams.get('end_date'),
                    trackType: urlParams.get('track_type')
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('트랙이 성공적으로 저장되었습니다.');
                    window.location.href = '/Journey';
                } else {
                    alert(data.error || '트랙 저장에 실패했습니다.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('트랙 저장 중 오류가 발생했습니다.');
            });
        });

        document.addEventListener('DOMContentLoaded', function() {
            const placeList = document.getElementById('place-list');
            let draggedItem = null;

            // 드래그 시작
            placeList.addEventListener('dragstart', function(e) {
                draggedItem = e.target;
                e.target.style.opacity = '0.5';
            });

            // 드래그 종료
            placeList.addEventListener('dragend', function(e) {
                e.target.style.opacity = '1';
            });

            // 드래그 오버
            placeList.addEventListener('dragover', function(e) {
                e.preventDefault();
                const afterElement = getDragAfterElement(placeList, e.clientY);
                const draggable = document.querySelector('.dragging');
                if (afterElement == null) {
                    placeList.appendChild(draggedItem);
                } else {
                    placeList.insertBefore(draggedItem, afterElement);
                }
            });

            function getDragAfterElement(container, y) {
                const draggableElements = [...container.querySelectorAll('.place-box:not(.dragging)')]
                
                return draggableElements.reduce((closest, child) => {
                    const box = child.getBoundingClientRect();
                    const offset = y - box.top - box.height / 2;
                    if (offset < 0 && offset > closest.offset) {
                        return { offset: offset, element: child };
                    } else {
                        return closest;
                    }
                }, { offset: Number.NEGATIVE_INFINITY }).element;
            }
        });