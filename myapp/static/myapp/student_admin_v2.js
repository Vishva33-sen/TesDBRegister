document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ student_admin.js loaded");
    console.log("📍 Current URL:", window.location.href);

    // Select dropdowns from the Student admin form
    const courseSelect = document.querySelector("#id_course");
    const staffSelect = document.querySelector("#id_staff");
    const batchSelect = document.querySelector("#id_batch");

    if (!courseSelect || !staffSelect || !batchSelect) {
        console.warn("⚠️ One or more select fields not found in StudentAdmin form.");
        return;
    }

    // --- Helper: get CSRF token ---
    function getCSRFToken() {
        const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        return tokenElement ? tokenElement.value : '';
    }

    // --- Helper: clear dropdown options ---
    function clearOptions(selectElem, placeholder = "---------") {
        selectElem.innerHTML = "";
        const opt = document.createElement("option");
        opt.value = "";
        opt.textContent = placeholder;
        selectElem.appendChild(opt);
    }

    // --- Helper: populate dropdown options ---
    function populateOptions(selectElem, items) {
        // Clear existing options
        selectElem.innerHTML = "";
        
        // Add placeholder first
        const placeholder = document.createElement("option");
        placeholder.value = "";
        placeholder.textContent = "---------";
        selectElem.appendChild(placeholder);
        
        // Add actual items
        console.log("📝 Adding options:", items);
        items.forEach(item => {
            const opt = document.createElement("option");
            opt.value = item.id;
            opt.textContent = item.name;
            selectElem.appendChild(opt);
            console.log("  ✓ Added:", item.name);
        });
        
        console.log("📊 Total options now:", selectElem.options.length);
    }

    // --- When Course changes → fetch staff list ---
    courseSelect.addEventListener("change", function () {
        const courseId = this.value;
        console.log("📘 Course changed:", courseId);

        clearOptions(staffSelect, "---------");
        clearOptions(batchSelect, "---------");

        if (!courseId) return;

        // Get the current page URL and construct the correct path
        const currentUrl = window.location.pathname;
        console.log("📍 Current path:", currentUrl);
        
        // Build URL based on whether we're on add or change page
        let baseUrl;
        if (currentUrl.includes('/add/')) {
            // We're on add page: /admin/myapp/student/add/
            baseUrl = currentUrl.replace('/add/', '/getstaff/');
        } else {
            // We're on change page: /admin/myapp/student/123/change/
            baseUrl = currentUrl.split('/change/')[0].replace(/\/\d+$/, '') + '/getstaff/';
        }
        
        const url = `${baseUrl}?course_id=${courseId}`;
        console.log("➡️ Full URL for staff:", url);

        fetch(url, { 
            credentials: "same-origin",
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(async response => {
                console.log("📡 Response status:", response.status);
                console.log("📡 Response URL:", response.url);
                const text = await response.text();
                console.log("📥 Response preview:", text.substring(0, 200));

                // Detect if the response is HTML (login page) instead of JSON
                if (response.redirected || text.trim().startsWith("<!DOCTYPE") || text.trim().startsWith("<html")) {
                    console.error("⚠️ HTML response received instead of JSON.");
                    console.error("Full response:", text);
                    alert("Failed to load staff. The URL might be incorrect. Check console.");
                    throw new Error("Received HTML instead of JSON");
                }

                return JSON.parse(text);
            })
            .then(data => {
                console.log("✅ Staff fetched:", data);
                if (data.length === 0) {
                    console.warn("⚠️ No staff found for this course");
                }
                populateOptions(staffSelect, data);
            })
            .catch(err => {
                console.error("❌ Error fetching staff:", err);
            });
    });

    // --- When Staff changes → fetch batches ---
    staffSelect.addEventListener("change", function () {
        const staffId = this.value;
        console.log("👤 Staff changed:", staffId);

        clearOptions(batchSelect, "---------");
        if (!staffId) return;

        // Get the current page URL and construct the correct path
        const currentUrl = window.location.pathname;
        
        // Build URL based on whether we're on add or change page
        let baseUrl;
        if (currentUrl.includes('/add/')) {
            baseUrl = currentUrl.replace('/add/', '/getbatches/');
        } else {
            baseUrl = currentUrl.split('/change/')[0].replace(/\/\d+$/, '') + '/getbatches/';
        }
        
        const url = `${baseUrl}?staff_id=${staffId}`;
        console.log("➡️ Full URL for batches:", url);

        fetch(url, { 
            credentials: "same-origin",
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(async response => {
                console.log("📡 Response status:", response.status);
                console.log("📡 Response URL:", response.url);
                const text = await response.text();
                console.log("📥 Response preview:", text.substring(0, 200));

                if (response.redirected || text.trim().startsWith("<!DOCTYPE") || text.trim().startsWith("<html")) {
                    console.error("⚠️ HTML response received instead of JSON.");
                    console.error("Full response:", text);
                    alert("Failed to load batches. The URL might be incorrect. Check console.");
                    throw new Error("Received HTML instead of JSON");
                }

                return JSON.parse(text);
            })
            .then(data => {
                console.log("✅ Batches fetched:", data);
                if (data.length === 0) {
                    console.warn("⚠️ No batches found for this staff");
                }
                populateOptions(batchSelect, data);
            })
            .catch(err => {
                console.error("❌ Error fetching batches:", err);
            });
    });
});