// JSON 데이터 로드
fetch("data.json")
  .then(response => {
    if (!response.ok) throw new Error("Network response was not ok");
    return response.json();
  })
  .then(jsondata => {
    data = jsondata;
    display_random_results();
  })
  .catch(error => {
    console.error("Error loading JSON data:", error);
  });

// 검색 버튼 클릭 시 카테고리 필터링
document.querySelector(".search_btn").onclick = () => {
    const query = document.querySelector(".search_input").value.toLowerCase();

    if (query.trim() === "") {
        display_random_results();
    } else {
        // 검색어를 공백을 기준으로 단어로 분할
        const query_keywords = query.split(" ");

        // 검색어 필터링
        const filtered_results = data.flatMap(item =>
            item.links.filter(link => {
                const category_match = query_keywords.some(keyword => item.category.toLowerCase().includes(keyword));
                const link_match = query_keywords.some(keyword => link.url.toLowerCase().includes(keyword));
                return category_match || link_match;
            }).map(link => ({
                category: item.category,
                url: link.url,
                image: link.image
            }))
        );

        update_card_links(filtered_results.slice(0, 6)); 
    }
};

// 검색어가 없을 때 랜덤으로 6개의 링크 표시
function display_random_results() {
    const all_links = data.flatMap(item => item.links.map(link => ({
        category: item.category,
        url: link.url,
        image: link.image
    })));

    const random_links = all_links.sort(() => Math.random() - 0.5).slice(0, 6);
    update_card_links(random_links);
}

// 카드의 링크, 카테고리 텍스트, 이미지 
function update_card_links(results) {
    const cards = document.querySelectorAll(".card");

    results.forEach((result, index) => {
        if (cards[index]) {
            const card = cards[index];
            const card_content = card.querySelector(".card_content");
            card_content.querySelector("h3").textContent = result.category;
            card_content.querySelector("a").textContent = result.url;
            card_content.querySelector("a").href = result.url;

            // 이미지
            const placeholder_image = card.querySelector(".placeholder_image");
            placeholder_image.style.backgroundImage = `url(${result.image})`;

            // 카드 클릭 이동
            card.onclick = () => {
                window.open(result.url, "_blank");
            };
        }
    });

    
    for (let i = results.length; i < cards.length; i++) {
        const card = cards[i];
        const card_content = card.querySelector(".card_content");
        card_content.querySelector("h3").textContent = "카테고리 없음";
        card_content.querySelector("a").textContent = "링크 없음";
        card_content.querySelector("a").href = "#";

        // 빈 카드의 이미지 초기화
        const placeholder_image = card.querySelector(".placeholder_image");
        placeholder_image.style.backgroundImage = "none";

        
        card.onclick = null;
    }
}
