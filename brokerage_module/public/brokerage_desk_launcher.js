// Brokerage Desk Launcher for Frappe / ERPNext Desk (/app)
frappe.provide('brokerage_module');

$(document).on('toolbar_setup', function() {
    brokerage_module.add_brokerage_desk_button();
});

$(document).ready(function() {
    brokerage_module.add_brokerage_desk_button();
});

brokerage_module.add_brokerage_desk_button = function() {
    if ($('#navbar-brokerage-desk-btn').length) return;

    const btnHtml = `
        <li class="nav-item dropdown dropdown-notifications dropdown-mobile" id="navbar-brokerage-desk-btn" style="margin-right: 8px;">
            <a class="nav-link btn btn-sm" href="/brokerage-desk" style="background: #1e3a8a; color: #ffffff; font-weight: 600; font-size: 12px; padding: 5px 12px; border-radius: 6px; display: inline-flex; align-items: center; gap: 6px; text-decoration: none; border: 1px solid #3b82f6; box-shadow: 0 1px 3px rgba(0,0,0,0.15);">
                <span>💼</span>
                <span>Brokerage Desk</span>
            </a>
        </li>
    `;

    if ($('.navbar .navbar-nav:last').length) {
        $('.navbar .navbar-nav:last').prepend(btnHtml);
    } else if ($('.navbar-collapse').length) {
        $('.navbar-collapse').append(btnHtml);
    }
};

// Global Keyboard Shortcut inside ERPNext Desk: Alt+B -> Open Brokerage Desk
$(document).on('keydown', function(e) {
    if (e.altKey && (e.key === 'b' || e.key === 'B')) {
        if (!['input', 'textarea', 'select'].includes(document.activeElement.tagName.toLowerCase())) {
            e.preventDefault();
            window.location.href = '/brokerage-desk';
        }
    }
});
