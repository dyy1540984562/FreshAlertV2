document.addEventListener('DOMContentLoaded', function() {
    // Example of adding an event listener to the search form
    var searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(event) {
            event.preventDefault();
            var searchTerm = document.getElementById('search-term').value;
            // Perform the search here, possibly making an AJAX request
            // For now, we'll just log the term to the console
            console.log('Search term:', searchTerm);
        });
    }
});