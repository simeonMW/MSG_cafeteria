/**
 * MSG Cafe Admin Dashboard - Core Application Engine
 * Handles Navigation, Theme System, Modals, Dynamic Charts, Data Tables, and Auth Flow.
 */

document.addEventListener("DOMContentLoaded", () => {
    // Initialize Theme & Settings Modules
    initThemeAndSettings();
    
    // Initialize Page-Specific Handlers based on DOM presence
    if (document.getElementById('ratioChart')) initAnalyticsPage();
    if (document.getElementById('userSearchInput')) initUserManagementPage();
    if (document.getElementById('initiatePaymentBtn')) initOrdersPage();
    if (document.getElementById('paymentsTable')) initPaymentsPage();
    if (document.getElementById('row-name')) initProfilePage();
    if (document.getElementById('loginForm')) initAuthFlow();
    if (document.getElementById('twofaForm')) init2FAFlow();
});

/* ==========================================================================
   1. Global Theme & Settings Modal Manager
   ========================================================================== */
function initThemeAndSettings() {
    const settingsBtn = document.getElementById("settingsBtn");
    const settingsModal = document.getElementById("settingsModal");
    const themeSelector = document.getElementById("themeSelector");
    const exportSelector = document.getElementById("exportSelector");

    // Load persisted theme preference
    const savedTheme = localStorage.getItem("theme") || "light";
    document.documentElement.setAttribute("data-theme", savedTheme);
    if (themeSelector) themeSelector.value = savedTheme;

    // Load persisted document export type preference
    const savedExport = localStorage.getItem("exportFormat") || "pdf";
    if (exportSelector) exportSelector.value = savedExport;

    // Settings Modal Toggle
    if (settingsBtn && settingsModal) {
        settingsBtn.addEventListener("click", () => {
            settingsModal.style.display = "flex";
        });
    }

    // Theme Switch Event Listener
    if (themeSelector) {
        themeSelector.addEventListener("change", (e) => {
            const theme = e.target.value;
            document.documentElement.setAttribute("data-theme", theme);
            localStorage.setItem("theme", theme);
        });
    }

    // Export Preference Listener
    if (exportSelector) {
        exportSelector.addEventListener("change", (e) => {
            localStorage.setItem("exportFormat", e.target.value);
        });
    }

    // Modal Global Close Handlers
    document.querySelectorAll(".close-btn, .modal-close-icon").forEach(btn => {
        btn.addEventListener("click", function() {
            const modal = this.closest(".modal");
            if (modal) modal.style.display = "none";
        });
    });

    window.addEventListener("click", (e) => {
        if (e.target.classList.contains("modal")) {
            e.target.style.display = "none";
        }
    });
}

/* ==========================================================================
   2. Analytics Page & Chart.js Integration
   ========================================================================== */
let ratioChartInstance = null;
let ordersChartInstance = null;

