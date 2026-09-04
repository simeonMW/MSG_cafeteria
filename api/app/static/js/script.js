/* window.addEventListener('resize', ()=>{
    console.log(window.screen.width);
    if ( window.screen.width >  920 ) {
            sidebarExit.style.display = "none";
            sidebarMenu.style.display = "none";
            navLinks.style.display = "flex";
            sidebarBottom.style.display = "flex";
    }
}) */

function showAuthAlert(message, isError = true) {
    const alertBox = document.getElementById('authAlert');
    if (!alertBox) return;
    alertBox.textContent = message;
    alertBox.classList.remove('hidden');
    alertBox.classList.toggle('error', isError);
}

document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);

    const themeSelector = document.getElementById('themeSelector');
    if (themeSelector) {
        themeSelector.value = savedTheme;
        themeSelector.addEventListener('change', (event) => {
            const nextTheme = event.target.value;
            document.documentElement.setAttribute('data-theme', nextTheme);
            localStorage.setItem('theme', nextTheme);
        });
    }

    const settingsBtn = document.getElementById('settingsBtn');
    const settingsModal = document.getElementById('settingsModal');
    if (settingsBtn && settingsModal) {
        settingsBtn.addEventListener('click', () => settingsModal.style.display = 'block');
    }

    document.querySelectorAll('.close-btn').forEach((button) => {
        button.addEventListener('click', () => {
            const modal = button.closest('.modal');
            if (modal) modal.style.display = 'none';
        });
    });

    window.addEventListener('click', (event) => {
        if (event.target && event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });

    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', (event) => {
            const spinner = document.getElementById('loginSpinner');
            if (spinner) spinner.classList.remove('hidden');
        });
    }

    const donutChart = document.getElementById('donutChart');
    if (donutChart) {
        const value = Number(donutChart.dataset.value);
        const remainder = 100 - value;
        donutChart.style.background = `conic-gradient(var(--accent) 0 ${value}%, #dfe7f1 ${value}% ${value + remainder}%)`;
    }

    const barChart = document.getElementById('barChart');
    if (barChart) {
        const orders_number_series = JSON.parse(barChart.dataset.series);
        //console.log(orders_number_series);
        const max_orders_number = Math.max(...orders_number_series);
        let count = 0;
        barChart.innerHTML = orders_number_series.map((orders_number) => {
            const height = (orders_number / max_orders_number) * 100;
            if ( count === 0) {
                count += 1;
                return `
                    <div class="bar-item">
                        <div class="bar" style="height:100%; background: transparent; " ></div>
                        <span style="transform: translate(-14px,-35px) rotate(-90deg);"> orders </span>
                        <span class="text-muted" style="transform: translate(-5px, 8px ); overflow-x: visible; padding-bottom: 10px;">day</span>
                    </div>
                `;
            }
            count += 1;
            return `
                <div class="bar-item">
                    <span> ${orders_number} </span>
                    <div class="bar" style="height:${height}%;"></div>
                    <span class="text-muted">${count - 1}</span>
                </div>
            `;
        }).join('');
    }

    /* async function set_month(monthizzo) {
        console.log(monthizzo);
        try {
            const respoC = await fetch(
                "{{ url_for(dashboard.month) }}",
                {
                    method: "POST",
                    headers : {
                        "Content-Type": "applicatio/json"
                    },
                    body: JSON.stringify({ month: monthizzo})
                }
            );
            //response = await respoC.json();
        } catch (error) {
            console.log("error updating active month")
        }
    } */


    function filterRows(selector, filterValue) {
        const rows = document.querySelectorAll(selector);
        rows.forEach((row) => {
            const rawText = row.textContent.toLowerCase();
            row.style.display = rawText.includes(filterValue.toLowerCase()) ? '' : 'none';
        });
    }

    const paymentSearch = document.getElementById('paymentSearchInput');
    if (paymentSearch) {
        paymentSearch.addEventListener('input', (event) => {
            filterRows('#paymentsTableBody tr', event.target.value);
        });
    }

    const userSearch = document.getElementById('userSearchInput');
    if (userSearch) {
        userSearch.addEventListener('input', (event) => {
            filterRows('#userTableBody tr', event.target.value);
        });
    }

    const orderSearch = document.getElementById('orderSearchInput');
    if (orderSearch) {
        orderSearch.addEventListener('input', (event) => {
            filterRows('#orderTableBody tr', event.target.value);
        });
    }

    const paymentStatusFilter = document.getElementById('paymentStatusFilter');
    if (paymentStatusFilter) {
        paymentStatusFilter.addEventListener('change', (event) => {
            const value = event.target.value;
            document.querySelectorAll('#paymentsTableBody tr').forEach((row) => {
                const status = row.dataset.status || '';
                const matches = value === 'all' || status.toLowerCase() === value.toLowerCase();
                row.style.display = matches ? '' : 'none';
            });
        });
    }

    const initiatePaymentBtn = document.getElementById('initiatePaymentBtn');
    const paymentModal = document.getElementById('paymentModal');
    if (initiatePaymentBtn && paymentModal) {
        initiatePaymentBtn.addEventListener('click', () => {
            paymentModal.style.display = 'block';
        });
    }
});

