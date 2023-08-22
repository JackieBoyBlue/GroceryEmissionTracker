// Add and remove input fields for items and prices.
let inputs = document.getElementById('extra-inputs');

const receiptForm = document.getElementById("receipt-form")

receiptForm.addEventListener("click", (event) => {
    if(event.target.id === 'add-item-input') {
        let inputs = document.getElementById('extra-inputs');
        
        function add(){
            var numInputs = document.getElementsByClassName('input-group').length;
            
            var input = document.createElement('div');
            input.setAttribute('class', 'input-group my-3');
            input.innerHTML = `
            <input class="form-control" id="i${numInputs}" name="i${numInputs}" placeholder="Item" required="True" type="text">
            <span for="w${numInputs}" class="input-group-text">kg/L</span>
            <input class="form-control" id="w${numInputs}" min="0" name="w${numInputs}" placeholder="0.0" style="max-width: 100px;" type="number" value="", step="0.001">
            <span for="p${numInputs}" class="input-group-text">£</span>
            <input class="form-control" id="p${numInputs}" min="0" name="p${numInputs}" placeholder="0.00" required="True" step="0.01" style="max-width: 100px;" type="number">`;
            inputs.appendChild(input);
        };
        add();
    }
});

receiptForm.addEventListener("click", (event) => {
    if(event.target.id === 'remove-item-input') {
        let inputs = document.getElementById('extra-inputs');
        
        function remove(){
            inputs.removeChild(inputs.lastChild);
        };
        remove();
        tallyTotal();
    }
});

// Update the total amount when the user inputs a price.

receiptForm.addEventListener("input", (event) => {
    if (event.target.type == 'number' && event.target.id[0] == 'p' && event.target.value != '') {
        tallyTotal();
    }
});

receiptForm.addEventListener("htmx:afterSettle", (event) => {
    tallyTotal();
});

function tallyTotal() {
    let sum = document.getElementById('total-amount');
    let form = document.getElementById('items-form');
    let total = 0;
    
    console.log(form);
    for (let i = 0; i < form.length; i++) {
        if (form[i].type == 'number' && form[i].id[0] == 'p') {
            if (form[i].value == '') {
                form[i].value = 0;
            }
            total += parseFloat(form[i].value);
            if (form[i].value == 0) {
                form[i].value = '';
            }
        }
    }
    if (isNaN(total)) {
        total = 0;
    }
    sum.innerHTML = `£${total.toFixed(2)}`;
}