function initAnalyticsPage() {
    const dayViewToggle = document.getElementById("dayViewToggle");
    const daySelector = document.getElementById("daySelector");

    // Render Doughnut Chart (User order ratio)
    const ratioCtx = document.getElementById('ratioChart').getContext('2d');
    ratioChartInstance = new Chart(ratioCtx, {
        type: 'doughnut',
        data: {
            labels: ['Placed Orders', 'No Orders'],
            datasets: [{
                data: [68, 32],
                backgroundColor: ['#28a745', '#e3e6ea'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'bottom' } }
        }
    });

    // Render Bar Chart (Total Orders)
    const ordersCtx = document.getElementById('ordersChart').getContext('2d');
    ordersChartInstance = new Chart(ordersCtx, {
        type: 'bar',
        data: {
            labels: ['1', '5', '10', '15', '20', '25', '30'],
            datasets: [{
                label: 'Total Orders',
                data: [45, 88, 120, 65, 140, 95, 110],
                backgroundColor: '#6f42c1',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
    });

    // Toggle switch logic to activate/deactivate Day Selector and update Bar chart
    if (dayViewToggle && daySelector) {
        dayViewToggle.addEventListener("change", (e) => {
            if (e.target.checked) {
                daySelector.classList.remove("hidden");
                // Update chart for Hourly View
                ordersChartInstance.data.labels = ['8 AM', '10 AM', '12 PM', '2 PM', '4 PM', '6 PM', '8 PM'];
                ordersChartInstance.data.datasets[0].data = [12, 35, 62, 40, 28, 55, 30];
                ordersChartInstance.update();
            } else {
                daySelector.classList.add("hidden");
                // Reset chart to Monthly Day View
                ordersChartInstance.data.labels = ['1', '5', '10', '15', '20', '25', '30'];
                ordersChartInstance.data.datasets[0].data = [45, 88, 120, 65, 140, 95, 110];
                ordersChartInstance.update();
            }
        });
    }
}

/* ==========================================================================
   3. User Management Module
   ========================================================================== */
function initUserManagementPage() {
    window.filterUserTable = function() {
        const searchInput = document.getElementById('userSearchInput').value.toLowerCase().trim();
        const statusFilter = document.getElementById('statusFilter').value;
        const rows = document.querySelectorAll('#userTableBody tr:not(#noResultsRow)');

        rows.forEach(row => {
            const textContent = row.innerText.toLowerCase();
            const isVerified = row.getAttribute('data-verified') === 'true';

            const matchesSearch = textContent.includes(searchInput);
            let matchesStatus = true;
            if (statusFilter === 'verified') matchesStatus = isVerified;
            if (statusFilter === 'unverified') matchesStatus = !isVerified;

            row.style.display = (matchesSearch && matchesStatus) ? '' : 'none';
        });
    };

    window.toggleUserVerification = async function(userId, isChecked) {
        try {
            const res = await fetch(`/api/users/${userId}/toggle-verify`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ verified: isChecked })
            });
            const data = await res.json();
            if (data.success) {
                const row = document.querySelector(`tr[data-user-id="${userId}"]`);
                if (row) row.setAttribute('data-verified', isChecked ? 'true' : 'false');
            } else {
                alert('Verification update failed.');
            }
        } catch (err) {
            console.error('Error:', err);
        }
    };
}

/* ==========================================================================
   4. Orders & Batch Payment Workflow
   ========================================================================== */
function initOrdersPage() {
    const initiateBtn = document.getElementById("initiatePaymentBtn");
    const paymentModal = document.getElementById("paymentModal");
    const closeBtn = document.getElementById("closePaymentModal");

    if (initiateBtn && paymentModal) {
        initiateBtn.addEventListener("click", () => {
            paymentModal.style.display = "flex";
        });
    }

    if (closeBtn && paymentModal) {
        closeBtn.addEventListener("click", () => {
            paymentModal.style.display = "none";
        });
    }
}

/* ==========================================================================
   5. Payments & Detailed Transaction Modal
   ========================================================================== */
function initPaymentsPage() {
    window.filterPaymentsTable = function() {
        const searchInput = document.getElementById('paymentSearchInput').value.toLowerCase().trim();
        const statusFilter = document.getElementById('paymentStatusFilter').value;
        const rows = document.querySelectorAll('#paymentsTableBody tr:not(#noPaymentsRow)');

        rows.forEach(row => {
            const textContent = row.innerText.toLowerCase();
            const rowStatus = row.getAttribute('data-status');

            const matchesSearch = textContent.includes(searchInput);
            const matchesStatus = (statusFilter === 'all') || (rowStatus === statusFilter);

            row.style.display = (matchesSearch && matchesStatus) ? '' : 'none';
        });
    };

    window.openPaymentDetailModal = async function(paymentId) {
        const modal = document.getElementById('paymentDetailModal');
        const tbody = document.getElementById('modalOrdersTableBody');
        if (!modal || !tbody) return;

        tbody.innerHTML = `<tr><td colspan="6" class="text-center">Loading details...</td></tr>`;
        modal.style.display = 'flex';

        try {
            const res = await fetch(`/api/payments/${paymentId}`);
            const data = await res.json();

            if (data.success) {
                const pay = data.payment;
                document.getElementById('modalPayId').innerText = pay.id;
                document.getElementById('modalPeriod').innerText = pay.reporting_period || '2026-08-01 to 2026-08-31';
                document.getElementById('modalTimestamp').innerText = pay.generated_at || '2026-08-24 09:12:00 UTC';
                document.getElementById('modalTotalAmount').innerText = `$${pay.amount.toFixed(2)}`;

                tbody.innerHTML = '';
                if (pay.orders && pay.orders.length > 0) {
                    pay.orders.forEach(ord => {
                        tbody.innerHTML += `
                            <tr>
                                <td class="font-mono text-bold">${ord.id}</td>
                                <td>${ord.customer}</td>
                                <td>${ord.item}</td>
                                <td class="text-center">${ord.qty}</td>
                                <td class="text-muted">${ord.date}</td>
                                <td class="text-right text-bold">$${ord.amount.toFixed(2)}</td>
                            </tr>`;
                    });
                }
            }
        } catch (err) {
            console.error('Failed to load payment detail:', err);
        }
    };

    window.closePaymentDetailModal = function() {
        const modal = document.getElementById('paymentDetailModal');
        if (modal) modal.style.display = 'none';
    };

    window.downloadPaymentRecordFromModal = function() {
        const format = localStorage.getItem('exportFormat') || 'pdf';
        alert(`Downloading record as ${format.toUpperCase()}...`);
    };
}

/* ==========================================================================
   6. Profile Management Module
   ========================================================================== */
function initProfilePage() {
    window.enableInlineEdit = function(fieldKey) {
        const row = document.getElementById(`row-${fieldKey}`);
        if (!row) return;

        row.querySelector(`#display-${fieldKey}`).classList.add('hidden');
        row.querySelector('.edit-btn').classList.add('hidden');
        row.querySelector(`#input-${fieldKey}`).classList.remove('hidden');
        row.querySelector(`#controls-${fieldKey}`).classList.remove('hidden');
    };

    window.cancelInlineEdit = function(fieldKey) {
        const row = document.getElementById(`row-${fieldKey}`);
        if (!row) return;

        row.querySelector(`#input-${fieldKey}`).classList.add('hidden');
        row.querySelector(`#controls-${fieldKey}`).classList.add('hidden');
        row.querySelector(`#display-${fieldKey}`).classList.remove('hidden');
        row.querySelector('.edit-btn').classList.remove('hidden');
    };

    window.saveInlineEdit = async function(fieldKey) {
        const input = document.getElementById(`input-${fieldKey}`);
        const newValue = input.value.trim();

        try {
            const res = await fetch('/api/profile/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ field: fieldKey, value: newValue })
            });

            const data = await res.json();
            if (data.success) {
                document.getElementById(`display-${fieldKey}`).innerText = fieldKey === 'password' ? '••••••••••••' : newValue;
                cancelInlineEdit(fieldKey);
            }
        } catch (err) {
            console.error('Save failed:', err);
        }
    };

    window.togglePasswordDisplay = function(fieldKey) {
        const span = document.getElementById(`display-${fieldKey}`);
        const btn = document.getElementById('toggle-pwd-btn');
        if (span.innerText === '••••••••••••') {
            span.innerText = 'password123';
            if (btn) btn.innerText = '🙈';
        } else {
            span.innerText = '••••••••••••';
            if (btn) btn.innerText = '👁️';
        }
    };
}

