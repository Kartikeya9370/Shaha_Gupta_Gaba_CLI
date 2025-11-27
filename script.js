// Use same-origin API (works with your Flask server at http://localhost:5000)
const API_BASE = '/api';

document.addEventListener('DOMContentLoaded', () => {
    // State
    let contacts = [];
    let editingContactName = null;

    // DOM elements
    const addContactForm = document.getElementById('addContactForm');
    const contactsList = document.getElementById('contactsList');
    const searchInput = document.getElementById('searchInput');
    const messageContainer = document.getElementById('messageContainer');
    const refreshBtn = document.getElementById('refreshBtn');
    const totalContactsEl = document.getElementById('totalContacts');
    const searchCountEl = document.getElementById('searchCount');
    const lastUpdatedEl = document.getElementById('lastUpdated');

    const editModal = document.getElementById('editModal');
    const editContactForm = document.getElementById('editContactForm');
    const editNameEl = document.getElementById('editName');
    const editPhoneEl = document.getElementById('editPhone');
    const editEmailEl = document.getElementById('editEmail');
    const closeEditModalBtn = document.getElementById('closeEditModal');

    // -------------------- utilities --------------------
    function showMessage(text, type = 'success') {
        // type: 'success' | 'error' | 'warning' | 'info'
        messageContainer.textContent = text;
        messageContainer.className = `status status--${type}`;
    }

    function fmtTime(d = new Date()) {
        const pad = n => String(n).padStart(2, '0');
        return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
    }

    function updateLastUpdated() {
        if (lastUpdatedEl) lastUpdatedEl.textContent = fmtTime();
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text == null ? '' : String(text);
        return div.innerHTML;
    }

    function filterContacts(query) {
        const q = (query || '').trim().toLowerCase();
        if (!q) return contacts;
        return contacts.filter(c =>
            (c.name || '').toLowerCase().includes(q) ||
            (c.phone || '').toLowerCase().includes(q) ||
            (c.email || '').toLowerCase().includes(q)
        );
    }

    function render(list) {
        contactsList.innerHTML = '';
        searchCountEl.textContent = String(list.length);

        if (!list.length) {
            const empty = document.createElement('div');
            empty.className = 'contacts-empty';
            empty.textContent = 'No contacts found.';
            contactsList.appendChild(empty);
            return;
        }

        list
            .slice()
            .sort((a, b) => a.name.localeCompare(b.name))
            .forEach(c => {
                const row = document.createElement('div');
                row.className = 'contact-item';

                const info = document.createElement('div');
                info.className = 'contact-info';
                info.innerHTML = `
                    <div class="contact-name">${escapeHtml(c.name)}</div>
                    <div class="contact-meta">
                        <span>📞 ${escapeHtml(c.phone)}</span>
                        <span>✉️ ${escapeHtml(c.email)}</span>
                    </div>
                `;

                const actions = document.createElement('div');
                actions.className = 'contact-actions';

                const editBtn = document.createElement('button');
                editBtn.className = 'btn';
                editBtn.textContent = 'Edit';
                editBtn.onclick = () => openEdit(c);

                const delBtn = document.createElement('button');
                delBtn.className = 'btn';
                delBtn.textContent = 'Delete';
                delBtn.onclick = () => delContact(c.name);

                actions.appendChild(editBtn);
                actions.appendChild(delBtn);

                row.appendChild(info);
                row.appendChild(actions);
                contactsList.appendChild(row);
            });
    }

    // -------------------- API calls --------------------
    async function loadContacts() {
        try {
            const res = await fetch(`${API_BASE}/contacts`);
            const data = await res.json();

            // Your Flask server returns { success, data:[...], count }
            if (Array.isArray(data.data)) {
                contacts = data.data;
            } else if (Array.isArray(data)) {
                // fallback if it's a plain array
                contacts = data;
            } else {
                throw new Error(data.error || 'Unexpected response format');
            }

            totalContactsEl.textContent = String(contacts.length);
            render(filterContacts(searchInput.value));
            updateLastUpdated();
            showMessage(`Loaded ${contacts.length} contacts`, 'success');
        } catch (err) {
            console.error('Error loading contacts:', err);
            showMessage('Error connecting to server', 'error');
        }
    }

    async function addContact(payload) {
        const res = await fetch(`${API_BASE}/contacts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        const data = await res.json();
        if (!res.ok || data.success === false) {
            throw new Error(data.error || 'Failed to add contact');
        }

        await loadContacts();
        showMessage('Contact added ✅', 'success');
    }

    async function updateContact(name, payload) {
        const res = await fetch(`${API_BASE}/contacts/${encodeURIComponent(name)}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        const data = await res.json();
        if (!res.ok || data.success === false) {
            throw new Error(data.error || 'Failed to update contact');
        }

        await loadContacts();
        showMessage('Contact updated ✅', 'success');
    }

    async function delContact(name) {
        if (!confirm(`Delete '${name}'?`)) return;

        const res = await fetch(`${API_BASE}/contacts/${encodeURIComponent(name)}`, {
            method: 'DELETE',
        });

        const data = await res.json();
        if (!res.ok || data.success === false) {
            showMessage(data.error || 'Failed to delete contact', 'error');
            return;
        }

        await loadContacts();
        showMessage('Contact deleted 🗑️', 'success');
    }

    // -------------------- edit modal -------------------
    function openEdit(c) {
        editingContactName = c.name;
        editNameEl.value = c.name;
        editPhoneEl.value = c.phone;
        editEmailEl.value = c.email;

        // CSS uses .modal.show for visibility
        editModal.classList.add('show');
    }

    function closeEditModal() {
        editingContactName = null;
        editModal.classList.remove('show');
    }

    // -------------------- event handlers ---------------
    function setupEventListeners() {
        // Add contact form
        addContactForm.addEventListener('submit', async (e) => {
            e.preventDefault();  // prevent page reload

            const name = document.getElementById('name').value.trim();
            const phone = document.getElementById('phone').value.trim();
            const email = document.getElementById('email').value.trim();

            if (!name || !phone || !email) {
                showMessage('⚠️ All fields are required', 'warning');
                return;
            }

            try {
                await addContact({ name, phone, email });
                addContactForm.reset();
            } catch (err) {
                showMessage(err.message || 'Add failed', 'error');
            }
        });

        // Search filter
        searchInput.addEventListener('input', () => {
            const list = filterContacts(searchInput.value);
            render(list);
        });

        // Refresh button
        refreshBtn.addEventListener('click', () => {
            loadContacts();
        });

        // Edit form submit
        editContactForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (!editingContactName) return;

            const payload = {
                name: editNameEl.value.trim(),
                phone: editPhoneEl.value.trim(),
                email: editEmailEl.value.trim(),
            };

            if (!payload.name || !payload.phone || !payload.email) {
                showMessage('⚠️ All fields are required', 'warning');
                return;
            }

            try {
                await updateContact(editingContactName, payload);
                closeEditModal();
            } catch (err) {
                showMessage(err.message || 'Update failed', 'error');
            }
        });

        // Close edit modal button
        closeEditModalBtn.addEventListener('click', () => {
            closeEditModal();
        });

        // Close modal if clicking outside the content
        editModal.addEventListener('click', (e) => {
            if (e.target === editModal) {
                closeEditModal();
            }
        });
    }

    // Initialize
    setupEventListeners();
    loadContacts();
    updateLastUpdated();
    setInterval(updateLastUpdated, 60000); // keep timestamp fresh
});
