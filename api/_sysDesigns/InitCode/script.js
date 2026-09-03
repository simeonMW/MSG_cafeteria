document.addEventListener("DOMContentLoaded", () => {
    // --- Settings Modal & Theme Logic ---
    const settingsBtn = document.getElementById("settingsBtn");
    const settingsModal = document.getElementById("settingsModal");
    const closeBtns = document.querySelectorAll(".close-btn");
    const themeSelector = document.getElementById("themeSelector");

    // Load saved theme
    const savedTheme = localStorage.getItem("theme") || "light";
    document.documentElement.setAttribute("data-theme", savedTheme);
    if(themeSelector) themeSelector.value = savedTheme;

    if (settingsBtn) {
        settingsBtn.onclick = () => settingsModal.style.display = "block";
    }

    if (themeSelector) {
        themeSelector.addEventListener("change", (e) => {
            const theme = e.target.value;
            document.documentElement.setAttribute("data-theme", theme);
            localStorage.setItem("theme", theme);
        });
    }

    // Modal Close Logic
    closeBtns.forEach(btn => {
        btn.onclick = function() {
            this.closest('.modal').style.display = "none";
        }
    });

    // --- Analytics Day View Toggle ---
    const dayViewToggle = document.getElementById("dayViewToggle");
    const daySelector = document.getElementById("daySelector");

    if (dayViewToggle && daySelector) {
        dayViewToggle.addEventListener("change", (e) => {
            if (e.target.checked) {
                daySelector.classList.remove("hidden");
                updateCharts('hourly'); // Mock function to update charts
            } else {
                daySelector.classList.add("hidden");
                updateCharts('daily');
            }
        });
    }

    // --- Analytics Charts (Chart.js) ---
    const ratioCtx = document.getElementById('ratioChart');
    const ordersCtx = document.getElementById('ordersChart');

    if (ratioCtx) {
        new Chart(ratioCtx, {
            type: 'doughnut',
            data: {
                labels: ['Ordered', 'No Orders'],
                datasets: [{
                    data: [65, 35],
                    backgroundColor: ['#007BFF', '#E0E0E0']
                }]
            }
        });
    }

    if (ordersCtx) {
        new Chart(ordersCtx, {
            type: 'bar',
            data: {
                labels: ['1', '2', '3', '4', '5'],
                datasets: [{
                    label: 'Orders',
                    data: [12, 19, 3, 5, 2],
                    backgroundColor: '#6F42C1'
                }]
            }
        });
    }

    // --- Order Initiate Payment Modal ---
    const initiatePaymentBtn = document.getElementById("initiatePaymentBtn");
    const paymentModal = document.getElementById("paymentModal");

    if (initiatePaymentBtn) {
        initiatePaymentBtn.onclick = () => paymentModal.style.display = "block";
    }
});