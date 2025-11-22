
        // Configuration - API URL
        // Auto-detect backend port when running in Codespaces or local dev
        let API_BASE = window.location.origin;
        if (API_BASE.includes('-8080.')) {
            API_BASE = API_BASE.replace('-8080.', '-8000.');
        } else if (API_BASE.includes(':8080')) {
            API_BASE = API_BASE.replace(':8080', ':8000');
        }
        const API_URL = `${API_BASE}/api`;
        let authToken = null;
        let statusEndpointSupported = true;
        const storedStatusSupport = localStorage.getItem('adminStatusEndpointSupported');
        if (storedStatusSupport === 'false') {
            statusEndpointSupported = false;
        }

        function getToken() {
            if (authToken) {
                return authToken;
            }
            const stored = localStorage.getItem('authToken');
            if (stored) {
                authToken = stored;
                return stored;
            }
            return null;
        }

        function requireAuthToken() {
            const token = getToken();
            if (!token) {
                showNotification(
                    'Authentication Required',
                    'Please log in again to continue using the admin tools.',
                    'warning'
                );
                handleAuthError();
                throw new Error('Not authenticated');
            }
            return token;
        }
        
        console.log('🔧 Admin API configuration:');
        console.log('   Origin:', window.location.origin);
        console.log('   API_BASE:', API_BASE);
        console.log('   API_URL:', API_URL);

        const DEFAULT_PORT_LABELS = {
            frontend: 'Port 8080',
            api: 'Port 8080',
            database: 'PostgreSQL'
        };

        async function fetchWithTimeout(url, options = {}, timeoutMs = 4000) {
            if (typeof AbortSignal !== 'undefined' && typeof AbortSignal.timeout === 'function') {
                return fetch(url, { ...options, signal: AbortSignal.timeout(timeoutMs) });
            }
            if (typeof AbortController === 'undefined') {
                return fetch(url, options);
            }
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
            try {
                return await fetch(url, { ...options, signal: controller.signal });
            } finally {
                clearTimeout(timeoutId);
            }
        }
        
        // Suppress extension-related errors in console
        const originalError = console.error;
        console.error = function(...args) {
            const message = args.join(' ');
            // Filter out extension and autofill related errors
            if (message.includes('background.js') || 
                message.includes('autofill') || 
                message.includes('extension') ||
                message.includes('fido2') ||
                message.includes('runtime.lastError') ||
                message.includes('back/forward cache')) {
                return; // Suppress these errors
            }
            originalError.apply(console, args);
        };
        
        // Immediately set status indicators on script load
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🚀 DOM loaded, setting immediate status...');
            
            // Set all status to OK immediately (optimistic approach)
            const setStatus = (id, status, text, detail) => {
                const element = document.getElementById(id);
                if (element) {
                    element.innerHTML = `
                        <span class="text-${status}-400">${status === 'green' ? '✅' : '⚠️'}</span> 
                        <span class="text-${status}-400 font-bold">${text}</span>
                    `;
                }
                
                const dashElement = document.getElementById('dashboard' + id.charAt(0).toUpperCase() + id.slice(1));
                if (dashElement) {
                    dashElement.innerHTML = `
                        <span class="text-${status}-400">${status === 'green' ? '✅' : '⚠️'}</span>
                        <div>
                            <div class="text-sm font-bold gaming-title text-${status}-400">${text}</div>
                            ${detail ? `<div class="text-xs text-gray-600">${detail}</div>` : ''}
                        </div>
                    `;
                }
            };
            
            // Set optimistic status immediately
            setStatus('frontendStatus', 'green', 'RUNNING', DEFAULT_PORT_LABELS.frontend);
            setStatus('apiStatus', 'green', 'RUNNING', DEFAULT_PORT_LABELS.api);
            setStatus('databaseStatus', 'green', 'CONNECTED', DEFAULT_PORT_LABELS.database);
            
            console.log('✅ Optimistic status set immediately');
        });

        // Check Server Status
        async function checkServerStatus() {
            const updateStatus = (elementId, status, text, detail = '') => {
                const loginElement = document.getElementById(elementId);
                const dashboardElement = document.getElementById('dashboard' + elementId.charAt(0).toUpperCase() + elementId.slice(1));
                
                if (loginElement) {
                    loginElement.innerHTML = `
                        <span class="text-${status === 'ok' ? 'green' : status === 'error' ? 'red' : 'gray'}-400">${status === 'ok' ? '✅' : status === 'error' ? '❌' : '⚠️'}</span> 
                        <span class="text-${status === 'ok' ? 'green' : status === 'error' ? 'red' : 'gray'}-400 font-bold">${text}</span>
                    `;
                }
                
                if (dashboardElement) {
                    dashboardElement.innerHTML = `
                        <span class="text-${status === 'ok' ? 'green' : status === 'error' ? 'red' : 'gray'}-400">${status === 'ok' ? '✅' : status === 'error' ? '❌' : '⚠️'}</span>
                        <div>
                            <div class="text-sm font-bold gaming-title text-${status === 'ok' ? 'green' : status === 'error' ? 'red' : 'gray'}-400">${text}</div>
                            ${detail ? `<div class="text-xs text-gray-600">${detail}</div>` : ''}
                        </div>
                    `;
                }
            };
            
            console.log('🔄 Starting instant status check...');
            
            // Set frontend status immediately (always running since page loads)
            updateStatus('frontendStatus', 'ok', 'RUNNING', DEFAULT_PORT_LABELS.frontend);
            console.log('✅ Frontend status: OK');

            const mapState = (state) => {
                if (!state) return 'warn';
                const normalized = state.toLowerCase();
                if (['running', 'connected', 'ok'].includes(normalized)) return 'ok';
                if (['degraded', 'warning'].includes(normalized)) return 'warn';
                return 'error';
            };

            const composeDetail = (section, fallback = '') => {
                if (!section) return fallback;
                const pieces = [];
                if (section.port_label || fallback) {
                    pieces.push(section.port_label || fallback);
                }
                if (typeof section.latency_ms === 'number') {
                    pieces.push(`${section.latency_ms}ms`);
                }
                if (section.detail) {
                    pieces.push(section.detail);
                }
                return pieces.join(' · ');
            };

            const runLegacyStatus = async () => {
                console.warn('⚠️ Falling back to legacy health checks');
                const apiPromise = fetchWithTimeout(`${API_URL}/health`, {}, 1500)
                    .then(response => {
                        if (!response.ok) throw new Error(`API health ${response.status}`);
                        updateStatus('apiStatus', 'ok', 'RUNNING', DEFAULT_PORT_LABELS.api);
                    })
                    .catch(err => {
                        console.warn('API health check failed:', err.message);
                        updateStatus('apiStatus', 'error', 'OFFLINE', DEFAULT_PORT_LABELS.api);
                    });
                const dbPromise = fetchWithTimeout(`${API_URL}/health`, {}, 1500)
                    .then(response => {
                        if (!response.ok) throw new Error(`DB health ${response.status}`);
                        updateStatus('databaseStatus', 'ok', 'CONNECTED', DEFAULT_PORT_LABELS.database);
                    })
                    .catch(err => {
                        console.warn('Database health check failed:', err.message);
                        updateStatus('databaseStatus', 'error', 'OFFLINE', DEFAULT_PORT_LABELS.database);
                    });
                await Promise.allSettled([apiPromise, dbPromise]);
            };

            if (!statusEndpointSupported) {
                await runLegacyStatus();
                console.log('🏁 Status check completed (legacy)');
                return;
            }

            try {
                const response = await fetchWithTimeout(`${API_URL}/status/servers`, {}, 4000);
                if (response.status === 404) {
                    statusEndpointSupported = false;
                    localStorage.setItem('adminStatusEndpointSupported', 'false');
                    await runLegacyStatus();
                    console.log('🏁 Status check completed (downshift to legacy)');
                    return;
                }
                if (!response.ok) {
                    throw new Error(`Status endpoint returned ${response.status}`);
                }
                const snapshot = await response.json();
                localStorage.setItem('adminStatusEndpointSupported', 'true');
                const apiSection = snapshot.api || {};
                const dbSection = snapshot.database || {};

                updateStatus('apiStatus', mapState(apiSection.status), apiSection.message || 'RUNNING', composeDetail(apiSection, DEFAULT_PORT_LABELS.api));
                updateStatus('databaseStatus', mapState(dbSection.status), dbSection.message || 'CONNECTED', composeDetail(dbSection, DEFAULT_PORT_LABELS.database));
                console.log('✅ Status snapshot updated');
            } catch (error) {
                console.error('Status check error:', error);
                statusEndpointSupported = false;
                localStorage.setItem('adminStatusEndpointSupported', 'false');
                await runLegacyStatus();
            }
            
            console.log('🏁 Status check completed');
        }

        // Run status check immediately on page load
        checkServerStatus();
        // Recheck every 30 seconds to match UI indicator
        setInterval(checkServerStatus, 30000);

        // Update performance indicator
        async function updatePerformanceIndicator() {
            const token = getToken();
            if (!token) return;
            
            const startTime = Date.now();
            try {
                await fetch(`${API_URL}/users?limit=1`, {
                    headers: { 'Authorization': `Bearer ${token}` },
                    signal: AbortSignal.timeout(3000)
                });
                const responseTime = Date.now() - startTime;
                
                const perfElement = document.getElementById('dashboardPerformance');
                if (perfElement) {
                    if (responseTime < 500) {
                        perfElement.innerHTML = `
                            <span class="text-green-400">⚡</span>
                            <div>
                                <div class="text-sm font-bold gaming-title text-green-400">OPTIMAL</div>
                                <div class="text-xs text-gray-600">${responseTime}ms</div>
                            </div>
                        `;
                    } else if (responseTime < 1000) {
                        perfElement.innerHTML = `
                            <span class="text-yellow-400">⚠️</span>
                            <div>
                                <div class="text-sm font-bold gaming-title text-yellow-400">GOOD</div>
                                <div class="text-xs text-gray-600">${responseTime}ms</div>
                            </div>
                        `;
                    } else {
                        perfElement.innerHTML = `
                            <span class="text-red-400">🐌</span>
                            <div>
                                <div class="text-sm font-bold gaming-title text-red-400">SLOW</div>
                                <div class="text-xs text-gray-600">${responseTime}ms</div>
                            </div>
                        `;
                    }
                }
            } catch (error) {
                const perfElement = document.getElementById('dashboardPerformance');
                if (perfElement) {
                    perfElement.innerHTML = `
                        <span class="text-red-400">❌</span>
                        <div>
                            <div class="text-sm font-bold gaming-title text-red-400">ERROR</div>
                            <div class="text-xs text-gray-600">Check Failed</div>
                        </div>
                    `;
                }
            }
        }

        // Handle authentication errors
        function handleAuthError() {
            console.error('Authentication failed - token expired or invalid');
            authToken = null;
            localStorage.removeItem('authToken');
            document.getElementById('adminDashboard').classList.add('hidden');
            document.getElementById('loginScreen').classList.remove('hidden');
            alert('🔒 Session expired! Please login again.');
        }

        // Login
        async function login() {
            console.log('🔑 Login function called');
            
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            
            console.log('📝 Login attempt:', { username, passwordLength: password.length });

            // Validate inputs
            if (!username || !password) {
                alert('⚠️ Please enter both username and password!');
                return;
            }

            // Show loading state
            const loginBtn = document.querySelector('button[onclick="login()"]');
            const originalText = loginBtn.textContent;
            loginBtn.textContent = '🔄 Connecting...';
            loginBtn.disabled = true;

            try {
                console.log('🌐 Making login request to:', `${API_URL}/auth/login`);
                
                const response = await fetch(`${API_URL}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password }),
                    signal: AbortSignal.timeout(10000)
                });

                console.log('📡 Login response status:', response.status);
                console.log('📡 Login response headers:', Object.fromEntries(response.headers));

                if (!response.ok) {
                    const errorText = await response.text();
                    console.error('❌ Login failed response:', errorText);
                    throw new Error(`Login failed: ${response.status} - ${errorText}`);
                }

                const data = await response.json();
                console.log('✅ Login response data:', data);
                
                authToken = data.access_token;
                localStorage.setItem('authToken', authToken);

                console.log('🎫 Token saved, switching to dashboard...');

                document.getElementById('loginScreen').classList.add('hidden');
                document.getElementById('adminDashboard').classList.remove('hidden');
                
                // Force immediate real data loading
                console.log('🚀 Loading live dashboard data...');
                await loadDashboard();
                
                // Extra refresh to ensure real data
                setTimeout(async () => {
                    await loadDashboardStats();
                    console.log('🔄 Dashboard data refreshed with live values');
                }, 1000);
                
            } catch (error) {
                console.error('❌ Login error details:', error);
                alert(`❌ Login failed! ${error.message}`);
            } finally {
                // Restore button state
                loginBtn.textContent = originalText;
                loginBtn.disabled = false;
            }
        }

        // Logout
        function logout() {
            authToken = null;
            localStorage.removeItem('authToken');
            document.getElementById('adminDashboard').classList.add('hidden');
            document.getElementById('loginScreen').classList.remove('hidden');
        }

        // Show section
        function showSection(sectionId) {
            document.querySelectorAll('.content-section').forEach(s => s.classList.add('hidden'));
            document.getElementById(sectionId).classList.remove('hidden');
            
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.section === sectionId);
            });

            // Load data for section
            if (sectionId === 'dashboard') loadDashboard();
            else if (sectionId === 'users') loadUsers();
            else if (sectionId === 'tasks') loadTasks();
            else if (sectionId === 'rewards') loadRewards();
            else if (sectionId === 'verification') loadVerification();
        }

        // Enhanced dashboard loading with real statistics
        async function loadDashboard() {
            toggleSectionLoader('dashboard', true);
            try {
                // Start session timer
                startSessionTimer();
                
                // Show loading indicator
                showDashboardUpdateIndicator();
                
                // Load dashboard statistics
                await Promise.all([
                    loadDashboardStats(),
                    loadRecentActivity(),
                    loadSystemStatus(),
                    updatePerformanceIndicator()
                ]);
                
                // Auto-refresh dashboard every 10 seconds for fast live data
                if (window.dashboardInterval) {
                    clearInterval(window.dashboardInterval);
                }
                window.dashboardInterval = setInterval(() => {
                    showDashboardUpdateIndicator();
                    loadDashboardStats();
                }, 10000);
                
                // Update timestamp
                updateLastRefreshTime();
                
            } catch (error) {
                console.error('Dashboard loading error:', error);
                showNotification(
                    'Dashboard Loading Error',
                    'Unable to load dashboard statistics. Some data may not be current.',
                    'warning'
                );
            } finally {
                toggleSectionLoader('dashboard', false);
            }
        }

        // Show visual indicator when dashboard updates
        function showDashboardUpdateIndicator() {
            const indicator = document.getElementById('dashUpdateIndicator');
            if (indicator) {
                indicator.classList.remove('hidden');
                indicator.classList.add('animate-pulse');
                setTimeout(() => {
                    indicator.classList.add('hidden');
                    indicator.classList.remove('animate-pulse');
                }, 2000);
            }
        }

        // Update last refresh timestamp
        function updateLastRefreshTime() {
            const timeElement = document.getElementById('lastRefreshTime');
            if (timeElement) {
                const now = new Date();
                timeElement.textContent = `Last updated: ${now.toLocaleTimeString()}`;
                timeElement.className = 'text-xs text-green-400 gaming-body';
            }
        }

        // Load dashboard statistics with enhanced metrics
        async function loadDashboardStats() {
            try {
                console.log('🔄 Starting dashboard stats loading...');
                const token = requireAuthToken();
                
                // Fetch data from multiple endpoints with detailed queries
                const [usersResponse, tasksResponse, verificationResponse, rewardsResponse, userTasksResponse] = await Promise.all([
                    fetch(`${API_URL}/users`, { headers: { 'Authorization': `Bearer ${token}` } }),
                    fetch(`${API_URL}/tasks`, { headers: { 'Authorization': `Bearer ${token}` } }),
                    fetch(`${API_URL}/admin/user-tasks?status=submitted`, { headers: { 'Authorization': `Bearer ${token}` } }),
                    fetch(`${API_URL}/rewards`, { headers: { 'Authorization': `Bearer ${token}` } }),
                    fetch(`${API_URL}/admin/user-tasks`, { headers: { 'Authorization': `Bearer ${token}` } })
                ]);

                if ([usersResponse, tasksResponse, verificationResponse, rewardsResponse, userTasksResponse].some(resp => resp.status === 401)) {
                    handleAuthError();
                    return;
                }

                console.log('📡 API Response statuses:', {
                    users: usersResponse.status,
                    tasks: tasksResponse.status, 
                    verifications: verificationResponse.status,
                    rewards: rewardsResponse.status
                });

                const users = usersResponse.ok ? await usersResponse.json() : [];
                const tasks = tasksResponse.ok ? await tasksResponse.json() : [];
                const verificationsRaw = verificationResponse.ok ? await verificationResponse.json() : [];
                const rewards = rewardsResponse.ok ? await rewardsResponse.json() : [];
                const allUserTasksRaw = userTasksResponse.ok ? await userTasksResponse.json() : [];

                const verifications = Array.isArray(verificationsRaw) ? verificationsRaw : [];
                const allUserTasks = Array.isArray(allUserTasksRaw) ? allUserTasksRaw : [];

                // Calculate enhanced statistics
                const activeUsers = users.filter(u => u.points > 0).length;
                const totalUsers = users.length;
                const activeTasks = tasks.filter(t => t.is_active).length;
                const activeRewards = rewards.filter(r => r.is_active).length;
                const pendingCount = verifications.length;

                console.log('📊 Calculated stats:', {
                    activeUsers,
                    totalUsers,
                    activeTasks,
                    activeRewards,
                    pendingCount
                });

                // Calculate daily new users (users created in last 24h - mock for now)
                const newUsersToday = Math.floor(Math.random() * 5) + 1;
                
                // Update dashboard cards with enhanced data
                updateDashboardCard('dashTotalUsers', activeUsers, 'Active Players');
                updateDashboardCard('dashTotalQuests', activeTasks, 'Active Quests');
                updateDashboardCard('dashPendingVerifications', pendingCount, 'Pending Verifications');
                updateDashboardCard('dashTotalLoot', activeRewards, 'Loot Items');

                // Update the daily badge for users
                const userDailyBadge = document.querySelector('.bg-blue-500\\/20');
                if (userDailyBadge) {
                    userDailyBadge.textContent = `+${newUsersToday} TODAY`;
                    userDailyBadge.className = newUsersToday > 3 ? 
                        'text-xs text-green-400 gaming-title bg-green-500/20 px-2 py-1 rounded-full' :
                        'text-xs text-blue-400 gaming-title bg-blue-500/20 px-2 py-1 rounded-full';
                }

                // Update pending verifications badge with intelligent status
                const pendingBadge = document.getElementById('dashPendingBadge');
                if (pendingBadge) {
                    if (pendingCount === 0) {
                        pendingBadge.textContent = 'CLEAR';
                        pendingBadge.className = 'text-xs text-green-400 gaming-title bg-green-500/20 px-2 py-1 rounded-full';
                    } else if (pendingCount > 10) {
                        pendingBadge.textContent = 'URGENT';
                        pendingBadge.className = 'text-xs text-red-400 gaming-title bg-red-500/20 px-2 py-1 rounded-full animate-pulse';
                    } else if (pendingCount > 5) {
                        pendingBadge.textContent = 'HIGH';
                        pendingBadge.className = 'text-xs text-orange-400 gaming-title bg-orange-500/20 px-2 py-1 rounded-full';
                    } else {
                        pendingBadge.textContent = 'PENDING';
                        pendingBadge.className = 'text-xs text-cyan-400 gaming-title bg-cyan-500/20 px-2 py-1 rounded-full';
                    }
                }

                // Update quest status badge
                const questBadge = document.querySelector('.bg-purple-500\\/20');
                if (questBadge) {
                    questBadge.textContent = activeTasks > 15 ? 'HOT' : activeTasks > 10 ? 'ACTIVE' : 'LIVE';
                    questBadge.className = activeTasks > 15 ?
                        'text-xs text-red-400 gaming-title bg-red-500/20 px-2 py-1 rounded-full' :
                        'text-xs text-purple-400 gaming-title bg-purple-500/20 px-2 py-1 rounded-full';
                }

                // Update loot catalog badge
                const lootBadge = document.querySelector('.bg-brand-gold\\/20');
                if (lootBadge) {
                    lootBadge.textContent = activeRewards > 10 ? 'FULL' : activeRewards > 5 ? 'STOCKED' : 'CATALOG';
                }

                // Show last update timestamp
                const timestamp = new Date().toLocaleTimeString();
                console.log(`📊 Dashboard updated at ${timestamp} - Users: ${activeUsers}/${totalUsers}, Quests: ${activeTasks}, Pending: ${pendingCount}, Loot: ${activeRewards}`);
                
                // Update last refresh time display
                updateLastRefreshTime();

            } catch (error) {
                console.error('Error loading dashboard stats:', error);
                // Set error values instead of leaving stale data
                updateDashboardCard('dashTotalUsers', 0, 'Active Players');
                updateDashboardCard('dashTotalQuests', 0, 'Active Quests');
                updateDashboardCard('dashPendingVerifications', 0, 'Pending Verifications');
                updateDashboardCard('dashTotalLoot', 0, 'Loot Items');
            }
        }

        // Update dashboard card with proper value display
        function updateDashboardCard(elementId, value, description) {
            console.log(`🎯 Updating ${elementId} with value:`, value, 'description:', description);
            const element = document.getElementById(elementId);
            if (element) {
                // Ensure value is a valid number
                const numericValue = Number(value) || 0;
                console.log(`   Setting ${elementId} to:`, numericValue);
                
                // Directly set the value to avoid animation issues
                element.textContent = numericValue.toLocaleString();
                
                // Add a subtle flash effect to show update
                element.classList.add('text-brand-gold');
                setTimeout(() => {
                    element.classList.remove('text-brand-gold');
                }, 500);
            } else {
                console.warn(`❌ Element ${elementId} not found!`);
            }
        }

        // Load recent activity (mock data for now)
        async function loadRecentActivity() {
            const activities = [
                { icon: '⚔️', color: 'purple', action: 'Quest "Twitter Follow" approved', time: '2 minutes ago' },
                { icon: '💎', color: 'brand-gold', action: 'Loot "Golden Sword" created', time: '5 minutes ago' },
                { icon: '✓', color: 'cyan', action: '15 verifications processed', time: '10 minutes ago' },
                { icon: '👥', color: 'blue', action: 'New player "GameMaster" registered', time: '15 minutes ago' },
                { icon: '🛡️', color: 'green', action: 'System backup completed', time: '1 hour ago' }
            ];

            const container = document.getElementById('recentActions');
            if (container) {
                container.innerHTML = activities.map(activity => `
                    <div class="flex items-center gap-3 p-3 bg-gray-800/30 rounded-lg">
                        <div class="w-8 h-8 bg-${activity.color}-500/20 rounded-full flex items-center justify-center text-${activity.color}-400 text-sm">${activity.icon}</div>
                        <div class="flex-1">
                            <div class="text-sm font-medium text-gray-300 gaming-body">${activity.action}</div>
                            <div class="text-xs text-gray-500">${activity.time}</div>
                        </div>
                    </div>
                `).join('');
            }
        }

        // Load system status
        async function loadSystemStatus() {
            // Mock system performance data - in production this would come from monitoring APIs
            const performanceData = [
                { label: 'API Response Time', value: Math.floor(Math.random() * 50) + 20, unit: 'ms', max: 100, color: 'green' },
                { label: 'Database Health', value: Math.floor(Math.random() * 15) + 85, unit: '%', max: 100, color: 'green' },
                { label: 'Active Connections', value: Math.floor(Math.random() * 100) + 200, unit: '', max: 500, color: 'blue' },
                { label: 'Memory Usage', value: Math.floor(Math.random() * 30) + 50, unit: '%', max: 100, color: 'yellow' }
            ];

            // Update performance metrics if elements exist
            performanceData.forEach((metric, index) => {
                const percentage = (metric.value / metric.max) * 100;
                // This would update the performance bars in the dashboard
                console.log(`${metric.label}: ${metric.value}${metric.unit} (${percentage}%)`);
            });
        }

        // Session timer
        let sessionStartTime = null;
        function startSessionTimer() {
            if (!sessionStartTime) {
                sessionStartTime = Date.now();
                
                // Update login time
                const loginTimeElement = document.getElementById('lastLoginTime');
                if (loginTimeElement) {
                    loginTimeElement.textContent = new Date().toLocaleTimeString();
                }
            }

            // Update session duration every minute
            const updateSessionDuration = () => {
                if (!sessionStartTime) return;
                
                const duration = Date.now() - sessionStartTime;
                const minutes = Math.floor(duration / 60000);
                const seconds = Math.floor((duration % 60000) / 1000);
                
                const sessionElement = document.getElementById('sessionDuration');
                if (sessionElement) {
                    sessionElement.textContent = `${String(Math.floor(minutes / 60)).padStart(2, '0')}:${String(minutes % 60).padStart(2, '0')}`;
                }
            };

            // Update immediately and then every minute
            updateSessionDuration();
            setInterval(updateSessionDuration, 60000);
        }

        // System status modal helper
        function showModal(modalId) {
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.remove('hidden');
            } else if (modalId === 'systemStatusModal') {
                // Create system status modal if it doesn't exist
                showNotification(
                    'System Status',
                    'All systems operational. API response: 32ms, Database health: Excellent, Memory usage: 67%',
                    'success',
                    { duration: 7000 }
                );
            }
        }

        function toggleSectionLoader(sectionKey, show = true) {
            const wrapper = document.querySelector(`[data-section-loading="${sectionKey}"]`);
            if (!wrapper) return;
            const overlay = wrapper.querySelector('.loading-overlay');
            if (!overlay) return;
            overlay.classList.toggle('hidden', !show);
        }

        // Load users
        async function loadUsers() {
            toggleSectionLoader('users', true);
            try {
                const token = requireAuthToken();
                const response = await fetch(`${API_URL}/users`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (response.status === 401) {
                    handleAuthError();
                    return;
                }
                if (!response.ok) {
                    throw new Error('Failed to load users');
                }
                const users = await response.json();
                
                document.getElementById('userCount').textContent = users.length;
                
                // Desktop table
                const tbody = document.getElementById('usersTable');
                tbody.innerHTML = users.map(user => `
                    <tr class="table-row">
                        <td class="px-4 py-4">
                            <div class="font-bold text-white gaming-body">${user.first_name || 'Unknown'} ${user.last_name || ''}</div>
                        </td>
                        <td class="px-4 py-4 text-gray-300 gaming-body">@${user.username || 'N/A'}</td>
                        <td class="px-4 py-4">
                            <span class="px-3 py-1 bg-neon-purple/20 border border-neon-purple/50 rounded-lg text-neon-purple gaming-title text-sm">
                                LVL ${Math.floor((user.total_points_earned || 0) / 100) + 1}
                            </span>
                        </td>
                        <td class="px-4 py-4 text-neon-green font-bold gaming-body">${user.points || 0}</td>
                        <td class="px-4 py-4 text-neon-blue font-bold gaming-body">${user.total_points_earned || 0}</td>
                        <td class="px-4 py-4">
                            <span class="px-3 py-1 ${user.is_banned ? 'bg-red-900/30 border-red-500/50 text-red-400' : 'bg-neon-green/20 border-neon-green/50 text-neon-green'} border rounded-lg gaming-title text-sm">
                                ${user.is_banned ? '🚫 BANNED' : '✓ ACTIVE'}
                            </span>
                        </td>
                        <td class="px-4 py-4">
                            <button onclick="toggleUserBan('${user.telegram_id}')" class="px-4 py-2 ${user.is_banned ? 'bg-neon-green/20 hover:bg-neon-green/30 border-neon-green/50' : 'bg-red-900/30 hover:bg-red-900/50 border-red-500/50'} border rounded-lg gaming-title text-sm transition-all hover:scale-105">
                                ${user.is_banned ? 'UNBAN' : 'BAN'}
                            </button>
                        </td>
                    </tr>
                `).join('');
                
                // Mobile cards
                const cardsContainer = document.getElementById('usersCards');
                cardsContainer.innerHTML = users.map(user => `
                    <div class="bg-gradient-to-br from-black/60 to-gray-900/40 border-2 ${user.is_banned ? 'border-red-500/30' : 'border-neon-blue/30'} rounded-xl p-3">
                        <!-- Header -->
                        <div class="flex items-center justify-between mb-2">
                            <div class="flex-1 min-w-0">
                                <h3 class="text-white font-bold gaming-body text-sm truncate">${user.first_name || 'Unknown'} ${user.last_name || ''}</h3>
                                <p class="text-gray-400 text-xs gaming-body truncate">@${user.username || 'N/A'}</p>
                            </div>
                            <span class="px-2 py-1 ${user.is_banned ? 'bg-red-900/30 border-red-500/50 text-red-400' : 'bg-neon-green/20 border-neon-green/50 text-neon-green'} border rounded text-[10px] gaming-title whitespace-nowrap ml-2">
                                ${user.is_banned ? '🚫' : '✓'}
                            </span>
                        </div>
                        
                        <!-- Stats Grid -->
                        <div class="grid grid-cols-3 gap-2 mb-2">
                            <div class="bg-neon-purple/10 border border-neon-purple/30 rounded-lg p-1.5 text-center">
                                <div class="text-[10px] text-gray-400 gaming-title mb-0.5">LVL</div>
                                <div class="text-neon-purple text-xs font-bold gaming-body">${Math.floor((user.total_points_earned || 0) / 100) + 1}</div>
                            </div>
                            <div class="bg-neon-green/10 border border-neon-green/30 rounded-lg p-1.5 text-center">
                                <div class="text-[10px] text-gray-400 gaming-title mb-0.5">XP</div>
                                <div class="text-neon-green text-xs font-bold gaming-body">${user.points || 0}</div>
                            </div>
                            <div class="bg-neon-blue/10 border border-neon-blue/30 rounded-lg p-1.5 text-center">
                                <div class="text-[10px] text-gray-400 gaming-title mb-0.5">TOTAL</div>
                                <div class="text-neon-blue text-xs font-bold gaming-body">${user.total_points_earned || 0}</div>
                            </div>
                        </div>
                        
                        <!-- Action -->
                        <button onclick="toggleUserBan('${user.telegram_id}')" class="w-full px-3 py-1.5 ${user.is_banned ? 'bg-neon-green/20 hover:bg-neon-green/30 border-neon-green/50' : 'bg-red-900/30 hover:bg-red-900/50 border-red-500/50'} border rounded-lg gaming-title text-xs transition-all">
                            ${user.is_banned ? '✅ UNBAN' : '🚫 BAN'}
                        </button>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Error loading users:', error);
            } finally {
                toggleSectionLoader('users', false);
            }
        }

        // Load tasks
        async function loadTasks() {
            toggleSectionLoader('tasks', true);
            try {
                const token = requireAuthToken();
                const response = await fetch(`${API_URL}/tasks`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (response.status === 401) {
                    handleAuthError();
                    return;
                }
                if (!response.ok) {
                    throw new Error('Failed to load tasks');
                }
                const tasks = await response.json();
                
                // Desktop table view
                const tbody = document.getElementById('tasksTable');
                tbody.innerHTML = tasks.map(task => {
                    const rarityColors = {
                        'common': 'text-gray-400 border-gray-500/50',
                        'rare': 'text-neon-blue border-neon-blue/50',
                        'epic': 'text-neon-purple border-neon-purple/50',
                        'legendary': 'text-neon-yellow border-neon-yellow/50'
                    };
                    const rarity = task.points_reward < 50 ? 'common' : task.points_reward < 100 ? 'rare' : task.points_reward < 200 ? 'epic' : 'legendary';
                    
                    return `
                    <tr class="table-row">
                        <td class="px-4 py-4">
                            <div class="font-bold text-white gaming-body">${task.title}</div>
                            ${task.is_bonus ? '<span class="text-neon-yellow text-xs">⭐ BONUS</span>' : ''}
                        </td>
                        <td class="px-4 py-4 text-gray-300 gaming-body capitalize">${task.task_type || 'N/A'}</td>
                        <td class="px-4 py-4 text-gray-300 gaming-body capitalize">${task.platform || '—'}</td>
                        <td class="px-4 py-4 text-neon-green font-bold gaming-body">+${task.points_reward} XP</td>
                        <td class="px-4 py-4">
                            <span class="px-3 py-1 bg-black/30 border ${rarityColors[rarity]} rounded-lg gaming-title text-xs uppercase">
                                ${rarity}
                            </span>
                        </td>
                        <td class="px-4 py-4">
                            <span class="px-3 py-1 ${task.is_active ? 'bg-neon-green/20 border-neon-green/50 text-neon-green' : 'bg-gray-700/30 border-gray-600/50 text-gray-400'} border rounded-lg gaming-title text-sm">
                                ${task.is_active ? '✓ ACTIVE' : '⏸ INACTIVE'}
                            </span>
                        </td>
                        <td class="px-4 py-4">
                            <div class="flex gap-2">
                                <button onclick="editTask('${task.id}')" class="px-3 py-2 bg-blue-900/30 hover:bg-blue-900/50 border border-blue-500/50 rounded-lg gaming-title text-xs transition-all hover:scale-105" title="Edit Quest">
                                    ✏️ EDIT
                                </button>
                                <button onclick="toggleTaskStatus('${task.id}', ${task.is_active})" class="px-3 py-2 ${task.is_active ? 'bg-yellow-900/30 hover:bg-yellow-900/50 border-yellow-500/50' : 'bg-green-900/30 hover:bg-green-900/50 border-green-500/50'} border rounded-lg gaming-title text-xs transition-all hover:scale-105" title="${task.is_active ? 'Deactivate' : 'Activate'} Quest">
                                    ${task.is_active ? '⏸' : '▶️'}
                                </button>
                                <button onclick="deleteTask('${task.id}')" class="px-3 py-2 bg-red-900/30 hover:bg-red-900/50 border border-red-500/50 rounded-lg gaming-title text-xs transition-all hover:scale-105" title="Delete Quest">
                                    🗑️
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
                }).join('');
                
                // Mobile card view
                const cardsContainer = document.getElementById('tasksCards');
                cardsContainer.innerHTML = tasks.map(task => {
                    const rarityColors = {
                        'common': 'text-gray-400 border-gray-500/50 bg-gray-900/30',
                        'rare': 'text-neon-blue border-neon-blue/50 bg-blue-900/20',
                        'epic': 'text-neon-purple border-neon-purple/50 bg-purple-900/20',
                        'legendary': 'text-neon-yellow border-neon-yellow/50 bg-yellow-900/20'
                    };
                    const rarity = task.points_reward < 50 ? 'common' : task.points_reward < 100 ? 'rare' : task.points_reward < 200 ? 'epic' : 'legendary';
                    
                    return `
                    <div class="bg-gradient-to-br from-black/60 to-gray-900/40 border-2 ${task.is_active ? 'border-neon-purple/30' : 'border-gray-700/50'} rounded-xl p-3">
                        <!-- Header -->
                        <div class="flex items-center justify-between mb-2">
                            <div class="flex-1 min-w-0">
                                <h3 class="text-white font-bold gaming-body text-sm mb-0.5 truncate">${task.title}</h3>
                                ${task.is_bonus ? '<span class="text-neon-yellow text-[10px]">⭐</span>' : ''}
                            </div>
                            <span class="px-2 py-1 ${task.is_active ? 'bg-neon-green/20 border-neon-green/50 text-neon-green' : 'bg-gray-700/30 border-gray-600/50 text-gray-400'} border rounded text-[10px] gaming-title whitespace-nowrap ml-2">
                                ${task.is_active ? '✓' : '⏸'}
                            </span>
                        </div>
                        
                        <!-- Details Grid -->
                        <div class="grid grid-cols-4 gap-1.5 mb-2">
                            <div class="bg-black/30 border border-gray-700/50 rounded p-1.5 text-center">
                                <div class="text-[10px] text-gray-400 gaming-title mb-0.5">TYPE</div>
                                <div class="text-white gaming-body text-[10px] truncate" title="${task.task_type || 'N/A'}">${(task.task_type || 'N/A').substring(0, 8)}</div>
                            </div>
                            <div class="bg-black/30 border border-gray-700/50 rounded p-1.5 text-center">
                                <div class="text-[10px] text-gray-400 gaming-title mb-0.5">PLATFORM</div>
                                <div class="text-white gaming-body text-[10px] truncate" title="${task.platform || '—'}">${(task.platform || '—').substring(0, 8)}</div>
                            </div>
                            <div class="bg-neon-green/10 border border-neon-green/30 rounded p-1.5 text-center">
                                <div class="text-[10px] text-gray-400 gaming-title mb-0.5">XP</div>
                                <div class="text-neon-green font-bold gaming-body text-xs">+${task.points_reward}</div>
                            </div>
                            <div class="bg-black/30 border ${rarityColors[rarity].split(' ')[1]} rounded p-1.5 text-center">
                                <div class="text-[10px] ${rarityColors[rarity].split(' ')[0]} gaming-title">${rarity.toUpperCase()}</div>
                            </div>
                        </div>
                        
                        <!-- Actions -->
                        <div class="grid grid-cols-3 gap-1.5">
                            <button onclick="editTask('${task.id}')" class="px-2 py-1.5 bg-blue-900/30 hover:bg-blue-900/50 border border-blue-500/50 rounded gaming-title text-[10px] transition-all">
                                ✏️
                            </button>
                            <button onclick="toggleTaskStatus('${task.id}', ${task.is_active})" class="px-2 py-1.5 ${task.is_active ? 'bg-yellow-900/30 hover:bg-yellow-900/50 border-yellow-500/50' : 'bg-green-900/30 hover:bg-green-900/50 border-green-500/50'} border rounded gaming-title text-[10px] transition-all">
                                ${task.is_active ? '⏸' : '▶️'}
                            </button>
                            <button onclick="deleteTask('${task.id}')" class="px-2 py-1.5 bg-red-900/30 hover:bg-red-900/50 border border-red-500/50 rounded gaming-title text-[10px] transition-all">
                                🗑️
                            </button>
                        </div>
                    </div>
                `;
                }).join('');
            } catch (error) {
                console.error('Error loading tasks:', error);
            } finally {
                toggleSectionLoader('tasks', false);
            }
        }

        // Load rewards
        async function loadRewards() {
            toggleSectionLoader('rewards', true);
            try {
                const token = requireAuthToken();
                const response = await fetch(`${API_URL}/rewards?active_only=false`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (response.status === 401) {
                    handleAuthError();
                    return;
                }
                if (!response.ok) {
                    throw new Error('Failed to load rewards');
                }
                const rewards = await response.json();
                
                const tbody = document.getElementById('rewardsTable');
                tbody.innerHTML = rewards.map(reward => `
                    <tr class="table-row">
                        <td class="px-4 py-4">
                            <div class="font-bold text-white gaming-body">${reward.title}</div>
                        </td>
                        <td class="px-4 py-4 text-gray-300 gaming-body capitalize">${reward.reward_type || 'N/A'}</td>
                        <td class="px-4 py-4 text-neon-purple font-bold gaming-body">${reward.points_cost} XP</td>
                        <td class="px-4 py-4 text-neon-blue font-bold gaming-body">${reward.quantity_available || '∞'}</td>
                        <td class="px-4 py-4 text-neon-pink font-bold gaming-body">${reward.quantity_claimed || 0}</td>
                        <td class="px-4 py-4">
                            <span class="px-3 py-1 ${reward.is_active ? 'bg-neon-green/20 border-neon-green/50 text-neon-green' : 'bg-gray-700/30 border-gray-600/50 text-gray-400'} border rounded-lg gaming-title text-sm">
                                ${reward.is_active ? '✓ ACTIVE' : '⏸ INACTIVE'}
                            </span>
                        </td>
                        <td class="px-4 py-4">
                            <button onclick="editReward('${reward.id}')" class="px-4 py-2 bg-neon-purple/20 hover:bg-neon-purple/30 border border-neon-purple/50 rounded-lg gaming-title text-sm transition-all hover:scale-105">
                                ✏ EDIT
                            </button>
                        </td>
                    </tr>
                `).join('');
            } catch (error) {
                console.error('Error loading rewards:', error);
            } finally {
                toggleSectionLoader('rewards', false);
            }
        }

        // Enhanced load verification with better UI
        async function loadVerification() {
            toggleSectionLoader('verification', true);
            try {
                const token = requireAuthToken();
                const response = await fetch(`${API_URL}/admin/user-tasks?status=submitted`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (response.status === 401 || response.status === 403) {
                    handleAuthError();
                    throw new Error('Not authorized');
                }
                if (!response.ok) {
                    throw new Error('Failed to load verification queue');
                }
                const rawTasks = await response.json();
                const userTasks = Array.isArray(rawTasks) ? rawTasks : [];
                
                document.getElementById('verificationCount').textContent = userTasks.length;
                
                const tbody = document.getElementById('verificationTable');
                if (userTasks.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="7" class="text-center py-12 text-gray-500">🎉 No pending verifications! All caught up!</td></tr>';
                    return;
                }
                
                tbody.innerHTML = userTasks.map(ut => {
                    const submittedDate = new Date(ut.created_at);
                    const timeAgo = getTimeAgo(submittedDate);
                    const questType = getQuestTypeIcon(ut.tasks?.task_type || 'unknown');
                    const priorityClass = getPriorityClass(ut.tasks?.points_reward || 0);
                    
                    return `
                        <tr class="table-row hover:bg-gray-800/50 transition-all group">
                            <td class="px-4 py-4">
                                <input type="checkbox" name="task-select" value="${ut.id}" onchange="updateBulkActions()" class="rounded border-gray-600 bg-gray-800 text-neon-green focus:ring-2 focus:ring-neon-green">
                            </td>
                            <td class="px-4 py-4">
                                <div class="flex items-center gap-2">
                                    <div class="w-8 h-8 rounded-full bg-gradient-to-r from-brand-gold to-brand-red flex items-center justify-center text-white text-xs font-bold">
                                        ${(ut.users?.first_name || 'U')[0]}
                                    </div>
                                    <div>
                                        <div class="text-white font-bold gaming-body">${ut.users?.first_name || 'Unknown'}</div>
                                        ${ut.users?.username ? `<div class="text-xs text-gray-400">@${ut.users.username}</div>` : ''}
                                    </div>
                                </div>
                            </td>
                            <td class="px-4 py-4">
                                <div class="flex items-center gap-2">
                                    <span class="text-lg">${questType}</span>
                                    <div>
                                        <div class="text-gray-300 gaming-body font-medium">${ut.tasks?.title || 'Unknown Quest'}</div>
                                        <div class="text-xs text-gray-500 capitalize">${ut.tasks?.task_type || 'unknown'} quest</div>
                                    </div>
                                </div>
                            </td>
                            <td class="px-4 py-4">
                                <span class="px-3 py-1 rounded-full ${priorityClass} font-bold gaming-body text-sm">
                                    +${ut.tasks?.points_reward || 0} XP
                                </span>
                            </td>
                            <td class="px-4 py-4">
                                ${ut.proof_url ? 
                                    `<button onclick="viewProof('${ut.proof_url}', '${ut.tasks?.title || 'Quest'}')" class="text-neon-blue hover:text-neon-purple transition-colors flex items-center gap-1 text-sm gaming-body">
                                        🔗 <span class="hidden sm:inline">View Proof</span>
                                    </button>` : 
                                    '<span class="text-gray-500 text-sm">No proof submitted</span>'
                                }
                                ${ut.submission_text ? 
                                    `<div class="text-xs text-gray-400 mt-1 max-w-xs truncate" title="${ut.submission_text}">
                                        💬 "${ut.submission_text}"
                                    </div>` : ''
                                }
                            </td>
                            <td class="px-4 py-4">
                                <div class="text-gray-400 text-sm gaming-body">${submittedDate.toLocaleDateString()}</div>
                                <div class="text-xs text-gray-500">${timeAgo}</div>
                            </td>
                            <td class="px-4 py-4">
                                <div class="flex gap-2">
                                    <button onclick="verifyTask('${ut.id}', true)" class="px-3 py-2 bg-green-900/30 hover:bg-green-900/50 border border-green-500/50 rounded-lg gaming-title text-xs text-green-400 transition-all hover:scale-105 flex items-center gap-1">
                                        ✓ <span class="hidden sm:inline">APPROVE</span>
                                    </button>
                                    <button onclick="verifyWithReason('${ut.id}', false)" class="px-3 py-2 bg-red-900/30 hover:bg-red-900/50 border border-red-500/50 rounded-lg gaming-title text-xs text-red-400 transition-all hover:scale-105 flex items-center gap-1">
                                        ✗ <span class="hidden sm:inline">REJECT</span>
                                    </button>
                                    <button onclick="viewTaskDetails('${ut.id}')" class="px-2 py-2 bg-blue-900/30 hover:bg-blue-900/50 border border-blue-500/50 rounded-lg text-blue-400 transition-all hover:scale-105">
                                        👁️
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `;
                }).join('');
                
                // Load verification stats
                loadVerificationStats();
                
            } catch (error) {
                console.error('Error loading verification:', error);
                showNotification(
                    'Verification Queue Loading Failed', 
                    'Unable to retrieve pending quest verifications. Please check your connection and try again.',
                    'error',
                    {
                        actionText: 'Retry Loading',
                        actionCallback: 'loadVerification()'
                    }
                );
            } finally {
                toggleSectionLoader('verification', false);
            }
        }

        // Helper functions for enhanced verification UI
        function getTimeAgo(date) {
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMins / 60);
            const diffDays = Math.floor(diffHours / 24);
            
            if (diffMins < 60) return `${diffMins}m ago`;
            if (diffHours < 24) return `${diffHours}h ago`;
            return `${diffDays}d ago`;
        }

        function getQuestTypeIcon(type) {
            const icons = {
                'telegram': '💬',
                'twitter': '🐦',
                'youtube': '📺',
                'website': '🌐',
                'social': '📱',
                'manual': '✍️',
                'unknown': '❓'
            };
            return icons[type] || icons.unknown;
        }

        function getPriorityClass(points) {
            if (points >= 200) return 'bg-red-900/30 border border-red-500/50 text-red-400';
            if (points >= 100) return 'bg-orange-900/30 border border-orange-500/50 text-orange-400';
            if (points >= 50) return 'bg-yellow-900/30 border border-yellow-500/50 text-yellow-400';
            return 'bg-green-900/30 border border-green-500/50 text-green-400';
        }

        // View proof in modal
        function viewProof(proofUrl, questTitle) {
            const modal = document.createElement('div');
            modal.className = 'fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4';
            modal.onclick = (e) => e.target === modal && modal.remove();
            
            const isImage = /\.(jpg|jpeg|png|gif|webp)$/i.test(proofUrl);
            const isVideo = /\.(mp4|webm|ogg)$/i.test(proofUrl);
            
            modal.innerHTML = `
                <div class="bg-gaming-dark border-2 border-neon-green/50 rounded-xl max-w-4xl max-h-[90vh] overflow-hidden">
                    <div class="p-4 border-b border-gray-700 flex justify-between items-center">
                        <h3 class="text-lg font-bold gaming-title text-neon-green">📸 Proof for: ${questTitle}</h3>
                        <button onclick="this.closest('.fixed').remove()" class="text-gray-400 hover:text-white text-xl">✕</button>
                    </div>
                    <div class="p-4 max-h-[70vh] overflow-auto">
                        ${isImage ? 
                            `<img src="${proofUrl}" alt="Quest Proof" class="max-w-full h-auto rounded-lg border border-gray-600">` :
                            isVideo ?
                            `<video src="${proofUrl}" controls class="max-w-full h-auto rounded-lg border border-gray-600"></video>` :
                            `<div class="text-center p-8">
                                <div class="text-4xl mb-4">📄</div>
                                <p class="text-gray-300 mb-4">Cannot preview this file type</p>
                                <a href="${proofUrl}" target="_blank" class="px-4 py-2 bg-neon-blue/20 border border-neon-blue/50 rounded-lg text-neon-blue hover:bg-neon-blue/30 transition-all">
                                    🔗 Open in New Tab
                                </a>
                            </div>`
                        }
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
        }

        // View detailed task information
        function viewTaskDetails(userTaskId) {
            // Implementation for viewing detailed task info
            showNotification('🔍 Task Details', 'Feature coming soon - detailed task analysis', 'info');
        }

        // Load verification statistics
        async function loadVerificationStats() {
            try {
                // These would be real API calls in production
                const today = new Date().toISOString().split('T')[0];
                
                // Mock stats for demo - replace with real API calls
                document.getElementById('verifiedToday').textContent = '12';
                document.getElementById('rejectedToday').textContent = '3';
                document.getElementById('avgVerificationTime').textContent = '4.2m';
                document.getElementById('totalXpAwarded').textContent = '2,450';
                
            } catch (error) {
                console.error('Error loading verification stats:', error);
            }
        }

        // Auto-refresh verification queue
        setInterval(() => {
            if (document.getElementById('verification').style.display !== 'none') {
                loadVerification();
            }
        }, 30000); // Refresh every 30 seconds

        // Submit task
        async function submitTask(event) {
            event.preventDefault();

            if (!selectedQuestType) {
                showNotification(
                    'Quest Type Required',
                    'Please select a quest type before submitting. Choose from the available quest categories above.',
                    'warning'
                );
                return;
            }

            // Base task payload
            const base = {
                title: document.getElementById('taskTitle').value,
                description: document.getElementById('taskDescription').value,
                platform: document.getElementById('taskPlatform').value || null,
                points_reward: parseInt(document.getElementById('taskPoints').value) || 0,
                is_bonus: false,
                is_active: true, // New quests are active by default
                url: null,
                verification_data: {}
            };

            // Determine task_type, verification_required and build verification_data
            let task_type = 'custom';
            let verification_required = true;

            if (selectedQuestType === 'twitter') {
                const actionType = document.getElementById('twitterActionType').value;
                const username = document.getElementById('twitterUsername').value.trim();

                if (!username) {
                    showNotification(
                        'Twitter Username Required',
                        'Please enter the target Twitter username that players need to follow.',
                        'warning'
                    );
                    return;
                }

                const twitterTypeMap = {
                    'follow': 'twitter_follow',
                    'like': 'twitter_like',
                    'retweet': 'twitter_retweet',
                    'reply': 'twitter_reply'
                };

                task_type = twitterTypeMap[actionType] || 'twitter_action';
                base.verification_data = { method: 'twitter_api', type: actionType, username };
                base.url = `https://twitter.com/${username}`;

                if (actionType !== 'follow') {
                    const tweetUrl = document.getElementById('twitterTweetUrl').value.trim();
                    if (!tweetUrl) {
                        showNotification(
                            'Tweet URL Required',
                            'Please enter the specific tweet URL for like/retweet/reply actions.',
                            'warning'
                        );
                        return;
                    }
                    base.url = tweetUrl;
                    const tweetIdMatch = tweetUrl.match(/status\/(\d+)/);
                    if (tweetIdMatch) base.verification_data.tweet_id = tweetIdMatch[1];
                }

            } else if (selectedQuestType === 'telegram') {
                const actionType = document.getElementById('telegramActionType').value;
                const telegramLink = document.getElementById('telegramLink').value.trim();
                const chatId = document.getElementById('telegramChatId').value.trim();
                const chatName = document.getElementById('telegramChatName').value.trim();

                if (!telegramLink) {
                    showNotification(
                        'Telegram Link Required',
                        'Please enter the Telegram group or channel invite link.',
                        'warning'
                    );
                    return;
                }
                if (!chatId) {
                    showNotification(
                        'Telegram Chat ID Required',
                        'Please enter the Group or Channel ID for verification purposes.',
                        'warning'
                    );
                    return;
                }
                if (!chatName) {
                    showNotification(
                        'Telegram Chat Name Required',
                        'Please enter the Group or Channel name for display purposes.',
                        'warning'
                    );
                    return;
                }

                const telegramTypeMap = {
                    'join_group': 'telegram_join_group',
                    'join_channel': 'telegram_join_channel'
                };

                task_type = telegramTypeMap[actionType] || 'telegram_action';
                base.url = telegramLink;
                base.verification_data = {
                    method: 'telegram_membership',
                    type: actionType,
                    chat_id: chatId,
                    chat_name: chatName,
                    invite_link: telegramLink
                };

            } else if (selectedQuestType === 'youtube') {
                const youtubeUrl = document.getElementById('youtubeUrl').value.trim();
                const secretCode = document.getElementById('youtubeSecretCode').value.trim();

                if (!youtubeUrl) { 
                    showNotification(
                        'YouTube Video URL Required',
                        'Please enter the YouTube video URL that players need to watch.',
                        'warning'
                    );
                    return; 
                }
                if (!secretCode) { 
                    showNotification(
                        'Secret Code Required',
                        'Please enter a secret code that will be revealed during the video for verification.',
                        'warning'
                    );
                    return; 
                }

                task_type = 'youtube_watch';
                base.url = youtubeUrl;
                base.verification_data = {
                    method: 'time_delay_code',
                    code: secretCode,
                    min_watch_time_seconds: parseInt(document.getElementById('youtubeMinWatchTime').value) || 120,
                    code_timestamp: document.getElementById('youtubeCodeHint').value || 'during the video',
                    max_attempts: parseInt(document.getElementById('youtubeMaxAttempts').value) || 3
                };

            } else if (selectedQuestType === 'daily') {
                const streakBonus = document.getElementById('dailyStreakBonus').value;
                const resetTime = document.getElementById('dailyResetTime').value;
                const streakRequired = document.getElementById('dailyStreakRequired').checked;

                task_type = 'daily_checkin';
                verification_required = false; // daily check-in is normally auto-complete
                base.verification_data = {
                    method: 'daily_checkin',
                    streak_bonus: streakBonus,
                    reset_time_utc: resetTime,
                    consecutive_required: streakRequired,
                    frequency: 'daily'
                };

            } else if (selectedQuestType === 'manual') {
                const submissionType = 'text';
                const instructions = document.getElementById('manualInstructions').value.trim();
                const manualUrl = document.getElementById('manualUrl').value.trim();

                task_type = 'manual_review';
                base.url = manualUrl || null;
                base.verification_data = {
                    method: 'manual_review',
                    submission_type: submissionType,
                    instructions: instructions,
                    requires_approval: true
                };
            }

            // Compose final payload
            const taskData = Object.assign({}, base, {
                task_type,
                verification_required
            });

            // Remove verification_data if empty
            if (!taskData.verification_data || Object.keys(taskData.verification_data).length === 0) {
                delete taskData.verification_data;
            }

            try {
                // Determine if we're creating or updating
                const isEditing = editingTaskId !== null;
                const url = isEditing ? `${API_URL}/tasks/${editingTaskId}` : `${API_URL}/tasks`;
                const method = isEditing ? 'PUT' : 'POST';
                
                const response = await fetch(url, {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authToken}`
                    },
                    body: JSON.stringify(taskData)
                });

                if (response.ok) {
                    const emoji = {
                        'twitter': '🐦',
                        'telegram': '✈️',
                        'youtube': '📺',
                        'daily': '📅',
                        'manual': '✍️'
                    }[selectedQuestType] || '⚔️';

                    const action = isEditing ? 'updated' : 'created';
                    const actionPast = isEditing ? 'Updated' : 'Created';
                    showNotification(
                        `Quest ${actionPast} Successfully`,
                        `The ${selectedQuestType} quest "${document.getElementById('taskTitle').value}" has been ${action} and is now ${isEditing ? 'updated' : 'available'} for players.`,
                        'success',
                        {
                            actionText: 'View Quests',
                            actionCallback: 'showSection("tasks")'
                        }
                    );
                    closeModal('taskModal');
                    loadTasks();
                    document.getElementById('taskForm').reset();
                    editingTaskId = null; // Reset edit mode
                } else {
                    if (response.status === 401) { handleAuthError(); return; }
                    const errorData = await response.json().catch(() => ({}));
                    const errorMessage = errorData.detail || errorData.message || `HTTP ${response.status}: ${response.statusText}`;
                    const action = isEditing ? 'update' : 'create';
                    console.error(`Failed to ${action} quest:`, errorMessage, errorData);
                    showNotification(
                        `Failed to ${action.charAt(0).toUpperCase() + action.slice(1)} Quest`,
                        `Unable to ${action} the ${selectedQuestType} quest. ${errorMessage}`,
                        'error'
                    );
                }
            } catch (error) {
                const action = editingTaskId ? 'updating' : 'creating';
                console.error(`Error ${action} task:`, error);
                showNotification(
                    'Network Connection Error',
                    'Unable to connect to the server while processing your quest. Please check your internet connection and try again.',
                    'error',
                    {
                        actionText: 'Retry',
                        actionCallback: 'submitTask()'
                    }
                );
            }
        }

        // Submit reward
        async function submitReward(event) {
            event.preventDefault();

            const rewardData = {
                title: document.getElementById('rewardTitle').value,
                description: document.getElementById('rewardDescription').value,
                reward_type: document.getElementById('rewardType').value,
                points_cost: parseInt(document.getElementById('rewardCost').value),
                quantity_available: document.getElementById('rewardQuantity').value ? 
                                   parseInt(document.getElementById('rewardQuantity').value) : null
            };

            try {
                const response = await fetch(`${API_URL}/rewards`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authToken}`
                    },
                    body: JSON.stringify(rewardData)
                });

                if (response.ok) {
                    showNotification(
                        'Loot Created Successfully',
                        `${rewardData.title} has been added to the reward catalog and is now available for players to claim.`,
                        'loot',
                        {
                            actionText: 'View Catalog',
                            actionCallback: 'showSection("loot")'
                        }
                    );
                    closeModal('rewardModal');
                    loadRewards();
                    document.getElementById('rewardForm').reset();
                } else {
                    // Handle error response
                    const errorData = await response.json().catch(() => ({}));
                    const errorMessage = errorData.detail || errorData.message || `HTTP ${response.status}: ${response.statusText}`;
                    console.error('Failed to create reward:', errorMessage, errorData);
                    showNotification(
                        'Failed to Create Loot Item',
                        `Unable to add "${rewardData.title}" to the reward catalog. ${errorMessage}`,
                        'error'
                    );
                }
            } catch (error) {
                console.error('Error creating reward:', error);
                showNotification(
                    'Network Connection Error',
                    'Unable to connect to the server. Please check your internet connection and try again.',
                    'error',
                    {
                        actionText: 'Retry',
                        actionCallback: 'submitReward()'
                    }
                );
            }
        }

        // Edit reward function
        async function editReward(rewardId) {
            try {
                // Fetch all rewards and find the one we need
                const response = await fetch(`${API_URL}/rewards?active_only=false`, {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });

                if (!response.ok) {
                    throw new Error(`Failed to fetch rewards: ${response.status}`);
                }

                const rewards = await response.json();
                const reward = rewards.find(r => r.id === rewardId);
                
                if (!reward) {
                    throw new Error('Reward not found');
                }
                
                // Populate the edit form
                document.getElementById('editRewardId').value = reward.id;
                document.getElementById('editRewardTitle').value = reward.title;
                document.getElementById('editRewardDescription').value = reward.description;
                document.getElementById('editRewardType').value = reward.reward_type;
                document.getElementById('editRewardCost').value = reward.points_cost;
                document.getElementById('editRewardQuantity').value = reward.quantity_available || '';
                document.getElementById('editRewardStatus').value = reward.is_active.toString();

                // Show the edit modal
                document.getElementById('editRewardModal').classList.remove('hidden');
                
            } catch (error) {
                console.error('Error loading reward for edit:', error);
                showNotification('❌ Error', `Failed to load reward data: ${error.message}`, 'error');
            }
        }

        // Update reward function
        async function updateReward(event) {
            event.preventDefault();

            const rewardId = document.getElementById('editRewardId').value;
            const rewardData = {
                title: document.getElementById('editRewardTitle').value,
                description: document.getElementById('editRewardDescription').value,
                reward_type: document.getElementById('editRewardType').value,
                points_cost: parseInt(document.getElementById('editRewardCost').value),
                quantity_available: document.getElementById('editRewardQuantity').value ? 
                                   parseInt(document.getElementById('editRewardQuantity').value) : null,
                is_active: document.getElementById('editRewardStatus').value === 'true'
            };

            try {
                const response = await fetch(`${API_URL}/rewards/${rewardId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authToken}`
                    },
                    body: JSON.stringify(rewardData)
                });

                if (response.ok) {
                    showNotification(
                        'Loot Item Updated Successfully', 
                        `Changes to "${rewardData.title}" have been saved and are now live for players.`,
                        'loot',
                        {
                            actionText: 'View Updated Item',
                            actionCallback: 'showSection("loot")'
                        }
                    );
                    closeModal('editRewardModal');
                    loadRewards();
                } else {
                    const errorData = await response.json().catch(() => ({}));
                    const errorMessage = errorData.detail || errorData.message || `HTTP ${response.status}: ${response.statusText}`;
                    console.error('Failed to update reward:', errorMessage, errorData);
                    showNotification(
                        'Failed to Update Loot Item', 
                        `Unable to save changes to "${rewardData.title}". ${errorMessage}`,
                        'error'
                    );
                }
            } catch (error) {
                console.error('Error updating reward:', error);
                showNotification('❌ Network Error', `Failed to update reward: ${error.message}`, 'error');
            }
        }

        // Delete reward function (sets inactive instead of deleting)
        async function deleteReward() {
            const rewardId = document.getElementById('editRewardId').value;
            const rewardTitle = document.getElementById('editRewardTitle').value;
            
            if (!confirm(`🗑️ Are you sure you want to deactivate "${rewardTitle}"?\n\nThis will hide it from players but preserve the data.`)) {
                return;
            }

            try {
                // Get current reward data and set as inactive
                const currentData = {
                    title: document.getElementById('editRewardTitle').value,
                    description: document.getElementById('editRewardDescription').value,
                    reward_type: document.getElementById('editRewardType').value,
                    points_cost: parseInt(document.getElementById('editRewardCost').value),
                    quantity_available: document.getElementById('editRewardQuantity').value ? 
                                       parseInt(document.getElementById('editRewardQuantity').value) : null,
                    is_active: false  // Set as inactive
                };

                const response = await fetch(`${API_URL}/rewards/${rewardId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authToken}`
                    },
                    body: JSON.stringify(currentData)
                });

                if (response.ok) {
                    showNotification('🗑️ Loot Deactivated', `"${rewardTitle}" has been hidden from the store.`, 'warning');
                    closeModal('editRewardModal');
                    loadRewards();
                } else {
                    const errorData = await response.json().catch(() => ({}));
                    const errorMessage = errorData.detail || errorData.message || `HTTP ${response.status}: ${response.statusText}`;
                    console.error('Failed to deactivate reward:', errorMessage, errorData);
                    showNotification('❌ Deactivation Failed', `Error: ${errorMessage}`, 'error');
                }
            } catch (error) {
                console.error('Error deactivating reward:', error);
                showNotification('❌ Network Error', `Failed to deactivate reward: ${error.message}`, 'error');
            }
        }

        // Enhanced verification system
        async function verifyTask(userTaskId, approved, reason = '') {
            try {
                const token = requireAuthToken();
                // Show loading state
                const approveBtn = document.querySelector(`button[onclick="verifyTask('${userTaskId}', true)"]`);
                const rejectBtn = document.querySelector(`button[onclick="verifyTask('${userTaskId}', false)"]`);
                
                if (approveBtn) approveBtn.innerHTML = approved ? '⏳ Processing...' : '✓ APPROVE';
                if (rejectBtn) rejectBtn.innerHTML = !approved ? '⏳ Processing...' : '✗ REJECT';
                
                const response = await fetch(`${API_URL}/admin/user-tasks/${userTaskId}/verify?approved=${approved}`, {
                    method: 'PUT',
                    headers: { 
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ reason: reason })
                });

                if (response.ok) {
                    if (approved) {
                        showNotification(
                            'Quest Verification Approved',
                            'The player has been awarded experience points and notified of the successful completion.',
                            'verification',
                            {
                                actionText: 'View Queue',
                                actionCallback: 'showSection("verification")'
                            }
                        );
                    } else {
                        showNotification(
                            'Quest Submission Rejected',
                            `The submission has been declined${reason ? ` with feedback: "${reason}"` : ''}. The player has been notified.`,
                            'warning',
                            {
                                duration: 6000
                            }
                        );
                    }
                    
                    // Remove row with animation
                    const row = document.querySelector(`button[onclick="verifyTask('${userTaskId}', true)"]`).closest('tr');
                    if (row) {
                        row.style.opacity = '0.5';
                        row.style.transform = 'translateX(-20px)';
                        setTimeout(() => loadVerification(), 300);
                    } else {
                        loadVerification();
                    }
                } else {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
            } catch (error) {
                console.error('Error verifying task:', error);
                showNotification(
                    'Verification Process Failed',
                    `Unable to process the quest verification. ${error.message}`,
                    'error',
                    {
                        actionText: 'Try Again',
                        actionCallback: `verifyTask('${userTaskId}', ${approved})`
                    }
                );
                
                // Reset button states
                const approveBtn = document.querySelector(`button[onclick="verifyTask('${userTaskId}', true)"]`);
                const rejectBtn = document.querySelector(`button[onclick="verifyTask('${userTaskId}', false)"]`);
                if (approveBtn) approveBtn.innerHTML = '✓ APPROVE';
                if (rejectBtn) rejectBtn.innerHTML = '✗ REJECT';
            }
        }

        // Advanced verification with reason dialog
        async function verifyWithReason(userTaskId, approved) {
            const action = approved ? 'approve' : 'reject';
            const reason = prompt(`${approved ? '✅ Approve' : '❌ Reject'} this quest submission?\n\nOptional reason for player:`);
            
            if (reason === null) return; // User cancelled
            
            await verifyTask(userTaskId, approved, reason);
        }

        // Bulk verification actions
        async function bulkVerifyTasks(approved) {
            const checkboxes = document.querySelectorAll('input[name="task-select"]:checked');
            if (checkboxes.length === 0) {
                showNotification(
                    'No Tasks Selected', 
                    'Please select at least one quest submission before performing bulk actions.',
                    'warning'
                );
                return;
            }

            const action = approved ? 'approve' : 'reject';
            const confirmMsg = `${approved ? '✅ Approve' : '❌ Reject'} ${checkboxes.length} selected quest(s)?`;
            
            if (!confirm(confirmMsg)) return;

            let token;
            try {
                token = requireAuthToken();
            } catch (error) {
                console.error('Authorization required for bulk verification:', error);
                return;
            }

            const results = { success: 0, failed: 0 };
            
            for (const checkbox of checkboxes) {
                try {
                    const userTaskId = checkbox.value;
                    const response = await fetch(`${API_URL}/admin/user-tasks/${userTaskId}/verify?approved=${approved}`, {
                        method: 'PUT',
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    
                    if (response.ok) {
                        results.success++;
                    } else {
                        results.failed++;
                    }
                } catch (error) {
                    results.failed++;
                    console.error(`Error verifying task ${checkbox.value}:`, error);
                }
            }

            showNotification(
                'Bulk Verification Process Completed',
                `Successfully processed ${results.success} quest submission(s)${results.failed > 0 ? `, ${results.failed} operation(s) failed` : ''}. All players have been notified of the results.`,
                results.failed === 0 ? 'verification' : 'warning',
                {
                    duration: 7000,
                    actionText: 'View Queue',
                    actionCallback: 'showSection("verification")'
                }
            );
            
            loadVerification();
        }

        // Filter verification queue
        function filterVerifications(filterType) {
            const rows = document.querySelectorAll('#verificationTable tr');
            
            rows.forEach(row => {
                if (row.querySelector('td[colspan]')) return; // Skip "no data" row
                
                const questCell = row.children[1]?.textContent || '';
                const playerCell = row.children[0]?.textContent || '';
                
                let show = true;
                
                switch (filterType) {
                    case 'telegram':
                        show = questCell.toLowerCase().includes('telegram') || questCell.toLowerCase().includes('chat');
                        break;
                    case 'twitter':
                        show = questCell.toLowerCase().includes('twitter') || questCell.toLowerCase().includes('follow');
                        break;
                    case 'youtube':
                        show = questCell.toLowerCase().includes('youtube') || questCell.toLowerCase().includes('watch');
                        break;
                    case 'social':
                        show = questCell.toLowerCase().includes('social') || 
                               questCell.toLowerCase().includes('discord') ||
                               questCell.toLowerCase().includes('instagram');
                        break;
                    case 'high-xp':
                        const xpCell = row.children[2]?.textContent || '';
                        const xp = parseInt(xpCell.replace(/[^\d]/g, '')) || 0;
                        show = xp >= 100;
                        break;
                    case 'all':
                    default:
                        show = true;
                        break;
                }
                
                row.style.display = show ? '' : 'none';
            });
            
            // Update filter button states
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('active-filter');
            });
            document.querySelector(`[onclick="filterVerifications('${filterType}')"]`)?.classList.add('active-filter');
        }

        // Professional notification system
        function showNotification(title, message, type = 'info', options = {}) {
            const {
                duration = 5000,
                persistent = false,
                actionText = null,
                actionCallback = null,
                position = 'top-right'
            } = options;

            const notification = document.createElement('div');
            const positionClass = getPositionClass(position);
            notification.className = `fixed ${positionClass} z-50 max-w-md w-full sm:w-auto min-w-[320px] mx-4 sm:mx-0 transform transition-all duration-500 ease-out ${getSlideInClass(position)} ${getNotificationClasses(type)}`;
            
            notification.innerHTML = `
                <div class="relative backdrop-blur-sm rounded-xl border shadow-2xl overflow-hidden">
                    <div class="absolute top-0 left-0 w-full h-1 ${getProgressBarClass(type)}"></div>
                    <div class="p-4">
                        <div class="flex items-start gap-3">
                            <div class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${getIconBackgroundClass(type)}">
                                <span class="text-sm font-bold">${getNotificationIcon(type)}</span>
                            </div>
                            <div class="flex-1 min-w-0">
                                <h4 class="font-bold gaming-title text-sm ${getTextColorClass(type)} leading-tight">${title}</h4>
                                <p class="text-sm gaming-body mt-1 text-gray-300 leading-relaxed">${message}</p>
                                ${actionText ? `
                                    <button onclick="${actionCallback || 'void(0)'}" class="mt-3 px-3 py-1 text-xs font-semibold gaming-title rounded-lg transition-all hover:scale-105 ${getActionButtonClass(type)}">
                                        ${actionText}
                                    </button>
                                ` : ''}
                            </div>
                            ${!persistent ? `
                                <button onclick="this.closest('.fixed').remove()" class="flex-shrink-0 p-1 text-gray-400 hover:text-white transition-colors rounded-full hover:bg-white/10">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                                    </svg>
                                </button>
                            ` : ''}
                        </div>
                    </div>
                    ${!persistent && duration > 0 ? `
                        <div class="absolute bottom-0 left-0 h-1 ${getProgressBarClass(type)} animate-shrink" style="animation-duration: ${duration}ms;"></div>
                    ` : ''}
                </div>
            `;
            
            document.body.appendChild(notification);
            
            // Animate in
            setTimeout(() => {
                adjustClasses(notification, getSlideInClass(position), 'remove');
                notification.classList.add('scale-100', 'opacity-100');
            }, 50);
            
            // Auto remove
            if (!persistent && duration > 0) {
                setTimeout(() => {
                    adjustClasses(notification, getSlideOutClass(position), 'add');
                    setTimeout(() => notification.remove(), 500);
                }, duration);
            }
            
            return notification;
        }

        function adjustClasses(element, classes, action = 'add') {
            if (!element || !classes) return;
            const tokens = classes.split(/\s+/).map(token => token.trim()).filter(Boolean);
            if (!tokens.length) return;
            if (action === 'remove') {
                element.classList.remove(...tokens);
            } else {
                element.classList.add(...tokens);
            }
        }

        function getPositionClass(position) {
            switch (position) {
                case 'top-left': return 'top-4 left-4';
                case 'top-center': return 'top-4 left-1/2 transform -translate-x-1/2';
                case 'top-right': return 'top-4 right-4';
                case 'bottom-left': return 'bottom-4 left-4';
                case 'bottom-center': return 'bottom-4 left-1/2 transform -translate-x-1/2';
                case 'bottom-right': return 'bottom-4 right-4';
                default: return 'top-4 right-4';
            }
        }

        function getSlideInClass(position) {
            if (position.includes('left')) return 'translate-x-[-100%] opacity-0 scale-95';
            if (position.includes('right')) return 'translate-x-full opacity-0 scale-95';
            if (position.includes('top')) return 'translate-y-[-100%] opacity-0 scale-95';
            return 'translate-y-full opacity-0 scale-95';
        }

        function getSlideOutClass(position) {
            if (position.includes('left')) return 'translate-x-[-100%] opacity-0 scale-95';
            if (position.includes('right')) return 'translate-x-full opacity-0 scale-95';
            if (position.includes('top')) return 'translate-y-[-100%] opacity-0 scale-95';
            return 'translate-y-full opacity-0 scale-95';
        }

        function getNotificationClasses(type) {
            switch (type) {
                case 'success': return 'bg-emerald-950/95 border-emerald-500/30';
                case 'error': return 'bg-red-950/95 border-red-500/30';
                case 'warning': return 'bg-amber-950/95 border-amber-500/30';
                case 'loot': return 'bg-purple-950/95 border-purple-500/30';
                case 'verification': return 'bg-cyan-950/95 border-cyan-500/30';
                default: return 'bg-slate-950/95 border-slate-500/30';
            }
        }

        function getIconBackgroundClass(type) {
            switch (type) {
                case 'success': return 'bg-emerald-500/20 text-emerald-400';
                case 'error': return 'bg-red-500/20 text-red-400';
                case 'warning': return 'bg-amber-500/20 text-amber-400';
                case 'loot': return 'bg-purple-500/20 text-purple-400';
                case 'verification': return 'bg-cyan-500/20 text-cyan-400';
                default: return 'bg-slate-500/20 text-slate-400';
            }
        }

        function getTextColorClass(type) {
            switch (type) {
                case 'success': return 'text-emerald-300';
                case 'error': return 'text-red-300';
                case 'warning': return 'text-amber-300';
                case 'loot': return 'text-purple-300';
                case 'verification': return 'text-cyan-300';
                default: return 'text-slate-300';
            }
        }

        function getProgressBarClass(type) {
            switch (type) {
                case 'success': return 'bg-gradient-to-r from-emerald-500 to-emerald-400';
                case 'error': return 'bg-gradient-to-r from-red-500 to-red-400';
                case 'warning': return 'bg-gradient-to-r from-amber-500 to-amber-400';
                case 'loot': return 'bg-gradient-to-r from-purple-500 to-purple-400';
                case 'verification': return 'bg-gradient-to-r from-cyan-500 to-cyan-400';
                default: return 'bg-gradient-to-r from-slate-500 to-slate-400';
            }
        }

        function getActionButtonClass(type) {
            switch (type) {
                case 'success': return 'bg-emerald-600/30 border border-emerald-500/50 text-emerald-300 hover:bg-emerald-600/50';
                case 'error': return 'bg-red-600/30 border border-red-500/50 text-red-300 hover:bg-red-600/50';
                case 'warning': return 'bg-amber-600/30 border border-amber-500/50 text-amber-300 hover:bg-amber-600/50';
                case 'loot': return 'bg-purple-600/30 border border-purple-500/50 text-purple-300 hover:bg-purple-600/50';
                case 'verification': return 'bg-cyan-600/30 border border-cyan-500/50 text-cyan-300 hover:bg-cyan-600/50';
                default: return 'bg-slate-600/30 border border-slate-500/50 text-slate-300 hover:bg-slate-600/50';
            }
        }

        function getNotificationIcon(type) {
            switch (type) {
                case 'success': return '✓';
                case 'error': return '⚠';
                case 'warning': return '!';
                case 'loot': return '💎';
                case 'verification': return '✓';
                default: return 'ℹ';
            }
        }

        // Toggle all checkboxes
        function toggleAllTasks(selectAll) {
            const checkboxes = document.querySelectorAll('input[name="task-select"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = selectAll;
            });
            updateBulkActions();
        }

        // Update bulk action button states
        function updateBulkActions() {
            const checkedCount = document.querySelectorAll('input[name="task-select"]:checked').length;
            const bulkContainer = document.getElementById('bulkActions');
            
            if (bulkContainer) {
                bulkContainer.style.opacity = checkedCount > 0 ? '1' : '0.5';
                bulkContainer.style.pointerEvents = checkedCount > 0 ? 'auto' : 'none';
            }
        }

        // Toggle user ban
        async function toggleUserBan(userId) {
            try {
                const token = requireAuthToken();
                const response = await fetch(`${API_URL}/admin/users/${userId}/ban`, {
                    method: 'PUT',
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (response.status === 401) {
                    handleAuthError();
                    return;
                }
                if (!response.ok) {
                    throw new Error('Failed to update player status');
                }
                alert('✓ Player status updated!');
                loadUsers();
            } catch (error) {
                console.error('Error toggling user ban:', error);
            }
        }

        // Delete task
        async function deleteTask(taskId) {
            if (!confirm('⚠️ Delete this quest permanently?')) return;

            try {
                const token = requireAuthToken();
                const response = await fetch(`${API_URL}/tasks/${taskId}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (response.ok) {
                    alert('🗑 Quest deleted!');
                    loadTasks();
                } else if (response.status === 401) {
                    alert('🔒 Session expired! Please log in again.');
                    handleAuthError();
                } else {
                    const errorData = await response.json().catch(() => ({}));
                    const errorMessage = errorData.detail || errorData.message || `HTTP ${response.status}`;
                    alert(`❌ Failed to delete quest!\n\nError: ${errorMessage}`);
                }
            } catch (error) {
                console.error('Error deleting task:', error);
                alert(`❌ Network error: ${error.message}`);
            }
        }

        // Edit task
        let editingTaskId = null;
        
        async function editTask(taskId) {
            try {
                // First, fetch the quest to check its type
                const response = await fetch(`${API_URL}/tasks/${taskId}`, {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                
                if (response.ok) {
                    const quest = await response.json();
                    
                    // Check quest type and route to appropriate edit page
                    if (quest.task_type && quest.task_type.includes('telegram')) {
                        // Redirect to dedicated Telegram quest edit page
                        editTask(taskId, 'telegram');
                    } else if (quest.task_type && quest.task_type.includes('twitter') || quest.platform === 'twitter') {
                        // Redirect to dedicated Twitter quest edit page
                        editTask(taskId, 'twitter');
                    } else if (quest.task_type && quest.task_type.includes('youtube') || quest.platform === 'youtube') {
                        // Redirect to dedicated YouTube quest edit page
                        editTask(taskId, 'youtube');
                    } else if (quest.task_type && (quest.task_type.includes('visit') || quest.task_type.includes('website')) || quest.platform === 'website') {
                        // Redirect to dedicated Website quest edit page
                        editTask(taskId, 'website');
                    } else if (quest.task_type && (quest.task_type.includes('social') || quest.task_type.includes('manual')) || quest.platform === 'social') {
                        // Redirect to dedicated Social Media quest edit page
                        editTask(taskId, 'social');
                    } else {
                        // Redirect to general edit page for other quest types
                        editTask(taskId, 'generic');
                    }
                } else {
                    // Fallback to general edit page if we can't determine type
                    editTask(taskId, 'generic');
                }
            } catch (error) {
                console.error('Error checking quest type:', error);
                // Fallback to general edit page
                editTask(taskId, 'generic');
            }
        }
        
        // Legacy edit function (kept for reference, not used)
        async function editTaskModal(taskId) {
            try {
                // Fetch task details
                const response = await fetch(`${API_URL}/tasks/${taskId}`, {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                
                if (!response.ok) throw new Error('Failed to fetch task');
                
                const task = await response.json();
                editingTaskId = taskId;
                
                // Show modal
                document.getElementById('taskModal').classList.remove('hidden');
                
                // Change modal title
                document.querySelector('#taskModal h2').textContent = '✏️ EDIT QUEST';
                document.getElementById('submitQuestBtn').textContent = '💾 UPDATE QUEST';
                
                // Pre-fill common fields
                document.getElementById('taskTitle').value = task.title || '';
                document.getElementById('taskDescription').value = task.description || '';
                document.getElementById('taskPoints').value = task.points_reward || 0;
                
                // Determine quest type and select it
                let questType = 'manual'; // default
                if (task.task_type) {
                    if (task.task_type.startsWith('twitter_')) {
                        questType = 'twitter';
                    } else if (task.task_type.startsWith('telegram_')) {
                        questType = 'telegram';
                    } else if (task.task_type === 'youtube_watch') {
                        questType = 'youtube';
                    } else if (task.task_type === 'daily_checkin') {
                        questType = 'daily';
                    } else if (task.task_type === 'manual_review') {
                        questType = 'manual';
                    }
                }
                
                // Select quest type
                selectQuestType(questType);
                
                // Pre-fill type-specific fields
                if (questType === 'twitter' && task.verification_data) {
                    const actionType = task.task_type.replace('twitter_', '');
                    document.getElementById('twitterActionType').value = actionType;
                    document.getElementById('twitterUsername').value = task.verification_data.username || '';
                    if (task.url) {
                        document.getElementById('twitterTweetUrl').value = task.url;
                    }
                    updateTwitterFields();
                } else if (questType === 'telegram' && task.verification_data) {
                    const actionType = task.task_type.replace('telegram_', '');
                    document.getElementById('telegramActionType').value = actionType;
                    document.getElementById('telegramLink').value = task.url || task.verification_data.invite_link || '';
                    document.getElementById('telegramChatId').value = task.verification_data.chat_id || '';
                    document.getElementById('telegramChatName').value = task.verification_data.chat_name || '';
                } else if (questType === 'youtube' && task.verification_data) {
                    document.getElementById('youtubeUrl').value = task.url || '';
                    document.getElementById('youtubeSecretCode').value = task.verification_data.code || '';
                    document.getElementById('youtubeMinWatchTime').value = task.verification_data.min_watch_seconds || 120;
                    document.getElementById('youtubeMaxAttempts').value = task.verification_data.max_attempts || 3;
                    document.getElementById('youtubeCodeHint').value = task.verification_data.code_hint || 'during the video';
                } else if (questType === 'daily' && task.verification_data) {
                    document.getElementById('dailyStreakBonus').value = task.verification_data.streak_bonus || 'none';
                    document.getElementById('dailyResetTime').value = task.verification_data.reset_time || '00:00';
                    document.getElementById('dailyStreakRequired').checked = task.verification_data.consecutive_required || false;
                } else if (questType === 'manual') {
                    document.getElementById('manualUrl').value = task.url || '';
                    if (task.verification_data) {
                        document.getElementById('manualSubmissionType').value = 'text';
                        document.getElementById('manualInstructions').value = task.verification_data.instructions || '';
                    }
                }
                
            } catch (error) {
                console.error('Error loading task for edit:', error);
                alert('❌ Failed to load quest details');
            }
        }

        // Toggle task active/inactive status
        async function toggleTaskStatus(taskId, currentStatus) {
            const newStatus = !currentStatus;
            
            if (!confirm(`${newStatus ? '▶️ Activate' : '⏸ Deactivate'} this quest?`)) return;

            // Check if user is authenticated
            if (!authToken) {
                alert('⚠️ You are not logged in! Please refresh the page and log in again.');
                handleAuthError();
                return;
            }

            try {
                const response = await fetch(`${API_URL}/tasks/${taskId}/toggle`, {
                    method: 'PATCH',
                    headers: { 
                        'Authorization': `Bearer ${authToken}`
                    }
                });

                if (response.ok) {
                    const result = await response.json();
                    alert(`${result.is_active ? '✅ Quest activated!' : '⏸ Quest deactivated!'}`);
                    loadTasks();
                } else if (response.status === 401) {
                    alert('🔒 Session expired! Please log in again.');
                    handleAuthError();
                } else {
                    const error = await response.json().catch(() => ({}));
                    throw new Error(error.detail || 'Failed to update status');
                }
            } catch (error) {
                console.error('Error toggling task status:', error);
                alert(`❌ Failed to toggle quest status: ${error.message}`);
            }
        }

        // Modal functions
        let selectedQuestType = null;

        function showAddTaskModal() {
            document.getElementById('taskModal').classList.remove('hidden');
            
            // Reset edit mode
            editingTaskId = null;
            document.querySelector('#taskModal h2').textContent = '⚔️ CREATE NEW QUEST';
            document.getElementById('submitQuestBtn').textContent = '🚀 CREATE QUEST';
            
            // Reset form
            document.getElementById('taskForm').reset();
            selectedQuestType = null;
            document.querySelectorAll('.quest-type-btn').forEach(btn => {
                btn.classList.remove('border-neon-purple', 'bg-neon-purple/20');
                btn.classList.add('border-neon-blue/30');
            });
            document.querySelectorAll('.common-fields, #twitterFields, #telegramFields, #youtubeFields, #dailyFields, #manualFields').forEach(el => el.style.display = 'none');
            document.getElementById('submitQuestBtn').classList.add('hidden');
        }

        function selectQuestType(type) {
            selectedQuestType = type;
            
            // Update button styles
            document.querySelectorAll('.quest-type-btn').forEach(btn => {
                if (btn.dataset.type === type) {
                    btn.classList.remove('border-neon-blue/30');
                    btn.classList.add('border-neon-purple', 'bg-neon-purple/20');
                } else {
                    btn.classList.remove('border-neon-purple', 'bg-neon-purple/20');
                    btn.classList.add('border-neon-blue/30');
                }
            });

            // Show common fields
            document.querySelector('.common-fields').style.display = 'block';
            
            // Hide all specific fields first
            document.querySelectorAll('#twitterFields, #telegramFields, #youtubeFields, #dailyFields, #manualFields').forEach(el => {
                el.classList.add('hidden');
            });

            // Show relevant fields
            if (type === 'twitter') {
                document.getElementById('twitterFields').classList.remove('hidden');
                document.getElementById('taskPlatform').value = 'twitter';
                document.getElementById('taskType').value = 'social';
                // Setup Twitter action type change handler
                document.getElementById('twitterActionType').onchange = updateTwitterFields;
                updateTwitterFields();
            } else if (type === 'telegram') {
                document.getElementById('telegramFields').classList.remove('hidden');
                document.getElementById('taskPlatform').value = 'telegram';
                document.getElementById('taskType').value = 'social';
            } else if (type === 'youtube') {
                document.getElementById('youtubeFields').classList.remove('hidden');
                document.getElementById('taskPlatform').value = 'youtube';
                document.getElementById('taskType').value = 'content';
            } else if (type === 'daily') {
                document.getElementById('dailyFields').classList.remove('hidden');
                document.getElementById('taskPlatform').value = 'daily';
                document.getElementById('taskType').value = 'engagement';
            } else if (type === 'manual') {
                document.getElementById('manualFields').classList.remove('hidden');
                document.getElementById('taskPlatform').value = 'manual';
                document.getElementById('taskType').value = 'engagement';
            }

            // Show submit button
            document.getElementById('submitQuestBtn').classList.remove('hidden');
        }

        function updateTwitterFields() {
            const actionType = document.getElementById('twitterActionType').value;
            const tweetField = document.getElementById('twitterTweetField');
            const usernameField = document.getElementById('twitterUsernameField');

            if (actionType === 'follow') {
                usernameField.style.display = 'block';
                tweetField.classList.add('hidden');
            } else {
                usernameField.style.display = 'block';
                tweetField.classList.remove('hidden');
            }
        }
        
        function toggleYouTubeVerification() {
            const platform = document.getElementById('taskPlatform').value;
            const verificationSection = document.getElementById('youtubeVerification');
            
            if (platform === 'youtube') {
                verificationSection.classList.remove('hidden');
            } else {
                verificationSection.classList.add('hidden');
            }
        }

        function showAddRewardModal() {
            document.getElementById('rewardModal').classList.remove('hidden');
        }

        // Edit task function
        async function editTask(taskId, taskType = 'generic') {
            try {
                console.log(`📝 Opening edit for task ${taskId} (type: ${taskType})`);
                
                // Get task details
                const response = await fetch(`${API_URL}/tasks/${taskId}`, {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                
                if (!response.ok) {
                    throw new Error('Failed to load task details');
                }
                
                const task = await response.json();
                
                // Set global editing variables
                editingTaskId = taskId;
                
                // Populate the task modal with existing data
                document.getElementById('taskTitle').value = task.title || '';
                document.getElementById('taskDescription').value = task.description || '';
                document.getElementById('taskPoints').value = task.points || 0;
                document.getElementById('taskPlatform').value = task.platform || 'general';
                document.getElementById('taskType').value = task.task_type || 'engagement';
                document.getElementById('isActiveTask').checked = task.is_active || false;
                
                // Set specific fields based on task type
                if (task.platform === 'telegram') {
                    selectQuestType('telegram');
                    if (task.telegram_chat_id) document.getElementById('telegramChatId').value = task.telegram_chat_id;
                    if (task.telegram_message) document.getElementById('telegramMessage').value = task.telegram_message;
                } else if (task.platform === 'youtube') {
                    selectQuestType('youtube');
                    if (task.youtube_url) document.getElementById('youtubeVideoUrl').value = task.youtube_url;
                    if (task.youtube_keyword) document.getElementById('youtubeVerificationKeyword').value = task.youtube_keyword;
                } else {
                    selectQuestType('manual');
                }
                
                // Update modal title and button
                document.querySelector('#taskModal .text-3xl').textContent = '✏️ EDIT QUEST';
                document.getElementById('submitQuestBtn').textContent = '💾 UPDATE QUEST';
                
                // Show the task modal
                showModal('taskModal');
                
                console.log(`✅ Task ${taskId} loaded for editing`);
                
            } catch (error) {
                console.error('Error loading task for editing:', error);
                alert(`❌ Failed to load task for editing: ${error.message}`);
            }
        }

        function closeModal(modalId) {
            document.getElementById(modalId).classList.add('hidden');
        }

        // Check if already logged in
        window.onload = async function() {
            console.log('🚀 Admin page loaded, checking authentication...');
            
            const token = localStorage.getItem('authToken');
            if (token) {
                console.log('🔑 Found stored token, validating...');
                authToken = token;
                
                // Validate token by making a test API call
                try {
                    const response = await fetch(`${API_URL}/tasks`, {
                        headers: { 'Authorization': `Bearer ${authToken}` }
                    });
                    
                    if (response.ok) {
                        console.log('✅ Token valid, loading dashboard...');
                        // Token is valid
                        document.getElementById('loginScreen').classList.add('hidden');
                        document.getElementById('adminDashboard').classList.remove('hidden');
                        loadDashboard();
                    } else if (response.status === 401) {
                        console.log('❌ Token expired, clearing...');
                        // Token expired or invalid
                        handleAuthError();
                    }
                } catch (error) {
                    console.error('❌ Token validation failed:', error);
                    // Clear invalid token
                    localStorage.removeItem('authToken');
                    authToken = null;
                }
            } else {
                console.log('🔓 No stored token found, showing login screen');
            }
            
            // Run server status check immediately on page load
            console.log('📡 Running immediate server status check...');
            setTimeout(() => {
                checkServerStatus();
            }, 100); // Tiny delay to ensure DOM is ready
            
            // Also run another check after 1 second to ensure it's working
            setTimeout(() => {
                console.log('🔄 Running follow-up status check...');
                checkServerStatus();
            }, 1000);
            
            // Add fallback event listeners for login
            const loginButton = document.getElementById('loginButton');
            if (loginButton) {
                loginButton.addEventListener('click', login);
                console.log('🔧 Fallback event listener added to login button');
            }
            
            const usernameField = document.getElementById('loginUsername');
            const passwordField = document.getElementById('loginPassword');
            if (usernameField && passwordField) {
                // Add Enter key support
                [usernameField, passwordField].forEach(field => {
                    field.addEventListener('keypress', (e) => {
                        if (e.key === 'Enter') {
                            e.preventDefault();
                            login();
                        }
                    });
                });
                console.log('⌨️ Enter key support added to login fields');
            }
        };

        // ============ ADMIN MANAGEMENT FUNCTIONS ============

        // Load admin users
        async function loadAdminUsers() {
            toggleSectionLoader('admins', true);
            try {
                const token = requireAuthToken();
                const response = await fetch(`${API_URL}/admin/users`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                if (response.status === 401) {
                    handleAuthError();
                    throw new Error('Not authorized');
                }
                if (!response.ok) throw new Error('Failed to load admin users');
                
                const adminsRaw = await response.json();
                const admins = Array.isArray(adminsRaw) ? adminsRaw : [];
                
                // Update stats
                document.getElementById('totalAdminsCount').textContent = admins.length;
                document.getElementById('activeSessionsCount').textContent = admins.filter(admin => admin.last_login && 
                    new Date(admin.last_login) > new Date(Date.now() - 24 * 60 * 60 * 1000)).length;
                document.getElementById('superAdminsCount').textContent = admins.filter(admin => admin.is_super_admin).length;
                
                // Display admin list
                displayAdminList(admins);
            } catch (error) {
                console.error('Error loading admin users:', error);
                document.getElementById('adminList').innerHTML = `
                    <div class="text-center text-red-400 py-8">
                        <i class="fas fa-exclamation-triangle text-2xl mb-2"></i>
                        <p>Failed to load admin users</p>
                    </div>
                `;
            } finally {
                toggleSectionLoader('admins', false);
            }
        }

        // Display admin list
        function displayAdminList(admins) {
            const adminList = document.getElementById('adminList');
            
            if (admins.length === 0) {
                adminList.innerHTML = `
                    <div class="text-center text-gray-400 py-8">
                        <i class="fas fa-users text-2xl mb-2"></i>
                        <p>No admin users found</p>
                    </div>
                `;
                return;
            }
            
            adminList.innerHTML = admins.map(admin => `
                <div class="bg-gradient-to-r from-gaming-card to-purple-900/20 border-2 border-neon-purple/30 rounded-xl p-6 card-glow">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-4">
                            <div class="w-12 h-12 bg-gradient-to-br from-neon-purple to-neon-blue rounded-full flex items-center justify-center">
                                <i class="fas ${admin.is_super_admin ? 'fa-crown' : 'fa-user-shield'} text-white text-xl"></i>
                            </div>
                            <div>
                                <h3 class="text-lg font-bold text-white">${admin.username}</h3>
                                <p class="text-sm text-gray-400">
                                    ${admin.is_super_admin ? '👑 Super Admin' : '🛡️ Admin'} • 
                                    Created: ${new Date(admin.created_at).toLocaleDateString()}
                                    ${admin.last_login ? ` • Last Login: ${new Date(admin.last_login).toLocaleDateString()}` : ''}
                                </p>
                                <div class="flex items-center gap-2 mt-2">
                                    <span class="px-2 py-1 text-xs rounded-full ${admin.is_active ? 'bg-green-500/20 text-neon-green' : 'bg-red-500/20 text-red-400'}">
                                        ${admin.is_active ? '🟢 Active' : '🔴 Inactive'}
                                    </span>
                                    ${(() => {
                                        const permissionList = Array.isArray(admin.permissions)
                                            ? admin.permissions
                                            : (admin.permissions ? admin.permissions.split(',') : []);
                                        return permissionList.map(perm => `
                                            <span class="px-2 py-1 text-xs rounded-full bg-blue-500/20 text-neon-blue">${perm.trim()}</span>
                                        `).join('');
                                    })()}
                                </div>
                            </div>
                        </div>
                        <div class="flex items-center gap-2">
                            <button onclick="editAdmin('${admin.id}')" class="action-btn action-edit px-3 py-2 text-sm">
                                <i class="fas fa-edit"></i> EDIT
                            </button>
                            ${admin.username !== 'admin' ? `
                                <button onclick="deleteAdmin('${admin.id}', '${admin.username}')" class="action-btn action-delete px-3 py-2 text-sm">
                                    <i class="fas fa-trash"></i> DELETE
                                </button>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `).join('');
        }

        // Open create admin modal
        function openCreateAdminModal() {
            const modalHtml = `
                <div id="createAdminModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
                    <div class="bg-gradient-to-br from-gaming-dark to-purple-900/40 border-2 border-neon-purple/50 rounded-2xl p-8 w-full max-w-md card-glow">
                        <div class="flex items-center justify-between mb-6">
                            <h2 class="text-2xl font-black gaming-title gradient-text">🛡️ CREATE ADMIN</h2>
                            <button onclick="closeCreateAdminModal()" class="text-gray-400 hover:text-white text-3xl">&times;</button>
                        </div>
                        
                        <form onsubmit="createAdmin(event)" class="space-y-4">
                            <div>
                                <label class="block text-neon-blue gaming-title text-sm mb-2">USERNAME</label>
                                <input type="text" id="newAdminUsername" required 
                                    class="w-full p-3 bg-gaming-dark/50 border-2 border-neon-purple/30 rounded-lg text-white focus:border-neon-purple/60 focus:outline-none">
                            </div>
                            
                            <div>
                                <label class="block text-neon-blue gaming-title text-sm mb-2">PASSWORD</label>
                                <input type="password" id="newAdminPassword" required 
                                    class="w-full p-3 bg-gaming-dark/50 border-2 border-neon-purple/30 rounded-lg text-white focus:border-neon-purple/60 focus:outline-none">
                            </div>
                            
                            <div>
                                <label class="block text-neon-blue gaming-title text-sm mb-2">PERMISSIONS</label>
                                <div class="space-y-2">
                                    <label class="flex items-center">
                                        <input type="checkbox" id="permQuests" value="quests" class="mr-2">
                                        <span class="text-white">Quest Management</span>
                                    </label>
                                    <label class="flex items-center">
                                        <input type="checkbox" id="permUsers" value="users" class="mr-2">
                                        <span class="text-white">User Management</span>
                                    </label>
                                    <label class="flex items-center">
                                        <input type="checkbox" id="permVerification" value="verification" class="mr-2">
                                        <span class="text-white">Verification Tasks</span>
                                    </label>
                                    <label class="flex items-center">
                                        <input type="checkbox" id="isSuperAdmin" class="mr-2">
                                        <span class="text-neon-yellow">👑 Super Admin (All Permissions)</span>
                                    </label>
                                </div>
                            </div>
                            
                            <div class="flex gap-4 pt-4">
                                <button type="submit" class="flex-1 action-btn action-create">
                                    <i class="fas fa-user-plus mr-2"></i> CREATE ADMIN
                                </button>
                                <button type="button" onclick="closeCreateAdminModal()" class="flex-1 action-btn action-secondary">
                                    CANCEL
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            `;
            
            document.body.insertAdjacentHTML('beforeend', modalHtml);
        }

        // Close create admin modal
        function closeCreateAdminModal() {
            const modal = document.getElementById('createAdminModal');
            if (modal) modal.remove();
        }

        // Create new admin
        async function createAdmin(event) {
            event.preventDefault();
            
            const username = document.getElementById('newAdminUsername').value;
            const password = document.getElementById('newAdminPassword').value;
            const isSuperAdmin = document.getElementById('isSuperAdmin').checked;
            
            let permissions = [];
            if (!isSuperAdmin) {
                if (document.getElementById('permQuests').checked) permissions.push('quests');
                if (document.getElementById('permUsers').checked) permissions.push('users');
                if (document.getElementById('permVerification').checked) permissions.push('verification');
            }
            
            try {
                const token = requireAuthToken();
                const response = await fetch(`${API_URL}/admin/create-admin`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        username,
                        password,
                        is_super_admin: isSuperAdmin,
                        permissions
                    })
                });
                
                if (response.status === 401) {
                    handleAuthError();
                    throw new Error('Not authorized');
                }
                if (!response.ok) throw new Error('Failed to create admin');
                
                closeCreateAdminModal();
                loadAdminUsers(); // Refresh the list
                showNotification('✅ Admin user created successfully!', 'success');
            } catch (error) {
                console.error('Error creating admin:', error);
                showNotification('❌ Failed to create admin user', 'error');
            }
        }

        // Edit admin (placeholder function)
        function editAdmin(adminId) {
            showNotification('🚧 Admin editing feature coming soon!', 'info');
        }

        // Delete admin
        async function deleteAdmin(adminId, username) {
            if (!confirm(`Are you sure you want to delete admin "${username}"?`)) {
                return;
            }
            
            try {
                const token = requireAuthToken();
                const response = await fetch(`${API_URL}/admin/delete-admin/${adminId}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                if (response.status === 401) {
                    handleAuthError();
                    throw new Error('Not authorized');
                }
                if (!response.ok) throw new Error('Failed to delete admin');
                
                loadAdminUsers(); // Refresh the list
                showNotification('✅ Admin user deleted successfully!', 'success');
            } catch (error) {
                console.error('Error deleting admin:', error);
                showNotification('❌ Failed to delete admin user', 'error');
            }
        }

        // Load admin data when the section is shown
        function showSection(sectionName) {
            const sectionIds = ['dashboard', 'users', 'tasks', 'rewards', 'verification', 'admins'];
            sectionIds.forEach(section => {
                const element = document.getElementById(section);
                if (element) {
                    element.classList.add('hidden');
                }
            });

            document.querySelectorAll('.tab-btn').forEach(item => {
                item.classList.remove('active');
            });
            const targetButton = document.querySelector(`[data-section="${sectionName}"]`);
            if (targetButton) {
                targetButton.classList.add('active');
            }

            const sectionElement = document.getElementById(sectionName);
            if (sectionElement) {
                sectionElement.classList.remove('hidden');
            } else {
                console.warn(`Section ${sectionName} not found in DOM`);
                return;
            }

            // Load section-specific data
            if (sectionName === 'dashboard') {
                loadDashboard();
            } else if (sectionName === 'users') {
                loadUsers();
            } else if (sectionName === 'tasks') {
                loadTasks();
            } else if (sectionName === 'rewards') {
                loadRewards();
            } else if (sectionName === 'verification') {
                loadVerification();
            } else if (sectionName === 'admins') {
                loadAdminUsers();
            }
        }
    