/* ==========================================================================
   7. Authentication & 2FA Handler
   ========================================================================== */
function initAuthFlow() {
    window.toggleLoginPassword = function() {
        const input = document.getElementById('password');
        const btn = document.querySelector('.pwd-toggle-btn');
        if (input.type === 'password') {
            input.type = 'text';
            btn.innerText = '🙈';
        } else {
            input.type = 'password';
            btn.innerText = '👁️';
        }
    };

    window.handleLoginSubmit = async function(e) {
        e.preventDefault();
        const alertBox = document.getElementById('authAlert');
        const empId = document.getElementById('employee_id').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;

        try {
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ employee_id: empId, email: email, password: password })
            });
            const data = await res.json();

            if (data.success) {
                window.location.href = data.redirect;
            } else {
                alertBox.innerText = data.message || 'Login failed.';
                alertBox.className = 'auth-alert alert-danger';
                alertBox.classList.remove('hidden');
            }
        } catch (err) {
            console.error('Login error:', err);
        }
    };
}

function init2FAFlow() {
    const otpInputs = document.querySelectorAll('.otp-digit');
    otpInputs.forEach((input, index) => {
        input.addEventListener('input', (e) => {
            if (e.target.value.length === 1 && index < otpInputs.length - 1) {
                otpInputs[index + 1].focus();
            }
        });

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && !e.target.value && index > 0) {
                otpInputs[index - 1].focus();
            }
        });
    });

    window.handle2FASubmit = async function(e) {
        e.preventDefault();
        let fullCode = '';
        document.querySelectorAll('.otp-digit').forEach(i => fullCode += i.value);

        try {
            const res = await fetch('/api/verify-2fa', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: fullCode })
            });
            const data = await res.json();

            if (data.success) {
                window.location.href = data.redirect;
            } else {
                const alertBox = document.getElementById('twofaAlert');
                alertBox.innerText = data.message || 'Verification code invalid.';
                alertBox.className = 'auth-alert alert-danger';
                alertBox.classList.remove('hidden');
            }
        } catch (err) {
            console.error('2FA error:', err);
        }
    };
}