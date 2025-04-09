// API base URL
const API_BASE_URL = 'http://127.0.0.1:8000/api';

// Store user data and token
let currentUser = null;
let accessToken = localStorage.getItem('access_token');
let refreshToken = localStorage.getItem('refresh_token');

// DOM Elements
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application when DOM is fully loaded
    init();
});

// Initialize application
function init() {
    setupAuthenticationListeners();
    setupNavigationListeners();
    checkAuthentication();
    setupFormListeners();
}

// Check if user is authenticated
function checkAuthentication() {
    if (accessToken) {
        fetchUserProfile()
            .then(() => {
                showAuthenticatedUI();
                loadDashboard();
            })
            .catch(error => {
                console.error('Error fetching user profile:', error);
                if (error.status === 401) {
                    refreshAuthentication();
                } else {
                    showUnauthenticatedUI();
                }
            });
    } else {
        showUnauthenticatedUI();
    }
}

// Refresh authentication token
async function refreshAuthentication() {
    if (!refreshToken) {
        showUnauthenticatedUI();
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: refreshToken }),
        });

        if (!response.ok) throw new Error('Token refresh failed');

        const data = await response.json();
        accessToken = data.access;
        localStorage.setItem('access_token', accessToken);
        
        fetchUserProfile()
            .then(() => {
                showAuthenticatedUI();
                loadDashboard();
            })
            .catch(error => {
                console.error('Error after token refresh:', error);
                showUnauthenticatedUI();
            });
    } catch (error) {
        console.error('Error refreshing token:', error);
        showUnauthenticatedUI();
    }
}

// Setup authentication event listeners
function setupAuthenticationListeners() {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const logoutBtn = document.getElementById('logout-btn');

    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    if (registerForm) {
        registerForm.addEventListener('submit', handleRegistration);
    }

    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
}

// Setup navigation event listeners
function setupNavigationListeners() {
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.getAttribute('data-page');
            navigateTo(page);
        });
    });
}

// Setup form event listeners
function setupFormListeners() {
    const mealForm = document.getElementById('meal-form');
    const healthLogForm = document.getElementById('health-log-form');
    const sleepForm = document.getElementById('sleep-form');
    
    if (mealForm) {
        mealForm.addEventListener('submit', handleMealSubmit);
    }
    
    if (healthLogForm) {
        healthLogForm.addEventListener('submit', handleHealthLogSubmit);
    }
    
    if (sleepForm) {
        sleepForm.addEventListener('submit', handleSleepSubmit);
    }
}

// Handle user login
async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Login failed');
        }
        
        const data = await response.json();
        accessToken = data.access;
        refreshToken = data.refresh;
        
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
        
        await fetchUserProfile();
        showAuthenticatedUI();
        loadDashboard();
        
        showAlert('התחברת בהצלחה!', 'success');
    } catch (error) {
        console.error('Login error:', error);
        showAlert(error.message || 'שגיאה בהתחברות, נסה שוב', 'error');
    }
}

// Handle user registration
async function handleRegistration(e) {
    e.preventDefault();
    
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const password2 = document.getElementById('register-password2').value;
    
    if (password !== password2) {
        showAlert('הסיסמאות אינן תואמות', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password, password2 }),
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            const errorMessage = Object.values(errorData).flat().join(' ');
            throw new Error(errorMessage || 'Registration failed');
        }
        
        const data = await response.json();
        showAlert('נרשמת בהצלחה! כעת באפשרותך להתחבר', 'success');
        
        // Switch to login form
        document.getElementById('register-container').classList.add('hidden');
        document.getElementById('login-container').classList.remove('hidden');
    } catch (error) {
        console.error('Registration error:', error);
        showAlert(error.message || 'שגיאה בהרשמה, נסה שוב', 'error');
    }
}

// Handle user logout
function handleLogout(e) {
    e.preventDefault();
    
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    accessToken = null;
    refreshToken = null;
    currentUser = null;
    
    showUnauthenticatedUI();
    showAlert('התנתקת בהצלחה', 'success');
}

