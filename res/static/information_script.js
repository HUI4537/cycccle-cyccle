function showPopup() {
    fetch('data.json') // JSON 파일 경로
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const popupData = document.getElementById('popup-data');
            popupData.innerHTML = ""; // 기존 내용 초기화

            // JSON 데이터를 HTML로 변환
            for (const section in data) {
                const sectionTitle = document.createElement('h2');
                sectionTitle.textContent = section;
                sectionTitle.style.fontWeight = 'bold';
                popupData.appendChild(sectionTitle);

                data[section].forEach(item => {
                    const itemTitle = document.createElement('h3');
                    itemTitle.textContent = item.title;
                    itemTitle.style.fontWeight = 'bold';
                    popupData.appendChild(itemTitle);

                    // 객체 데이터를 처리하여 보기 좋게 표시
                    const itemContent = document.createElement('p');
                    if (typeof item.content === 'string') {
                        itemContent.textContent = item.content;
                    } else if (typeof item.content === 'object') {
                        // 객체인 경우 리스트로 변환
                        const list = document.createElement('ul');
                        for (const key in item.content) {
                            const listItem = document.createElement('li');
                            listItem.innerHTML = `<b>${key}:</b> ${item.content[key]}`;
                            list.appendChild(listItem);
                        }
                        itemContent.appendChild(list);
                    }
                    popupData.appendChild(itemContent);
                });
            }

            document.getElementById('popup').style.display = 'flex';
        })
        .catch(error => alert("Failed to load data: " + error));
}
function closePopup() {
    const popup = document.getElementById('popup');
    if (popup) {
        popup.style.display = 'none';
    }
}