window.handleLoginSubmit = function () {
    const form = document.getElementById('loginForm');
    if (!form) return;
    form.submit();
};

window.toggleLoginPassword = function () {
    toggleLoginPassword();
};

/* window.set_month = async function (monthizzo) {
    console.log(monthizzo);
    try {
        const respoC = await fetch(
            "{{ url_for(dashboard.month) }}",
            {
                method: "POST",
                headers : {
                    "Content-Type": "applicatio/json"
                },
                body: JSON.stringify({ month: monthizzo})
            }
        );
        //response = await respoC.json();
    } catch (error) {
        console.log("error updating active month")
    }
} */

window.filterPaymentsTable = function () {
    const input = document.getElementById('paymentSearchInput');
    const statusFilter = document.getElementById('paymentStatusFilter');
    const rows = document.querySelectorAll('#paymentsTableBody tr');
    rows.forEach((row) => {
        const text = row.textContent.toLowerCase();
        const status = row.dataset.status || '';
        const searchMatch = !input || text.includes(input.value.toLowerCase());
        const statusMatch = !statusFilter || statusFilter.value === 'all' || status.toLowerCase() === statusFilter.value.toLowerCase();
        row.style.display = searchMatch && statusMatch ? '' : 'none';
    });
};
window.filterOrdersTable = function () {
    const input = document.getElementById('orderSearchInput');
    const statusFilter = document.getElementById('orderStatusFilter');
    const rows = document.querySelectorAll('#ordersTableBody tr');
    rows.forEach((row) => {
        const text = row.textContent.toLowerCase();
        const status = row.dataset.status || '';
        const paid = row.dataset.paid || '';
        const searchMatch = !input || text.includes(input.value.toLowerCase());
        const statusMatch = !statusFilter || statusFilter.value === 'all' || status.toLowerCase() === statusFilter.value.toLowerCase() || paid.toLowerCase() === statusFilter.value.toLowerCase();
        row.style.display = searchMatch && statusMatch ? '' : 'none';
    }); 
}

window.filterUserTable = function () {
    const input = document.getElementById('userSearchInput');
    const rows = document.querySelectorAll('#userTableBody tr');
    rows.forEach((row) => {
        const text = row.textContent.toLowerCase();
        const show = !input || text.includes(input.value.toLowerCase());
        row.style.display = show ? '' : 'none';
    });
};

window.toggleUserVerification = function (userId, checked) {
    if (window.confirm(`Update verification for user ${userId}?`)) {
        console.log('Verification toggle', userId, checked);
    }
};

window.currentPaymentId = null;

