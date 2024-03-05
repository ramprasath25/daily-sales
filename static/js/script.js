var initialDate;
var initialQuantities = [];
var url = 'http://localhost:5000';
var editMode = false;
var today; // Define today globally

function toggleEdit() {
  editMode = !editMode;
  var productButtons = document.querySelectorAll('.productBtn');
  productButtons.forEach(function (button) {
    button.classList.toggle('hide');
  });

  document.getElementById('editBtn').classList.toggle('hide');
  document.getElementById('saveBtn').classList.toggle('hide');

  var dateInput = document.getElementById('date');
  dateInput.disabled = !dateInput.disabled;
  var onlineInput = document.getElementById('online')
  onlineInput.disabled = !onlineInput.disabled;
  // Show counter buttons if in edit mode
  if (!dateInput.disabled) {
    var counters = document.querySelectorAll('.counter');
    counters.forEach(function (counter) {
      counter.style.display = 'flex';
    });
  }
}

function saveChanges() {
  var dateInput = document.getElementById('date');
  var date = dateInput.value;
  var counters = document.querySelectorAll('.counter input');
  var onlineInput = document.getElementById('online')
  online = onlineInput.value
  var productsData = [];
  counters.forEach(function (counter, index) {
    var productId = counter.dataset.productId;
    var quantity = counter.value - initialQuantities[index];
    if (quantity !== 0) {
      productsData.push({ product_id: productId, quantity_sold: counter.value });
    }
  });

  fetch(url + '/record-sale', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      sale_date: date,
      online_sales: online,
      products: productsData
    })
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to save changes.');
      }
      toggleEdit(); // Toggle back to view mode
      initialDate = date;
      initialQuantities = [];
      counters.forEach(function (counter) {
        initialQuantities.push(counter.value);
      });
      location.reload();
    })
    .catch(error => {
      alert("Error saving data")
      console.error('Error saving changes:', error);
    });
}

function fetchProductsByDate(date) {
  var productList = document.getElementById('productList');
  productList.innerHTML = ''; // Clear previous product list
  var totalCount = 0;
  fetch(url + '/products?date=' + date)
    .then(response => response.json())
    .then(products => {
      var onlineInput = document.getElementById('online')
      onlineInput.value = products["online_sales"]
      products["product_data"].forEach(product => {
        //  Total count
        totalCount += product.total_quantity_sold
        var productDiv = document.createElement('div');
        buttonClass = editMode ? "productBtn" : "productBtn hide";
        productDiv.className = 'product';
        productDiv.innerHTML = `
          <div class="seventy-percent"><span>${product.name} </span></div>
          <div class="counter thirty-percent">
              <input type="number" value="${product.total_quantity_sold}" readonly style="width: 50px;" data-product-id="${product.id}" />
              <button class="${buttonClass}" onclick="decrement(this)">-</button>
              <button class="${buttonClass}" onclick="increment(this)">+</button>
          </div>
        `;
        productList.appendChild(productDiv);
      });
      sale_total_sold.innerHTML = `<div class="seventy-percent"><span>Total Items sold: </span></div>
                                    <div class="thirty-percent"><span>${totalCount}</span></div>`
      // Show counter buttons if in edit mode
      if (!document.getElementById('date').disabled) {
        var counters = document.querySelectorAll('.counter');
        counters.forEach(function (counter) {
          counter.style.display = 'flex';
        });
      }
    })
    .catch(error => {
      console.error('Error fetching products:', error);
    });
}

document.addEventListener('DOMContentLoaded', function () {
  var dateInput = document.getElementById('date');
  today = new Date(); // Set today's date
  var dd = String(today.getDate()).padStart(2, '0');
  var mm = String(today.getMonth() + 1).padStart(2, '0'); // January is 0!
  var yyyy = today.getFullYear();
  today = yyyy + '-' + mm + '-' + dd;
  dateInput.value = today;
  initialDate = today;

  fetchProductsByDate(today);

  var counters = document.querySelectorAll('.counter input');
  counters.forEach(function (counter) {
    initialQuantities.push(counter.value);
  });
  
  dateInput.addEventListener('change', function () {
    var selectedDate = dateInput.value;
    fetchProductsByDate(selectedDate); // Fetch products for the selected date
    var productButtons = document.querySelectorAll('.productBtn');
    // Reset all counters to zero
    counters.forEach(function (counter) {
      counter.value = 0;
    });
  });
});

function increment(button) {
  var input = button.parentElement.querySelector('input');
  input.value = parseInt(input.value) + 1;
}

function decrement(button) {
  var input = button.parentElement.querySelector('input');
  input.value = parseInt(input.value) - 1 >= 0 ? parseInt(input.value) - 1 : 0;
}