// Fetch user profile
async function fetchUserProfile() {
    try {
        const response = await fetch(`${API_BASE_URL}/user/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw { status: response.status, message: 'Failed to fetch user profile' };
        }
        
        currentUser = await response.json();
        
        // Update UI with user info
        const userNameElement = document.getElementById('user-name');
        if (userNameElement) {
            userNameElement.textContent = currentUser.username;
        }
        
        return currentUser;
    } catch (error) {
        console.error('Error fetching user profile:', error);
        throw error;
    }
}

// Show authenticated UI
function showAuthenticatedUI() {
    document.querySelectorAll('.auth-required').forEach(el => {
        el.classList.remove('hidden');
    });
    
    document.querySelectorAll('.auth-not-required').forEach(el => {
        el.classList.add('hidden');
    });
    
    navigateTo('dashboard');
}

// Show unauthenticated UI
function showUnauthenticatedUI() {
    document.querySelectorAll('.auth-required').forEach(el => {
        el.classList.add('hidden');
    });
    
    document.querySelectorAll('.auth-not-required').forEach(el => {
        el.classList.remove('hidden');
    });
    
    navigateTo('login');
}

// Navigation handler
function navigateTo(page) {
    document.querySelectorAll('.page').forEach(p => {
        p.classList.add('hidden');
    });
    
    document.getElementById(`${page}-page`).classList.remove('hidden');
    
    // Additional actions based on page
    if (page === 'dashboard' && accessToken) {
        loadDashboard();
    } else if (page === 'meal-form') {
        initializeMealForm();
    } else if (page === 'health-log-form') {
        initializeHealthLogForm();
    } else if (page === 'sleep-form') {
        initializeSleepForm();
    }
}

// Load dashboard data
async function loadDashboard() {
    const dashboardPage = document.getElementById('dashboard-page');
    if (!dashboardPage) return;
    
    const loadingElement = document.createElement('div');
    loadingElement.className = 'loading';
    dashboardPage.appendChild(loadingElement);
    
    try {
        await Promise.all([
            loadRecentMeals(),
            loadHealthTrends(),
            loadHealthAnalytics()
        ]);
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showAlert('שגיאה בטעינת הדאשבורד', 'error');
    } finally {
        dashboardPage.removeChild(loadingElement);
    }
}

// Load recent meals
async function loadRecentMeals() {
    try {
        const today = new Date();
        const formattedDate = today.toISOString().split('T')[0];
        
        const response = await fetch(`${API_BASE_URL}/meals/daily/${formattedDate}/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) throw new Error('Failed to fetch meals');
        
        const meals = await response.json();
        
        const recentMealsContainer = document.getElementById('recent-meals');
        if (!recentMealsContainer) return;
        
        if (meals.length === 0) {
            recentMealsContainer.innerHTML = '<p>אין ארוחות להיום. <a href="#" data-page="meal-form" class="add-data-link">הוסף ארוחה</a></p>';
            return;
        }
        
        let mealsHTML = '<h3>ארוחות להיום</h3><div class="meals-list">';
        
        meals.forEach(meal => {
            const mealTime = new Date(meal.date_time).toLocaleTimeString('he-IL', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
            
            mealsHTML += `
                <div class="meal-item card">
                    <div class="card-header">
                        <h4>${meal.meal_type} - ${mealTime}</h4>
                    </div>
                    <div class="card-body">
                        <p><strong>פירוט:</strong> ${meal.notes || 'אין הערות'}</p>
                        <div class="meal-foods">
                            <h5>מזונות:</h5>
                            <ul>
                                ${meal.meal_foods.map(mealFood => `
                                    <li>
                                        <strong>${mealFood.food.name}</strong> - 
                                        ${mealFood.amount}g
                                        ${mealFood.notes ? `<br><em>${mealFood.notes}</em>` : ''}
                                    </li>
                                `).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            `;
        });
        
        mealsHTML += '</div>';
        recentMealsContainer.innerHTML = mealsHTML;
        
        // Setup event listeners for add data links
        recentMealsContainer.querySelectorAll('.add-data-link').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const page = this.getAttribute('data-page');
                navigateTo(page);
            });
        });
    } catch (error) {
        console.error('Error loading recent meals:', error);
        document.getElementById('recent-meals').innerHTML = 
            '<p>שגיאה בטעינת ארוחות. <a href="#" data-page="meal-form" class="add-data-link">הוסף ארוחה</a></p>';
    }
}

