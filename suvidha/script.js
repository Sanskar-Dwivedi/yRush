// Simple user database
const users = {
    'student@college.edu': { 
        password: 'pass123', 
        name: 'John Student', 
        type: 'student' 
    },
    'admin@shop.com': { 
        password: 'admin123', 
        name: 'Shop Owner', 
        type: 'admin' 
    }
};

// Handle form submission
document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault(); // Stop form from refreshing page
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorElement = document.getElementById('errorMessage');
    
    // Reset error message
    errorElement.style.display = 'none';
    
    // Check if user exists and password matches
    if (users[email] && users[email].password === password) {
        // Login successful!
        const user = users[email];
        showDashboard(user);
        
    } else {
        // Login failed
        errorElement.textContent = '❌ Invalid email or password';
        errorElement.style.display = 'block';
    }
});

function showDashboard(user) {
    const loginBox = document.querySelector('.login-box');
    
    if (user.type === 'student') {
        loginBox.innerHTML = `
            <h1>🎉 Welcome, ${user.name}!</h1>
            <div style="text-align: center; margin: 30px 0;">
                <h3>Student Dashboard</h3>
                <p>You can now browse and reserve stationery!</p>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h4>Available Products:</h4>
                    <ul style="text-align: left; display: inline-block;">
                        <li>Practical Books - ₹60</li>
                        <li>Project Files - ₹40</li>
                        <li>Pens (Pack of 5) - ₹25</li>
                    </ul>
                </div>
                <button onclick="location.reload()" style="padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    Logout
                </button>
            </div>
        `;
    } else {
        loginBox.innerHTML = `
            <h1>🏪 Welcome, ${user.name}!</h1>
            <div style="text-align: center; margin: 30px 0;">
                <h3>Admin Dashboard</h3>
                <p>Shopkeeper management panel</p>
                <div style="background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h4>Recent Reservations:</h4>
                    <div style="text-align: left;">
                        <p><strong>John Student</strong> - 2 items - ₹110</p>
                        <p><strong>Alice Cooper</strong> - 1 item - ₹40</p>
                    </div>
                </div>
                <button onclick="location.reload()" style="padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    Logout
                </button>
            </div>
        `;
    }
}