window.openPaymentDetailModal = function (payId) {
    const modal = document.getElementById('paymentDetailModal');
    if (!modal) return;
    window.currentPaymentId = payId;
    modal.style.display = 'block';

    fetch(`/admin/api/payments/${payId}`)
        .then((response) => response.json())
        .then((payload) => {
            if (!payload || payload.status !== 'success' || !payload.payment) return;
            const payment = payload.payment;
            const periodText = payment.period_label || payment.period || 'N/A';
            const statusBadge = document.getElementById('modalStatusBadge');
            const rowsBody = document.getElementById('modalOrdersTableBody');
            document.getElementById('modalPeriod').textContent = periodText;
            document.getElementById('modalTimestamp').textContent = payment.created_at || 'N/A';
            document.getElementById('modalPayId').textContent = `PAY-${payment.id}`;
            document.getElementById('modalTotalAmount').textContent = `MK ${Number(payment.amount || 0).toFixed(2)}`;
            statusBadge.textContent = payment.status;
            statusBadge.className = `badge badge-${String(payment.status || 'unpaid').toLowerCase()}`;

            rowsBody.innerHTML = (payment.orders || []).map((row) => `
                <tr>
                    <td class="font-mono">${row.order_id}</td>
                    <td>${row.customer}</td>
                    <td>${row.item}</td>
                    <td>${row.date}</td>
                    <td class="text-right">MK ${Number(row.amount || 0).toFixed(2)}</td>
                </tr>
            `).join('') || '<tr><td colspan="6" class="empty-table-msg">No orders linked to this payment.</td></tr>';
        })
        .catch(() => {
            const rowsBody = document.getElementById('modalOrdersTableBody');
            if (rowsBody) rowsBody.innerHTML = '<tr><td colspan="6" class="empty-table-msg">Unable to load payment details.</td></tr>';
        });
};

window.closePaymentDetailModal = function () {
    const modal = document.getElementById('paymentDetailModal');
    if (modal) modal.style.display = 'none';
};

window.downloadPaymentRecord = function (payId, format = 'pdf') {
    let format_selection = document.querySelector('#exportSelector');
    let format_stored = localStorage.getItem('export_formart');
    if (format_stored || format_selection.value) {
        console.log(format_selection.value);
        format = format_stored ? format_stored : format_selection.value;
    }
    if (!payId) return;
    const url = `/admin/api/payments/${payId}/download?format=${format}`;
    const link = document.createElement('a');
    link.href = url;
    link.target = '_blank';
    link.rel = 'noopener';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};

window.downloadPaymentRecordFromModal = function () {
    if (!window.currentPaymentId) return;
    window.downloadPaymentRecord(window.currentPaymentId, 'pdf');
};

window.sharePaymentReport = function () {
    if (!window.currentPaymentId) return;
    fetch(`/admin/api/payments/${window.currentPaymentId}/share?format=pdf`)
        .then((response) => response.json())
        .then((payload) => {
            if (!payload || !payload.share_url) return;
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(payload.share_url).catch(() => {});
            }
            window.alert(`Payment document link ready for forwarding:\n${payload.share_url}`);
        })
        .catch(() => {
            window.alert('Unable to generate a shareable payment link.');
        });
};

window.markPaymentAsPaid = function () {
    if (!window.currentPaymentId) return;
    fetch(`/admin/api/payments/${window.currentPaymentId}/mark-paid`, { method: 'POST' })
        .then((response) => response.json())
        .then((payload) => {
            if (!payload || payload.status !== 'success') return;
            const badge = document.getElementById('modalStatusBadge');
            if (badge) {
                badge.textContent = 'paid';
                badge.className = 'badge badge-paid';
            }
            const row = document.querySelector(`#paymentsTableBody tr[data-pay-id="${window.currentPaymentId}"]`);
            if (row) {
                row.setAttribute('data-status', 'paid');
                const statusCell = row.querySelector('.badge');
                if (statusCell) statusCell.textContent = 'paid';
            }
            window.alert('Payment marked as paid.');
        })
        .catch(() => {
            window.alert('Unable to update payment status.');
        });
};