// Load health trends
async function loadHealthTrends() {
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/health-trends/?days=7`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) throw new Error('Failed to fetch health trends');
        
        const trends = await response.json();
        
        const healthTrendsContainer = document.getElementById('health-trends');
        if (!healthTrendsContainer) return;
        
        // Simple visualization of health trends
        let trendsHTML = '<h3>מגמות בריאות</h3>';
        
        if (!trends.physical_feeling || trends.physical_feeling.length === 0) {
            trendsHTML += '<p>אין נתוני בריאות זמינים. <a href="#" data-page="health-log-form" class="add-data-link">הוסף רשומת בריאות</a></p>';
        } else {
            trendsHTML += `
                <div class="trend-summary">
                    <div class="stats-card card">
                        <div class="stats-label">הרגשה פיזית ממוצעת</div>
                        <div class="stats-value">${calculateAverage(trends.physical_feeling, 'value').toFixed(1)}/5</div>
                    </div>
                    <div class="stats-card card">
                        <div class="stats-label">הרגשה נפשית ממוצעת</div>
                        <div class="stats-value">${calculateAverage(trends.mental_feeling, 'value').toFixed(1)}/5</div>
                    </div>
                </div>
                <div class="trends-visualization">
                    <h4>מגמות לאורך 7 ימים אחרונים</h4>
                    <div class="chart-container">
                        <canvas id="healthTrendsChart"></canvas>
                    </div>
                </div>
            `;
        }
        
        healthTrendsContainer.innerHTML = trendsHTML;
        
        // Setup health trends chart if data exists
        if (trends.physical_feeling && trends.physical_feeling.length > 0) {
            const ctx = document.getElementById('healthTrendsChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: trends.physical_feeling.map(item => formatDate(item.date)),
                    datasets: [
                        {
                            label: 'הרגשה פיזית',
                            data: trends.physical_feeling.map(item => item.value),
                            borderColor: '#34a9a1',
                            backgroundColor: 'rgba(52, 169, 161, 0.1)',
                            tension: 0.3
                        },
                        {
                            label: 'הרגשה נפשית',
                            data: trends.mental_feeling.map(item => item.value),
                            borderColor: '#6ac0b9',
                            backgroundColor: 'rgba(106, 192, 185, 0.1)',
                            tension: 0.3
                        }
                    ]
                },
                options: {
                    scales: {
                        y: {
                            min: 1,
                            max: 5,
                            ticks: { stepSize: 1 }
                        }
                    },
                    plugins: {
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    }
                }
            });
        }
        
        // Setup event listeners for add data links
        healthTrendsContainer.querySelectorAll('.add-data-link').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const page = this.getAttribute('data-page');
                navigateTo(page);
            });
        });
    } catch (error) {
        console.error('Error loading health trends:', error);
        document.getElementById('health-trends').innerHTML = 
            '<p>שגיאה בטעינת מגמות בריאות. <a href="#" data-page="health-log-form" class="add-data-link">הוסף רשומת בריאות</a></p>';
    }
}

// Load health analytics
async function loadHealthAnalytics() {
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/food-correlations/?days=30`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) throw new Error('Failed to fetch food correlations');
        
        const correlations = await response.json();
        
        const analyticsContainer = document.getElementById('health-analytics');
        if (!analyticsContainer) return;
        
        if (correlations.length === 0) {
            analyticsContainer.innerHTML = '<h3>תובנות בריאות</h3><p>אין מספיק נתונים לתובנות. הוסף נתוני בריאות וארוחות כדי לקבל תובנות.</p>';
            return;
        }
        
        let insightsHTML = '<h3>תובנות בריאות</h3>';
        
        // Simple correlation display
        insightsHTML += `
            <div class="card">
                <div class="card-header">
                    <h4>הקשרים בין מזון והרגשה</h4>
                </div>
                <div class="card-body">
                    <p>ניתוח של ${correlations.length} ימים אחרונים:</p>
                    <div class="correlations-table">
                        <table>
                            <thead>
                                <tr>
                                    <th>תאריך</th>
                                    <th>הרגשה פיזית</th>
                                    <th>מזונות מהיום הקודם</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${correlations.slice(0, 5).map(day => `
                                    <tr>
                                        <td>${formatDate(day.date)}</td>
                                        <td>
                                            ${getRatingStars(day.physical_feeling)}
                                        </td>
                                        <td>
                                            ${day.foods_eaten_previous_day.length > 0 ? 
                                                day.foods_eaten_previous_day.map(food => 
                                                    `${food.name} (${food.amount})`
                                                ).join(', ') : 
                                                'לא נמצאו ארוחות'
                                            }
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                    <p class="insight-note">* מוצגים 5 הימים האחרונים בלבד. לניתוח מלא ותובנות נוספות, בקר ב<a href="#" data-page="analytics">דף האנליטיקות</a>.</p>
                </div>
            </div>
        `;
        
        analyticsContainer.innerHTML = insightsHTML;
        
        // Setup event listeners for page links
        analyticsContainer.querySelectorAll('a[data-page]').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const page = this.getAttribute('data-page');
                navigateTo(page);
            });
        });
    } catch (error) {
        console.error('Error loading health analytics:', error);
        document.getElementById('health-analytics').innerHTML = 
            '<h3>תובנות בריאות</h3><p>שגיאה בטעינת תובנות. נסה שוב מאוחר יותר.</p>';
    }
}

// Initialize meal form
function initializeMealForm() {
    const mealForm = document.getElementById('meal-form');
    if (!mealForm) return;
    
    // Reset form
    mealForm.reset();
    
    // Set current date and time as default
    const now = new Date();
    const dateInput = document.getElementById('meal-date');
    const timeInput = document.getElementById('meal-time');
    
    if (dateInput) {
        dateInput.value = now.toISOString().split('T')[0];
    }
    
    if (timeInput) {
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        timeInput.value = `${hours}:${minutes}`;
    }
    
    // Load available foods for selection
    loadFoods();
}

// Load foods for meal form
async function loadFoods() {
    const foodSelect = document.getElementById('meal-food');
    if (!foodSelect) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/foods/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) throw new Error('Failed to fetch foods');
        
        const foods = await response.json();
        
        // Clear existing options
        foodSelect.innerHTML = '<option value="">בחר מזון</option>';
        
        // Add foods to select
        foods.forEach(food => {
            const option = document.createElement('option');
            option.value = food.id;
            option.textContent = `${food.name} (${food.calories} קלוריות)`;
            foodSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading foods:', error);
        foodSelect.innerHTML = '<option value="">שגיאה בטעינת מזונות</option>';
    }
}

// Handle meal form submission
async function handleMealSubmit(e) {
    e.preventDefault();
    
    const mealDate = document.getElementById('meal-date').value;
    const mealTime = document.getElementById('meal-time').value;
    const mealType = document.getElementById('meal-type').value;
    const mealNotes = document.getElementById('meal-notes').value;
    const foodId = document.getElementById('meal-food').value;
    const foodAmount = document.getElementById('meal-food-amount').value;
    const foodNotes = document.getElementById('meal-food-notes').value;
    
    if (!mealDate || !mealTime || !mealType || !foodId || !foodAmount) {
        showAlert('נא למלא את כל השדות הנדרשים', 'error');
        return;
    }
    
    const dateTime = `${mealDate}T${mealTime}:00Z`;
    
    try {
        // Create meal
        const mealResponse = await fetch(`${API_BASE_URL}/meals/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                date_time: dateTime,
                meal_type: mealType,
                notes: mealNotes
            })
        });
        
        if (!mealResponse.ok) {
            const errorData = await mealResponse.json();
            throw new Error(JSON.stringify(errorData));
        }
        
        const mealData = await mealResponse.json();
        
        // Add food to meal
        const mealFoodResponse = await fetch(`${API_BASE_URL}/meals/${mealData.id}/add-food/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                food_id: parseInt(foodId),
                amount: parseInt(foodAmount),
                notes: foodNotes
            })
        });
        
        if (!mealFoodResponse.ok) {
            const errorData = await mealFoodResponse.json();
            throw new Error(JSON.stringify(errorData));
        }
        
        showAlert('הארוחה נוספה בהצלחה', 'success');
        navigateTo('dashboard');
    } catch (error) {
        console.error('Error submitting meal:', error);
        showAlert('שגיאה בהוספת ארוחה. נסה שוב.', 'error');
    }
}

// Initialize health log form
function initializeHealthLogForm() {
    const healthForm = document.getElementById('health-log-form');
    if (!healthForm) return;
    
    // Reset form
    healthForm.reset();
    
    // Set current date as default
    const now = new Date();
    const dateInput = document.getElementById('health-date');
    
    if (dateInput) {
        dateInput.value = now.toISOString().split('T')[0];
    }
}

// Handle health log form submission
async function handleHealthLogSubmit(e) {
    e.preventDefault();
    
    const healthDate = document.getElementById('health-date').value;
    const physicalFeeling = document.getElementById('physical-feeling').value;
    const mentalFeeling = document.getElementById('mental-feeling').value;
    const stoolQuality = document.getElementById('stool-quality').value;
    const stoolCount = document.getElementById('stool-count').value;
    const symptoms = document.getElementById('symptoms').value;
    const weight = document.getElementById('weight').value;
    const notes = document.getElementById('health-notes').value;
    
    if (!healthDate || !physicalFeeling || !mentalFeeling) {
        showAlert('נא למלא את כל השדות הנדרשים', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/health-logs/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                date: healthDate,
                physical_feeling: parseInt(physicalFeeling),
                mental_feeling: parseInt(mentalFeeling),
                stool_quality: stoolQuality,
                stool_count: stoolCount ? parseInt(stoolCount) : null,
                symptoms: symptoms,
                weight: weight || null,
                notes: notes
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(JSON.stringify(errorData));
        }
        
        showAlert('רשומת הבריאות נוספה בהצלחה', 'success');
        navigateTo('dashboard');
    } catch (error) {
        console.error('Error submitting health log:', error);
        showAlert('שגיאה בהוספת רשומת בריאות. נסה שוב.', 'error');
    }
}

// Initialize sleep form
function initializeSleepForm() {
    const sleepForm = document.getElementById('sleep-form');
    if (!sleepForm) return;
    
    // Reset form
    sleepForm.reset();
    
    // Set current date as default
    const now = new Date();
    const dateInput = document.getElementById('sleep-date');
    
    if (dateInput) {
        dateInput.value = now.toISOString().split('T')[0];
    }
}

// Handle sleep form submission
async function handleSleepSubmit(e) {
    e.preventDefault();
    
    const sleepDate = document.getElementById('sleep-date').value;
    const duration = document.getElementById('sleep-duration').value;
    const quality = document.getElementById('sleep-quality').value;
    const wakeUpEase = document.getElementById('wake-up-ease').value;
    const energyLevel = document.getElementById('energy-level').value;
    const notes = document.getElementById('sleep-notes').value;
    
    if (!sleepDate || !duration || !quality || !wakeUpEase || !energyLevel) {
        showAlert('נא למלא את כל השדות הנדרשים', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/sleep/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                date: sleepDate,
                duration: parseFloat(duration),
                quality: parseInt(quality),
                wake_up_ease: parseInt(wakeUpEase),
                energy_level: parseInt(energyLevel),
                notes: notes
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(JSON.stringify(errorData));
        }
        
        showAlert('נתוני השינה נוספו בהצלחה', 'success');
        navigateTo('dashboard');
    } catch (error) {
        console.error('Error submitting sleep data:', error);
        showAlert('שגיאה בהוספת נתוני שינה. נסה שוב.', 'error');
    }
}

// Helper function to calculate average of array values
function calculateAverage(arr, key) {
    if (!arr || arr.length === 0) return 0;
    return arr.reduce((sum, item) => sum + item[key], 0) / arr.length;
}

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('he-IL', { day: 'numeric', month: 'numeric' });
}

// Generate star rating display
function getRatingStars(rating) {
    const maxRating = 5;
    let stars = '';
    
    for (let i = 1; i <= maxRating; i++) {
        if (i <= rating) {
            stars += '★'; // Filled star
        } else {
            stars += '☆'; // Empty star
        }
    }
    
    return stars;
}

// Show alert message
function showAlert(message, type) {
    const alertsContainer = document.getElementById('alerts');
    if (!alertsContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    alertsContainer.appendChild(alert);
    
    // Remove after 5 seconds
    setTimeout(() => {
        alertsContainer.removeChild(alert);
    }, 5000);
} 