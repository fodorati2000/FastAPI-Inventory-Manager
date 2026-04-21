loadProducts();

// --- TERMÉK KEZELÉS (Products) ---

async function addItem() {
    const name = document.getElementById("new_item_name").value;
    const brandId = document.getElementById("new_item_brand_id").value;
    const categoryId = document.getElementById("new_item_category_id").value;
    const locationId = document.getElementById("new_item_location_id").value;
    const pPrice = document.getElementById("new_item_purchase_price").value;
    const sPrice = document.getElementById("new_item_sale_price").value;
    const stock = document.getElementById("new_item_stock").value;
    const condition = document.getElementById("new_item_condition").value;
    const fileInput = document.getElementById("new_item_image");

    const formData = new FormData();
    formData.append("name", name);
    formData.append("brand_id", brandId);
    formData.append("category_id", categoryId);
    formData.append("location_id", locationId);
    formData.append("purchase_price", pPrice);
    formData.append("sale_price", sPrice);
    formData.append("stock_quantity", stock);
    formData.append("condition", condition);
    
    if (fileInput.files[0]) {
        formData.append("file", fileInput.files[0]);
    }

    const response = await fetch('http://127.0.0.1:8000/products/new', {
        method: 'POST',
        body: formData
    });

    if (response.ok) {
        Swal.fire("Success!", "Product saved successfully!", "success");
        loadProducts();
        document.getElementById("new_item_name").value = "";
        document.getElementById("new_item_purchase_price").value = "";
        document.getElementById("new_item_sale_price").value = "";
        document.getElementById("new_item_stock").value = "";
    } else {
        Swal.fire("Error!", "Could not save product.", "error");
    }
}

async function loadProducts() {
    const response = await fetch('http://127.0.0.1:8000/list');
    const data = await response.json();
    renderTable(data);
}

// Segédfüggvény a táblázat kirajzolásához (hogy ne kelljen duplikálni)
function renderTable(data, highlightStock = false) {
    const tableBody = document.querySelector('#product-table tbody');
    tableBody.innerHTML = ''; 

    data.forEach(item => { 
        const row = `
        <tr id="row-${item.id}">
            <td><img class="list-img" src="static/images/${item.image_path}" alt="product" style="width:50px; border-radius: 5px;"></td>
            <td class="product-name"><strong>${item.name}</strong></td>
            <td class="brand-cell">${item.brand_name}</td>
            <td class="category-cell">${item.category_name}</td>
            <td class="location-cell">${item.location_name || 'N/A'}</td>
            <td class="price-cell">${item.sale_price} Euro</td>
            <td class="stock-cell" style="${highlightStock ? 'color:red; font-weight:bold;' : ''}">${item.stock_quantity} db</td>
            <td class="condition-cell">${item.condition}</td>
            <td><button onclick="deleteProduct(${item.id})" class="danger-button">Delete</button></td>
            <td><button id="edit-btn-${item.id}" onclick="editInline(${item.id})" class="edit-button">Edit</button></td>
        </tr>`;
        tableBody.innerHTML += row;
    });
}

async function getLowStock() {
    const req = await fetch('http://127.0.0.1:8000/low-stock');
    const result = await req.json();
    renderTable(result, true);
}

async function editInline(id) {
    const row = document.getElementById(`row-${id}`);
    
    const nameCell = row.querySelector('.product-name');
    const brandCell = row.querySelector('.brand-cell');
    const categoryCell = row.querySelector('.category-cell');
    const locationCell = row.querySelector('.location-cell');
    const priceCell = row.querySelector('.price-cell');
    const stockCell = row.querySelector('.stock-cell');
    const editBtn = document.getElementById(`edit-btn-${id}`);

    // Adatok lekérése a selectekhez
    const [resB, resC, resL] = await Promise.all([
        fetch('http://127.0.0.1:8000/brands'),
        fetch('http://127.0.0.1:8000/categories'),
        fetch('http://127.0.0.1:8000/locations')
    ]);

    const brands = await resB.json();
    const categories = await resC.json();
    const locations = await resL.json();

    // Inputok behelyezése
    nameCell.innerHTML = `<input type="text" id="edit-name-${id}" value="${nameCell.innerText}">`;
    priceCell.innerHTML = `<input type="number" id="edit-price-${id}" value="${parseInt(priceCell.innerText)}">`;
    stockCell.innerHTML = `<input type="number" id="edit-stock-${id}" value="${parseInt(stockCell.innerText)}">`;

    // Selectek behelyezése (megkeresi a név alapján, melyik legyen alapból kiválasztva)
    brandCell.innerHTML = `<select id="edit-brand-${id}">${brands.map(b => `<option value="${b.id}" ${b.name === brandCell.innerText ? 'selected' : ''}>${b.name}</option>`).join('')}</select>`;
    categoryCell.innerHTML = `<select id="edit-category-${id}">${categories.map(c => `<option value="${c.id}" ${c.name === categoryCell.innerText ? 'selected' : ''}>${c.name}</option>`).join('')}</select>`;
    locationCell.innerHTML = `<select id="edit-location-${id}">${locations.map(l => `<option value="${l.id}" ${l.name === locationCell.innerText ? 'selected' : ''}>${l.name}</option>`).join('')}</select>`;

    editBtn.innerText = "Save";
    editBtn.onclick = () => saveInline(id);
    editBtn.style.backgroundColor = "#2ecc71"; // Zöld gomb a mentéshez
}

