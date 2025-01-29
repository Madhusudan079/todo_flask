document.getElementById('add-task-btn').addEventListener('click', function() {
    const todoInput = document.getElementById('todo-input');
    const taskText = todoInput.value.trim();
    
    if (taskText) {
        // Create a new task element
        const li = document.createElement('li');
        li.innerHTML = `
            <span>${taskText}</span>
            <button class="delete-btn">Delete</button>
        `;
        
        // Append the task to the list
        document.getElementById('todo-list').appendChild(li);
        
        // Clear the input field
        todoInput.value = '';
        
        // Add event listener to the delete button
        li.querySelector('.delete-btn').addEventListener('click', function() {
            li.remove();  // Remove the task from the list
        });
    }
});

// Optional: Allow pressing Enter to add the task
document.getElementById('todo-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        document.getElementById('add-task-btn').click();
    }
});
