document.addEventListener('DOMContentLoaded', function() {
    const starContainers = document.querySelectorAll('.star-rating');

    starContainers.forEach(starContainer => {
        const stars = starContainer.querySelectorAll('.star');
        const songId = starContainer.getAttribute('data-song-id');
        const rating = parseInt("{{ user_ratings[songId] }}"); 
        const dic = '{{ user_ratings|tojson }}'
        var user_rating = JSON.parse(dic)
        highlightStars(stars, user_rating[songId]);
        
        stars.forEach((star, index) => {
            star.addEventListener('mouseover', function(event) {
                const rating = parseInt(this.getAttribute('data-value'));
                highlightStars(stars, rating);
            });

            star.addEventListener('mouseout', function(event) {
                const currentRating = parseInt(starContainer.getAttribute('data-rating'));
                highlightStars(stars, user_rating[songId]);
            });

            star.addEventListener('click', function(event) {
                const rating = parseInt(this.getAttribute('data-value'));
                const songId = starContainer.getAttribute('data-song-id');
                updateRating(songId, rating);
            });
        });
    });
});

function highlightStars(stars, rating) {
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
}

function updateRating(songId, userRating) {
    const form = document.querySelector(`#ratingForm${songId}`);
    form.action = `/songs/rate/${songId}/${userRating}`;
    form.submit();
}