async function saveInline(id) {
    const formData = new FormData();
    formData.append("product_id", id);
    formData.append("name", document.getElementById(`edit-name-${id}`).value);
    formData.append("brand_id", document.getElementById(`edit-brand-${id}`).value);
    formData.append("category_id", document.getElementById(`edit-category-${id}`).value);
    formData.append("location_id", document.getElementById(`edit-location-${id}`).value);
    formData.append("sale_price", document.getElementById(`edit-price-${id}`).value);
    formData.append("stock_quantity", document.getElementById(`edit-stock-${id}`).value);
    formData.append("purchase_price", 0); 
    formData.append("condition", "Used");

    const response = await fetch('http://127.0.0.1:8000/edit', {
        method: 'PUT',
        body: formData
    });

    if (response.ok) {
        Swal.fire("Siker!", "Termék frissítve!", "success");
        loadProducts();
    } else {
        Swal.fire("Hiba!", "Nem sikerült a mentés.", "error");
    }
}

async function deleteProduct(productId) {
    const confirmResult = await Swal.fire({
        title: 'Are you sure?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, delete it!'
    });

    if (confirmResult.isConfirmed) {
        const response = await fetch(`http://127.0.0.1:8000/delete/${productId}`, { method: 'DELETE' });
        if (response.ok) {
            document.getElementById(`row-${productId}`).remove();
            Swal.fire('Deleted!', 'Success', 'success');
        }
    }
}

// --- SEGÉDTÁBLÁK KEZELÉSE ---

async function addBrand() {
    const nameInput = document.getElementById("new_brand_name");
    const formData = new FormData();
    formData.append("name", nameInput.value);
    const response = await fetch('http://127.0.0.1:8000/brands/new', { method: 'POST', body: formData });
    if (response.ok) { Swal.fire("Success!", "Brand added!", "success"); nameInput.value = ""; }
}

async function addCategory() {
    const nameInput = document.getElementById("new_category_name");
    const formData = new FormData();
    formData.append("name", nameInput.value);
    const response = await fetch('http://127.0.0.1:8000/categories/new', { method: 'POST', body: formData });
    if (response.ok) { Swal.fire("Success!", "Category added!", "success"); nameInput.value = ""; }
}

async function addLocation() {
    const nameInput = document.getElementById("new_location_name");
    const formData = new FormData();
    formData.append("name", nameInput.value);
    const response = await fetch('http://127.0.0.1:8000/locations/new', { method: 'POST', body: formData });
    if (response.ok) { 
        Swal.fire("Success!", "Location added!", "success"); 
        nameInput.value = ""; 
        await loadDropdownData(); 
    }
}

// --- UI LOGIKA ---

function searchByName() {
    const query = document.getElementById("search_input").value.toLowerCase();
    const rows = document.querySelectorAll('#product-table tbody tr');
    rows.forEach(row => {
        const text = row.innerText.toLowerCase();
        row.style.display = text.includes(query) ? "" : "none";
    });
}

async function toggleView(containerId) {
    const containers = ["brand_container", "category_container", "location_container", "product_container", "list_container"];
    containers.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = (id === containerId) ? "block" : "none";
    });

    if (containerId === "low_stock") {
        document.getElementById("list_container").style.display = "block";
        getLowStock();
    }
    if (containerId === "product_container") {
        await loadDropdownData();
    }
    if (containerId === "list_container") {
        loadProducts();
    }
}

async function loadDropdownData() {
    try {
        const [resB, resC, resL] = await Promise.all([
            fetch('http://127.0.0.1:8000/brands'),
            fetch('http://127.0.0.1:8000/categories'),
            fetch('http://127.0.0.1:8000/locations')
        ]);

        const brands = await resB.json();
        const categories = await resC.json();
        const locations = await resL.json();

        const populate = (id, data) => {
            const select = document.getElementById(id);
            if (select) select.innerHTML = data.map(i => `<option value="${i.id}">${i.name}</option>`).join('');
        };

        populate("new_item_brand_id", brands);
        populate("new_item_category_id", categories);
        populate("new_item_location_id", locations);
    } catch (e) { console.error(e); }
}