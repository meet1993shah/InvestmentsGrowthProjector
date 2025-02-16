document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById('investmentForm');

    if (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault(); // Prevent default page reload

            const formData = new FormData(this);
            const data = new URLSearchParams(formData);

            fetch('/investment_details', {
                method: 'POST',
                body: data
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url; // Redirect to /chart_display
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }
});
