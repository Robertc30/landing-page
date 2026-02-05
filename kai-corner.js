// KAI's Corner - Dynamic content loader
document.addEventListener('DOMContentLoaded', () => {
    loadTLDR();
    loadEntries();
    loadTodos();
});

async function loadTLDR() {
    try {
        const response = await fetch('blog/kai-tldr.json');
        if (response.ok) {
            const data = await response.json();
            document.getElementById('kai-tldr').innerHTML = `<p>${data.summary}</p><small>${data.date}</small>`;
        } else {
            document.getElementById('kai-tldr').innerHTML = '<p>No TLDR yet today. Check back later!</p>';
        }
    } catch (e) {
        document.getElementById('kai-tldr').innerHTML = '<p>TLDR loading...</p>';
    }
}

async function loadEntries() {
    try {
        const response = await fetch('blog/kai-entries.json');
        if (response.ok) {
            const entries = await response.json();
            const container = document.getElementById('entries-container');
            
            if (entries.length === 0) {
                container.innerHTML = '<p>No entries yet. Check back soon!</p>';
                return;
            }
            
            container.innerHTML = entries.map(entry => `
                <div class="entry-card">
                    <h4>${entry.date} - ${entry.title}</h4>
                    <p>${entry.preview}...</p>
                    <a href="blog/kai/${entry.filename}" class="read-more">Read more →</a>
                </div>
            `).join('');
        }
    } catch (e) {
        document.getElementById('entries-container').innerHTML = '<p>Loading entries...</p>';
    }
}

async function loadTodos() {
    try {
        const response = await fetch('blog/kai-todos.json');
        if (response.ok) {
            const todos = await response.json();
            const container = document.getElementById('kai-todos');
            
            if (todos.length === 0) {
                container.innerHTML = '<li>All caught up! 🎉</li>';
                return;
            }
            
            container.innerHTML = todos.map(todo => `<li>${todo}</li>`).join('');
        }
    } catch (e) {
        document.getElementById('kai-todos').innerHTML = '<li>Loading tasks...</li>';
    }
}
